from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD
from uuid import uuid4
from datetime import datetime
from typing import Optional


class GraphManager:

    MH = Namespace("http://www.semanticweb.org/hunaizanaveed/ontologies/2025/11/krr_project#")

    def __init__(self, ontology_path: str, base_graph_path: str):

        self.ontology_graph = Graph()
        self.base_graph = Graph()
        self.session_graph: Optional[Graph] = None
        self.session_uri: Optional[URIRef] = None
        self._session_id: Optional[str] = None

        # Load ontology and base graph (read-only reference)
        self.ontology_graph.parse(ontology_path)
        self.base_graph.parse(base_graph_path, format="turtle")

    def create_session(self, student_uri: URIRef, session_id: Optional[str] = None) -> URIRef:
 
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

        if self.session_graph is None or self.session_uri is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        self.session_graph.add((
            self.session_uri,
            self.MH.hasEvidence,
            evidence_uri
        ))

    def add_derived_state(self, mental_state_uri: URIRef) -> None:

        if self.session_graph is None or self.session_uri is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        self.session_graph.add((
            self.session_uri,
            self.MH.derivedState,
            mental_state_uri
        ))

    def add_confidence_label(self, evidence_uri: URIRef, label: str) -> None:

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

        if self.session_graph is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        for type_uri in type_uris:
            self.session_graph.add((evidence_uri, RDF.type, type_uri))

    def export_session(self, output_path: str) -> None:

        if self.session_graph is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        self.session_graph.serialize(destination=output_path, format="turtle")

    def get_merged_graph(self) -> Graph:

        if self.session_graph is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        merged = Graph()
        merged.bind("mh", self.MH)
        
        for g in [self.ontology_graph, self.base_graph, self.session_graph]:
            for triple in g:
                merged.add(triple)
        return merged

    def get_session_id(self) -> Optional[str]:
        return self._session_id

    def get_session_uri(self) -> Optional[URIRef]:
        return self.session_uri
        
    def scan_history_for_persistence(self, student_uri: URIRef, session_dir: str) -> bool:

        import os
        from pathlib import Path
        
        count = 0
        current_id = self._session_id
        
        path = Path(session_dir)
        if not path.exists():
            return False
            
        for file in path.glob("*.ttl"):
            if current_id and current_id in file.name:
                continue
                
            try:
                content = file.read_text(encoding="utf-8")
                if str(student_uri) in content:
                    if "NeedsMoreContext" in content:
                        count += 1

            except Exception:
                continue
                
            if count >= 1: 
                
        return False
