"""
Session Graph Manager — Phase 4: Graph Orchestration Layer
===========================================================

PURPOSE:
    This module manages immutable session graphs for the Mental Health KRR system.
    It creates, populates, and exports symbolic session data that records:
    - Which student is associated with a session
    - What evidence (emotions, symptoms, behaviors) was observed
    - What mental states were derived by the reasoning engine

SYMBOLIC CONSTRAINTS (MANDATORY):
    - NO numeric values (scores, durations, probabilities)
    - NO ML/statistical inference
    - NO diagnosis or medical claims
    - ALL predicates use symbolic labels only (e.g., "HIGH", "PERSISTENT")
    - Session graphs are ADDITIVE ONLY — never modify existing triples

NAMESPACE:
    Uses http://example.org/mental-health# (mh: prefix) to match base_graph.ttl

DOWNSTREAM CONSUMERS:
    Session graphs produced here are consumed by:
    1. SPARQL Query Engine (Phase 4) — pattern matching
    2. Explanation Engine (Phase 5) — rule-based explanations
    3. Risk Ranker (Phase 5) — symbolic risk classification
    4. Escalation Engine (Phase 6) — intervention triggers
    5. Audit Logger (Phase 7) — provenance and traceability

DETERMINISM:
    - Session IDs can be passed explicitly for reproducibility
    - If not provided, a UUID is generated
    - The SAME session ID is used in both URI and sessionId literal

AUTHOR: KRR Project Team
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD
from uuid import uuid4
from datetime import datetime
from typing import Optional


class GraphManager:
    """
    Session Graph Manager for Mental Health KRR System.
    
    Responsible ONLY for graph orchestration and session lifecycle.
    Does NOT perform reasoning, inference, or ranking.
    
    Usage:
        gm = GraphManager(ontology_path, base_graph_path)
        gm.create_session(student_uri)
        gm.add_evidence(evidence_uri)
        gm.add_confidence_label(evidence_uri, "HIGH")
        gm.add_derived_state(mental_state_uri)
        gm.export_session(output_path)
    """

    # Namespace matching ontology (Unified Namespace)
    MH = Namespace("http://www.semanticweb.org/hunaizanaveed/ontologies/2025/11/krr_project#")

    def __init__(self, ontology_path: str, base_graph_path: str):
        """
        Initialize the Graph Manager with ontology and base knowledge.
        
        Args:
            ontology_path: Path to the OWL ontology file
            base_graph_path: Path to the base knowledge graph (TTL)
        """
        self.ontology_graph = Graph()
        self.base_graph = Graph()
        self.session_graph: Optional[Graph] = None
        self.session_uri: Optional[URIRef] = None
        self._session_id: Optional[str] = None

        # Load ontology and base graph (read-only reference)
        self.ontology_graph.parse(ontology_path)
        self.base_graph.parse(base_graph_path, format="turtle")

    def create_session(self, student_uri: URIRef, session_id: Optional[str] = None) -> URIRef:
        """
        Create a new immutable session graph.
        
        Args:
            student_uri: URI of the student (e.g., mh:student_001)
            session_id: Optional deterministic session ID for reproducibility.
                        If not provided, a UUID-based ID is generated.
        
        Returns:
            URIRef: The session URI
        
        Note:
            The SAME session_id is used for both the URI and the sessionId literal
            to ensure audit traceability and Phase-7 integrity.
        """
        self.session_graph = Graph()
        self.session_graph.bind("mh", self.MH)

        # Generate ONE consistent session ID
        self._session_id = session_id if session_id else f"session_{uuid4()}"
        self.session_uri = self.MH[self._session_id]

        # Add session type
        self.session_graph.add((self.session_uri, RDF.type, self.MH.Session))

        # Add session ID literal (SAME as URI for traceability)
        self.session_graph.add((
            self.session_uri,
            self.MH.sessionId,
            Literal(self._session_id, datatype=XSD.string)
        ))

        # Add timestamp
        self.session_graph.add((
            self.session_uri,
            self.MH.sessionTimestamp,
            Literal(datetime.utcnow().isoformat() + "Z", datatype=XSD.dateTime)
        ))

        # Link session to student
        self.session_graph.add((
            self.session_uri,
            self.MH.hasSessionStudent,
            student_uri
        ))

        return self.session_uri

    def load_existing_session(self, session_graph_path: str) -> URIRef:
        """
        Load a previously saved session graph for multi-turn accumulation.
        
        This allows new evidence to be appended to an existing session
        without losing previous context.
        
        Args:
            session_graph_path: Path to the existing session TTL file
        
        Returns:
            URIRef: The session URI extracted from the loaded graph
        
        Note:
            - This method ONLY loads RDF triples
            - It does NOT infer or modify existing triples
            - It does NOT perform any reasoning
        """
        self.session_graph = Graph()
        self.session_graph.bind("mh", self.MH)
        self.session_graph.parse(session_graph_path, format="turtle")

        # Extract the session URI from the loaded graph
        for s, p, o in self.session_graph.triples((None, RDF.type, self.MH.Session)):
            self.session_uri = s
            break

        # Extract session ID from literal
        if self.session_uri:
            for s, p, o in self.session_graph.triples((self.session_uri, self.MH.sessionId, None)):
                self._session_id = str(o)
                break

        return self.session_uri

    def add_evidence(self, evidence_uri: URIRef) -> None:
        """
        Attach evidence to the current session.
        
        Args:
            evidence_uri: URI of the evidence (emotion, symptom, or behavior)
        
        Note:
            Evidence must already exist as a typed individual.
            This method only creates the hasEvidence link.
        """
        if self.session_graph is None or self.session_uri is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        self.session_graph.add((
            self.session_uri,
            self.MH.hasEvidence,
            evidence_uri
        ))

    def add_derived_state(self, mental_state_uri: URIRef) -> None:
        """
        Record an inferred mental state for the session.
        
        Args:
            mental_state_uri: URI of the mental state (e.g., mh:AnxietyRisk)
        
        Note:
            The derivation itself is done by SWRL/SPARQL in downstream phases.
            This method only records the result symbolically.
        """
        if self.session_graph is None or self.session_uri is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        self.session_graph.add((
            self.session_uri,
            self.MH.derivedState,
            mental_state_uri
        ))

    def add_confidence_label(self, evidence_uri: URIRef, label: str) -> None:
        """
        Attach a symbolic confidence label to an evidence item.
        
        Args:
            evidence_uri: URI of the evidence
            label: Symbolic label (e.g., "HIGH", "MEDIUM", "LOW")
        
        Note:
            This is a SYMBOLIC label, NOT a numeric score.
            Valid values: "HIGH", "MEDIUM", "LOW"
        """
        if self.session_graph is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        valid_labels = {"HIGH", "MEDIUM", "LOW"}
        if label not in valid_labels:
            raise ValueError(f"Invalid confidence label '{label}'. Must be one of: {valid_labels}")
        
        self.session_graph.add((
            evidence_uri,
            self.MH.confidenceLabel,
            Literal(label, datatype=XSD.string)
        ))

    def add_persistence_label(self, evidence_uri: URIRef, label: str) -> None:
        """
        Attach a symbolic persistence label to an evidence item.
        
        Args:
            evidence_uri: URI of the evidence
            label: Symbolic label (e.g., "PERSISTENT", "TRANSIENT", "RECURRING")
        
        Note:
            This is a SYMBOLIC label, NOT a numeric duration.
            Valid values: "PERSISTENT", "TRANSIENT", "RECURRING"
        """
        if self.session_graph is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        valid_labels = {"PERSISTENT", "TRANSIENT", "RECURRING"}
        if label not in valid_labels:
            raise ValueError(f"Invalid persistence label '{label}'. Must be one of: {valid_labels}")
        
        self.session_graph.add((
            evidence_uri,
            self.MH.persistenceLabel,
            Literal(label, datatype=XSD.string)
        ))

    def add_evidence_type(self, evidence_uri: URIRef, *type_uris: URIRef) -> None:
        """
        Declare the RDF types for an evidence individual.
        
        Args:
            evidence_uri: URI of the evidence
            type_uris: One or more class URIs (e.g., mh:Emotion, mh:Anxiety)
        """
        if self.session_graph is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        for type_uri in type_uris:
            self.session_graph.add((evidence_uri, RDF.type, type_uri))

    def export_session(self, output_path: str) -> None:
        """
        Persist session graph to a TTL file.
        
        Args:
            output_path: File path for the exported TTL
        
        Note:
            The exported file is a standalone, mergeable TTL
            that can be loaded for reasoning or audit.
        """
        if self.session_graph is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        self.session_graph.serialize(destination=output_path, format="turtle")

    def get_merged_graph(self) -> Graph:
        """
        Merge ontology + base graph + session graph for downstream reasoning.
        
        Returns:
            Graph: A new graph containing all triples from:
                   - Ontology (class/property definitions)
                   - Base graph (domain knowledge)
                   - Session graph (current session data)
        
        Note:
            This is used by downstream phases (SPARQL, Ranker, etc.)
            The merged graph is READ-ONLY for reasoning purposes.
        """
        if self.session_graph is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        merged = Graph()
        merged.bind("mh", self.MH)
        
        for g in [self.ontology_graph, self.base_graph, self.session_graph]:
            for triple in g:
                merged.add(triple)
        
        return merged

    def get_session_id(self) -> Optional[str]:
        """
        Get the current session ID.
        
        Returns:
            str: The session ID, or None if no session is active
        """
        return self._session_id

    def get_session_uri(self) -> Optional[URIRef]:
        """
        Get the current session URI.
        
        Returns:
            URIRef: The session URI, or None if no session is active
        """
        return self.session_uri
