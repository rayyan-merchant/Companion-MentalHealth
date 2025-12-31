"""
End-to-End Pipeline Orchestration Layer
Mental Health KRR System

Responsible for connecting all frozen components into a deterministic
symbolic pipeline. This module ensures correct execution order and data flow,
and acts as the single entry point for the system.

CONSTRAINTS:
- No new reasoning logic in the pipeline flow itself (reasoning is delegated).
- Logic for inference is EXECUTED via external SPARQL rules to strictly mimic SWRL behavior.
- Strict adherence to symbolic-only values (no numbers).
- Full audit logging mandated.
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from pathlib import Path
import logging

# Project Imports
from graph.graph_manager import GraphManager
from nlp.extractor import extract_concepts
from nlp.concept_mapper import map_to_ontology
from nlp.confidence_estimator import build_evidence 

# Reasoning Modules (Frozen logic)
from reasoning.explainer import generate_explanation
from reasoning.ranker import rank_risk_states
from reasoning.escalation import evaluate_escalation
from reasoning.audit_logger import log_audit_session

# RDFLib for Reasoning Simulation
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD

# =============================================================================
# CONSTANTS & CONFIG
# =============================================================================

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ONTOLOGY_PATH = str(BASE_DIR / "ontology" / "mental_health.owl")
BASE_GRAPH_PATH = str(BASE_DIR / "ontology" / "base_graph.ttl")
SESSION_GRAPH_DIR = BASE_DIR / "data" / "session_graphs"
SPARQL_DIR = BASE_DIR / "reasoning" / "sparql"

# Namespaces (Unified to Ontology)
KRR = Namespace("http://www.semanticweb.org/hunaizanaveed/ontologies/2025/11/krr_project#")

# =============================================================================
# HELPERS
# =============================================================================

def _expand_curie(curie: str) -> URIRef:
    """Expand CURIE string (e.g. 'mh:Stress') to full URIRef using KRR namespace."""
    # Mapping old prefixes to the unified KRR namespace if needed
    # But effectively we want everything in KRR namespace now
    name = curie.split(":")[1]
    return KRR[name]

# =============================================================================
# EXTERNAL RULE EXECUTION
# =============================================================================

def _execute_external_reasoning_rules(graph_manager: GraphManager) -> None:
    """
    Execute external SPARQL INSERT rules to perform symbolic inference.
    Rules are loaded from `reasoning/sparql/` directory.
    """
    sparql_path = Path(SPARQL_DIR)
    # List of active rules to run (order matters for dependencies)
    # We only run rules that do NOT depend on unsupported features (like persistence)
    # unless those features are supported. Currently persistence is NOT supported.
    active_rules = [
        "rule_R_ACS_01a.sparql",
        "rule_R_ACS_01b.sparql",
        "rule_R_ANX_01.sparql",
        "rule_R_PAN_01.sparql",
        "rule_R_DEP_01.sparql"
    ]
    
    # Run rules (simple fixpoint iteration for dependencies)
    for _ in range(2):
        for rule_file in active_rules:
            rule_path = sparql_path / rule_file
            if rule_path.exists():
                with open(rule_path, "r", encoding="utf-8") as f:
                    query = f.read()
                    # Execute on session graph
                    graph_manager.session_graph.update(query)

# =============================================================================
# SPARQL QUERY EXECUTION
# =============================================================================

NAMESPACES = {
    "krr": KRR,
    "rdf": RDF,
    "rdfs": RDFS
}

def _extract_sparql_data_for_explainer(graph_manager: GraphManager, student_uri: URIRef) -> Dict[str, Any]:
    """
    Manually extract data needed for explainer to ensure robust output.
    """
    g = graph_manager.session_graph
    
    # 1. Get Mental States
    states = []
    # Query for all direct classes that share namespace with KRR
    query_states = """
        SELECT ?type WHERE {
            ?s rdf:type ?type .
            FILTER(STRSTARTS(STR(?type), STR(krr:)))
            FILTER(?type != krr:Student)
        }
    """
    qres = g.query(query_states, initBindings={'s': student_uri}, initNs=NAMESPACES)
    for row in qres:
        states.append(str(row.type).split("#")[-1])

    # 2. Get Evidence (Emotions, Symptoms, Triggers)
    evidence = {"emotions": [], "symptoms": [], "triggers": [], "risk_factors": []}
    
    # Use unified KRR namespace for all queries
    
    # Emotions
    q_em = """SELECT ?e_type WHERE { ?sess krr:hasEvidence ?e . ?e rdf:type ?e_type . ?e_type rdfs:subClassOf* krr:Emotion . }"""
    # Note: subClassOf* requires reasoning or explicit hierarchy. Since we don't have a reasoner,
    # we rely on the type being explicitly added or simple convention.
    # FALLBACK: Just query types of evidence and categorize by concept_type map if possible, 
    # but here we must query the graph.
    # SIMPLIFICATION: Query explicit types attached to evidence nodes
    
    # Actually, let's just query everything attached via hasEvidence and filter by suffix/naming convention 
    # if strict typing isn't available. But we injected types.
    
    # Let's try simple queries assuming types are present.
    q_all_evidence = """
        SELECT ?etype WHERE {
            ?sess krr:hasEvidence ?e .
            ?e rdf:type ?etype .
        }
    """
    for row in g.query(q_all_evidence, initNs=NAMESPACES):
        name = str(row.etype).split("#")[-1]
        # Basic categorization based on name (Symbolic heuristic strictly for display bucketing)
        if name in ["Stress", "Anxiety", "Sadness", "Emotional_Overwhelm"]:
            evidence["emotions"].append(name)
        elif name in ["Insomnia", "Fatigue", "RapidHeartRate", "BreathingDifficulty"]:
            evidence["symptoms"].append(name)
        elif name in ["ExamPressure", "AcademicWorkload"]:
            evidence["triggers"].append(name)
    
    # Risk Factors
    q_rf = """SELECT ?rf_type WHERE { ?s krr:hasRiskFactor ?rf . ?rf rdf:type ?rf_type . }"""
    for row in g.query(q_rf, initBindings={'s': student_uri}, initNs=NAMESPACES): 
        evidence["risk_factors"].append(str(row.rf_type).split("#")[-1])

    # 3. Persistence Flag
    has_persistence = "RepeatedStressExposure" in evidence["risk_factors"]

    return {
        "mentalState": states[0] if states else None, 
        "riskState": states[0] if states else "Unknown",
        "emotions": evidence["emotions"],
        "symptoms": evidence["symptoms"],
        "triggers": evidence["triggers"],
        "risk_factors": evidence["risk_factors"],
        "has_persistence": has_persistence,
        "bindings": [] 
    }

def _extract_sparql_escalation_flags(graph_manager: GraphManager, student_uri: URIRef) -> Dict[str, bool]:
    """Check escalation conditions directly."""
    g = graph_manager.session_graph
    
    # Helpers
    def check_type(typename):
        return (student_uri, RDF.type, KRR[typename]) in g
        
    def check_rf(typename):
        # exists s -> hasRiskFactor -> type
        # Use initNs to ensure prefixes are recognized
        return bool(list(g.query(
            f"ASK {{ ?s krr:hasRiskFactor ?rf . ?rf rdf:type krr:{typename} }}", 
            initBindings={'s': student_uri},
            initNs=NAMESPACES
        )))

    return {
        "high_risk": check_type("HighRisk"),
        "panic_with_persistence": check_type("PanicRisk") and check_rf("RepeatedStressExposure"),
        "depressive_spectrum": check_type("DepressiveSpectrum"),
        "moderate_risk": check_type("ModerateRisk"),
        "multiple_states": False
    }

# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_krr_pipeline(
    session_id: str,
    student_uri_str: str,
    raw_text: str
) -> dict:
    
    # --- 1. Session Initialization ---
    if "http" not in student_uri_str:
        student_uri = KRR[student_uri_str]
    else:
        student_uri = URIRef(student_uri_str)

    # Initialize Graph Manager
    gm = GraphManager(ONTOLOGY_PATH, BASE_GRAPH_PATH)
    
    # Load or create session
    session_file = SESSION_GRAPH_DIR / f"{session_id}.ttl"
    SESSION_GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    
    if session_file.exists():
        session_uri = gm.load_existing_session(str(session_file))
    else:
        session_uri = gm.create_session(student_uri, session_id=session_id)
    
    # --- 2. NLP Extraction ---
    extracted_items = extract_concepts(raw_text)
    
    # --- 3. Concept Mapping ---
    mapped_concepts = map_to_ontology(extracted_items)
    
    # --- 4. Evidence Construction ---
    evidence_objects = build_evidence(mapped_concepts, session_id=session_id)
    
    # --- 5. Session Graph Update ---
    for ev in evidence_objects:
        ev_uri = KRR[ev['evidence_id']]
        
        # Expand type URI (Unified KRR Namespace)
        type_uri = _expand_curie(ev['concept_uri'])
        gm.add_evidence_type(ev_uri, type_uri)
        gm.add_evidence(ev_uri)
        
        # Strict Symbolic Confidence
        sym_conf = ev.get("confidence_label", "UNKNOWN")
        if sym_conf != "UNKNOWN":
            gm.add_confidence_label(ev_uri, sym_conf)
            
        # Persistence Logic:
        # We REMOVED all heuristics. We only add persistence if explicit info exists.
        # Currently NLP does not provide it, so we add nothing.
        # This respects "No illegal risk factor dependence".

    # --- 7. Symbolic Reasoning (External Execution) ---
    _execute_external_reasoning_rules(gm)
    
    # --- 8. Data Extraction ---
    sparql_results = _extract_sparql_data_for_explainer(gm, student_uri)
    escalation_flags = _extract_sparql_escalation_flags(gm, student_uri)
    
    # --- 9. Explanation Generation ---
    inferred_state = sparql_results["riskState"]
    
    # Strict Provenance: We do not guess which rule fired.
    rules_fired_safe = ["UNKNOWN_RULE_SOURCE"] 
    
    if inferred_state == "Unknown":
        explanation = {
            "explanation_text": "No specific risk factors detected based on current inputs.",
            "confidence": "LOW",
            "safety_flag": "SAFE"
        }
    else:
        explanation = generate_explanation(
            student_id=str(student_uri),
            sparql_results=sparql_results,
            escalation_flags=escalation_flags,
            rules_fired=rules_fired_safe,
            has_persistence=sparql_results["has_persistence"]
        )
    
    # --- 10. Risk Ranking ---
    if isinstance(explanation, dict): 
        ranking_output = rank_risk_states(
            student_id=str(student_uri),
            explanations=[explanation]
        )
    
    # --- 11. Escalation Decision ---
    escalation_output = evaluate_escalation(
        student_id=str(student_uri),
        ranking_result=ranking_output,
        escalation_findings=escalation_flags
    )
    
    # --- 12. Audit Logging ---
    audit_record = log_audit_session(
        session_id=session_id,
        student_id=str(student_uri),
        explanation_outputs=[explanation],
        ranking_result=ranking_output,
        escalation_result=escalation_output
    )
    
    # --- 13. Session Export (Persistence) ---
    gm.export_session(str(session_file))
    
    # --- 14. Final Output Assembly ---
    response = {
        "session_id": session_id,
        "summary": ranking_output["summary_rationale"],
        "explanations": [explanation["explanation_text"]],
        "ranked_concerns": [state["risk_state"] for state in ranking_output["ranked_states"]],
        "escalation_guidance": escalation_output["support_recommendation"],
        "disclaimer": escalation_output["disclaimer"],
        "audit_ref": audit_record["record_hash"]
    }
    
    return response

if __name__ == "__main__":
    test_id = f"session_{uuid.uuid4()}"
    print(f"Running pipeline for {test_id}...")
    text = "I am so stressed about my exams next week. I haven't slept in days causing insomnia."
    student = "student_001"
    result = run_krr_pipeline(test_id, student, text)
    print("\n--- PIPELINE RESULT ---")
    print(result)
