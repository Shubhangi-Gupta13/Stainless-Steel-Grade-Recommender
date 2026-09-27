"""Retrieval Agent: Retrieves relevant technical documentation, standards, and citations from knowledge base"""

from typing import List, Dict, Any
from src.knowledge_base import get_knowledge_base
from src.models import EngineeringRequirements, ScoredCandidate


class RetrievalAgent:
    """Retrieves technical documentation snippets and attaches verified datasheet citations"""

    def __init__(self):
        self.kb = get_knowledge_base()

    def retrieve_context_for_query(
        self,
        application_context: str,
        environment_context: str,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Queries knowledge base with application and environmental keywords"""
        query = f"{application_context} {environment_context} corrosion welding formability"
        return self.kb.retrieve_relevant_snippets(query=query, top_k=top_k)

    def attach_citations(
        self,
        candidate: ScoredCandidate
    ) -> ScoredCandidate:
        """Enriches candidate with exact datasheet citation and standard references"""
        grade = candidate.grade
        citations = [
            f"Jindal Stainless Datasheet: {grade.source_reference}",
            f"Applicable Standards: {', '.join(grade.standards)}"
        ]
        if grade.corrosion_properties.cpt_c is not None:
            citations.append(f"ASTM G150 CPT: {grade.corrosion_properties.cpt_c}°C | PREN: {grade.corrosion_properties.pren}")
        if grade.corrosion_properties.cct_c is not None:
            citations.append(f"ASTM G48 Method F CCT: {grade.corrosion_properties.cct_c}°C")
        
        candidate.citations = citations
        return candidate
