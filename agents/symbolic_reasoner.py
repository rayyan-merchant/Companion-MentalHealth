from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD


KRR = Namespace("http://www.semanticweb.org/hunaizanaveed/ontologies/2025/11/krr_project#")

ONTOLOGY_PATH = PROJECT_ROOT / "ontology" / "mental_health.owl"
BASE_GRAPH_PATH = PROJECT_ROOT / "ontology" / "base_graph.ttl"
SPARQL_DIR = PROJECT_ROOT / "reasoning" / "sparql"


@dataclass
class ReasoningResult:
    inferred_states: List[str] = field(default_factory=list)
    primary_state: Optional[str] = None
    evidence_used: Dict[str, List[str]] = field(default_factory=dict)
    rules_fired: List[str] = field(default_factory=list)
    confidence: str = "low"
    needs_clarification: bool = False
    clarification_reason: Optional[str] = None


CONCEPT_TO_URI = {
    # Emotions
    "stress": KRR.Stress,
    "anxiety": KRR.Anxiety,
    "panic": KRR.Panic,
    "sadness": KRR.Sadness,
    "depression": KRR.DepressiveSpectrum,
    "irritability": KRR.Irritability,
    "overwhelm": KRR.Emotional_Overwhelm,
    
    # Symptoms
    "insomnia": KRR.Insomnia,
    "fatigue": KRR.Fatigue,
    "restlessness": KRR.Restlessness,
    "heart_symptoms": KRR.Rapid_Heart_Rate,
    "breathing": KRR.Breathing_Difficulty,
    "appetite": KRR.Appetite_Change,
    "withdrawal": KRR.Social_Withdrawal,
    "anhedonia": KRR.Loss_Of_Interest,
    "concentration": KRR.Difficulty_Concentrating,
    
    # Triggers
    "academic": KRR.ExamPressure,
    "financial": KRR.Financial_Concern,
    "family": KRR.Family_Pressure,
    "social": KRR.SocialPressure,
    "work": KRR.AcademicWorkload  # Mapped to existing concept
}

STATE_PRIORITY = {
    "PanicRisk": 5,
    "DepressiveSpectrum": 4,
    "AnxietyRisk": 3,
    "AcademicStress": 2,
    "SleepDisturbance": 1,
    "NeedsMoreContext": 0
}


class SymbolicReasoningAgent:

    def __init__(self):
        self.ontology_graph = Graph()
        self.base_graph = Graph()
        self.active_rules = self._get_active_rules()
        
        # Load ontology if available
        if ONTOLOGY_PATH.exists():
            self.ontology_graph.parse(str(ONTOLOGY_PATH))
        if BASE_GRAPH_PATH.exists():
            self.base_graph.parse(str(BASE_GRAPH_PATH), format="turtle")
    
    def _get_active_rules(self) -> List[str]:
        return [
            "rule_R_DEP_explicit.sparql",
            "rule_R_ACS_02.sparql",
            "rule_R_ANX_physio.sparql",
            "rule_R_ANX_life.sparql",
            "rule_R_DEP_complex.sparql",
            "rule_R_PAN_acute.sparql",
            "rule_R_SLEEP_01.sparql",
            "rule_R_ISO_01.sparql",
            "rule_R_LOW_CONTEXT.sparql"
        ]
    
    def reason(
        self,
        emotions: List[str],
        symptoms: List[str],
        triggers: List[str],
        session_id: str = "anonymous",
        persistence: bool = False
    ) -> ReasoningResult:

        result = ReasoningResult()
        result.evidence_used = {
            "emotions": emotions,
            "symptoms": symptoms,
            "triggers": triggers
        }
        
        inferred_states = []
        rules_fired = []
        
        # Normalize to sets for easier matching
        emotions_set = set(emotions)
        symptoms_set = set(symptoms)
        triggers_set = set(triggers)
        
        if "panic" in emotions_set:
            if symptoms_set & {"heart_symptoms", "breathing"}:
                inferred_states.append("PanicRisk")
                rules_fired.append("R_PAN_acute")
        
        if emotions_set & {"depression", "sadness"}:
            if symptoms_set & {"withdrawal", "anhedonia", "fatigue"}:
                inferred_states.append("DepressiveSpectrum")
                rules_fired.append("R_DEP_complex")
        
        # Explicit depression mention
        if "depression" in emotions_set:
            if "DepressiveSpectrum" not in inferred_states:
                inferred_states.append("DepressiveSpectrum")
                rules_fired.append("R_DEP_explicit")
        
        if "anxiety" in emotions_set:
            if symptoms_set & {"insomnia", "restlessness"}:
                inferred_states.append("AnxietyRisk")
                rules_fired.append("R_ANX_physio")
            elif triggers_set & {"financial", "family", "social", "work"}:
                inferred_states.append("AnxietyRisk")
                rules_fired.append("R_ANX_life")
        
        if emotions_set & {"stress", "anxiety", "panic"}:
            if triggers_set & {"academic", "work"}:
                inferred_states.append("AcademicStress")
                rules_fired.append("R_ACS_02")
        
        if "insomnia" in symptoms_set:
            if "AnxietyRisk" not in inferred_states:
                inferred_states.append("SleepDisturbance")
                rules_fired.append("R_SLEEP_01")
        
        if "withdrawal" in symptoms_set:
            if "DepressiveSpectrum" not in inferred_states:
                inferred_states.append("SocialIsolation")
                rules_fired.append("R_ISO_01")
        
        total_evidence = len(emotions) + len(symptoms) + len(triggers)
        
        if not inferred_states:
            if total_evidence == 0:
                result.needs_clarification = True
                result.clarification_reason = "no_evidence"
                result.primary_state = None
            else:
                inferred_states.append("NeedsMoreContext")
                rules_fired.append("R_LOW_CONTEXT")
                result.needs_clarification = True
                result.clarification_reason = "insufficient_evidence"
        
        result.inferred_states = inferred_states
        result.rules_fired = rules_fired
        result.primary_state = self._get_primary_state(inferred_states) if inferred_states else None
        
        # Determine confidence
        evidence_categories = sum([
            1 if emotions else 0,
            1 if symptoms else 0,
            1 if triggers else 0
        ])
        
        if evidence_categories >= 2 and len(inferred_states) >= 1:
            result.confidence = "high"
        elif evidence_categories >= 1 and inferred_states and inferred_states[0] != "NeedsMoreContext":
            result.confidence = "medium"
        else:
            result.confidence = "low"
        
        return result
    
    def _build_session_graph(
        self,
        session_id: str,
        emotions: List[str],
        symptoms: List[str],
        triggers: List[str],
        persistence: bool
    ) -> Graph:
        g = Graph()
        g.bind("krr", KRR)
        
        session_uri = KRR[f"session_{session_id}"]
        student_uri = KRR[f"student_{session_id}"]
        
        # Add session and student
        g.add((session_uri, RDF.type, KRR.Session))
        g.add((student_uri, RDF.type, KRR.Student))
        g.add((session_uri, KRR.hasSessionStudent, student_uri))
        
        # Add evidence
        evidence_counter = 0
        
        for emotion in emotions:
            if emotion in CONCEPT_TO_URI:
                ev_uri = KRR[f"evidence_{evidence_counter}"]
                g.add((ev_uri, RDF.type, CONCEPT_TO_URI[emotion]))
                g.add((session_uri, KRR.hasEvidence, ev_uri))
                evidence_counter += 1
        
        for symptom in symptoms:
            if symptom in CONCEPT_TO_URI:
                ev_uri = KRR[f"evidence_{evidence_counter}"]
                g.add((ev_uri, RDF.type, CONCEPT_TO_URI[symptom]))
                g.add((session_uri, KRR.hasEvidence, ev_uri))
                evidence_counter += 1
        
        for trigger in triggers:
            if trigger in CONCEPT_TO_URI:
                ev_uri = KRR[f"evidence_{evidence_counter}"]
                g.add((ev_uri, RDF.type, CONCEPT_TO_URI[trigger]))
                g.add((session_uri, KRR.hasEvidence, ev_uri))
                evidence_counter += 1
        
        # Add persistence if detected
        if persistence:
            rf_uri = KRR["rf_persistence"]
            g.add((rf_uri, RDF.type, KRR.RepeatedStressExposure))
            g.add((student_uri, KRR.hasRiskFactor, rf_uri))
        
        return g
    
    def _apply_rules(self, session_graph: Graph, session_id: str) -> List[str]:
        student_uri = KRR[f"student_{session_id}"]
        
        # Apply each rule
        for rule_file in self.active_rules:
            rule_path = SPARQL_DIR / rule_file
            if rule_path.exists():
                try:
                    with open(rule_path, "r", encoding="utf-8") as f:
                        query = f.read()
                        session_graph.update(query)
                except Exception as e:
                    print(f"Rule {rule_file} failed: {e}")
        
        inferred = []
        query = """
            SELECT ?type WHERE {
                ?s rdf:type ?type .
                FILTER(STRSTARTS(STR(?type), STR(krr:)))
                FILTER(?type != krr:Student)
            }
        """
        
        try:
            results = session_graph.query(
                query,
                initBindings={'s': student_uri},
                initNs={"krr": KRR, "rdf": RDF}
            )
            for row in results:
                state_name = str(row.type).split("#")[-1]
                if state_name not in ["Session", "Student"] and state_name not in inferred:
                    inferred.append(state_name)
        except Exception as e:
            print(f"State extraction failed: {e}")
        
        return inferred
    
    def _get_primary_state(self, states: List[str]) -> str:
        """Get the highest priority state."""
        if not states:
            return "NeedsMoreContext"
        
        return max(states, key=lambda s: STATE_PRIORITY.get(s, 1))


_reasoner_instance: Optional[SymbolicReasoningAgent] = None


def get_reasoner() -> SymbolicReasoningAgent:
    global _reasoner_instance
    if _reasoner_instance is None:
        _reasoner_instance = SymbolicReasoningAgent()
    return _reasoner_instance


def reason_from_signals(
    emotions: List[str],
    symptoms: List[str],
    triggers: List[str],
    session_id: str = "anonymous",
    persistence: bool = False
) -> Dict[str, Any]:

    reasoner = get_reasoner()
    result = reasoner.reason(emotions, symptoms, triggers, session_id, persistence)
    
    return {
        "inferred_states": result.inferred_states,
        "primary_state": result.primary_state,
        "evidence_used": result.evidence_used,
        "rules_fired": result.rules_fired,
        "confidence": result.confidence,
        "needs_clarification": result.needs_clarification,
        "clarification_reason": result.clarification_reason
    }


if __name__ == "__main__":
    print("Symbolic Reasoning Agent Test")
    print("=" * 60)
    
    test_cases = [
        (["anxiety"], ["insomnia"], [], "Anxiety + Insomnia"),
        (["stress"], [], ["academic"], "Stress + Academic Trigger"),
        (["sadness"], ["withdrawal"], [], "Sadness + Withdrawal"),
        (["panic"], ["heart_symptoms", "breathing"], [], "Panic + Heart + Breathing"),
        ([], [], [], "No evidence")
    ]
    
    for emotions, symptoms, triggers, description in test_cases:
        result = reason_from_signals(emotions, symptoms, triggers)
        print(f"\n{description}")
        print(f"  Emotions: {emotions}, Symptoms: {symptoms}, Triggers: {triggers}")
        print(f"  → Primary State: {result['primary_state']}")
        print(f"  → Confidence: {result['confidence']}")
        print(f"  → Needs Clarification: {result['needs_clarification']}")
