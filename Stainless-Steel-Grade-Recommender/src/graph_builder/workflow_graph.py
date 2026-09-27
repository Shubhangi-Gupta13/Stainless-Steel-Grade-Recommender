"""LangGraph workflow for Stainless Steel Agentic Recommendation Pipeline"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END

from src.models import (
    FabricatorRequirements,
    EngineeringRequirements,
    PriorityWeights,
    GradeRecord,
    HardConstraintCheck,
    ScoredCandidate,
    TradeOffComparison,
    BottleneckAnalysis,
    RecommendationPackage
)
from src.knowledge_base import get_knowledge_base
from src.agents.interpretation_layer import InterpretationLayer
from src.agents.constraint_agent import ConstraintAgent
from src.agents.scoring_agent import ScoringAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.tradeoff_agent import TradeOffAgent
from src.agents.explanation_agent import ExplanationAgent


class MaterialSelectionState(BaseModel):
    """LangGraph State object tracking the complete decision-support pipeline"""
    mode: str = "fabricator"
    fabricator_input: Optional[FabricatorRequirements] = None
    engineering_input: Optional[EngineeringRequirements] = None
    custom_weights: Optional[PriorityWeights] = None
    
    # Processed states
    active_engineering_req: Optional[EngineeringRequirements] = None
    active_weights: Optional[PriorityWeights] = None
    assumptions: List[str] = Field(default_factory=list)
    retrieved_snippets: List[Dict[str, Any]] = Field(default_factory=list)
    
    eligible_grades: List[Tuple[Any, Any]] = Field(default_factory=list)
    excluded_grades: List[Tuple[Any, Any]] = Field(default_factory=list)
    bottleneck: Optional[BottleneckAnalysis] = None
    
    scored_candidates: List[ScoredCandidate] = Field(default_factory=list)
    trade_offs: List[TradeOffComparison] = Field(default_factory=list)
    explanation: str = ""
    result_package: Optional[RecommendationPackage] = None


class WorkflowGraphBuilder:
    """Builds and compiles the multi-agent StateGraph"""

    def __init__(self):
        self.kb = get_knowledge_base()
        self.retrieval_agent = RetrievalAgent()
        self.explanation_agent = ExplanationAgent()

    # --- Node 1: Interpretation ---
    def interpret_node(self, state: MaterialSelectionState) -> Dict[str, Any]:
        if state.mode == "fabricator" and state.fabricator_input:
            eng_req, default_w, assumptions = InterpretationLayer.interpret(state.fabricator_input)
            weights = state.custom_weights or default_w
            return {
                "active_engineering_req": eng_req,
                "active_weights": weights,
                "assumptions": assumptions
            }
        else:
            eng_req = state.engineering_input or EngineeringRequirements()
            weights = state.custom_weights or PriorityWeights()
            return {
                "active_engineering_req": eng_req,
                "active_weights": weights,
                "assumptions": []
            }

    # --- Node 2: Retrieval ---
    def retrieve_node(self, state: MaterialSelectionState) -> Dict[str, Any]:
        req = state.active_engineering_req or EngineeringRequirements()
        snippets = self.retrieval_agent.retrieve_context_for_query(
            application_context=req.environment_type,
            environment_context=req.chloride_exposure,
            top_k=4
        )
        return {"retrieved_snippets": snippets}

    # --- Node 3: Hard Constraints ---
    def constraint_node(self, state: MaterialSelectionState) -> Dict[str, Any]:
        req = state.active_engineering_req or EngineeringRequirements()
        all_grades = self.kb.get_all_grades()
        eligible, excluded, bottleneck = ConstraintAgent.audit_grades(all_grades, req)
        return {
            "eligible_grades": eligible,
            "excluded_grades": excluded,
            "bottleneck": bottleneck
        }

    # --- Router ---
    def check_eligibility_route(self, state: MaterialSelectionState) -> str:
        if state.eligible_grades and len(state.eligible_grades) > 0:
            return "scoring_node"
        return "bottleneck_node"

    # --- Node 4A: Scoring ---
    def scoring_node(self, state: MaterialSelectionState) -> Dict[str, Any]:
        req = state.active_engineering_req or EngineeringRequirements()
        weights = state.active_weights or PriorityWeights()
        candidates = ScoringAgent.score_and_rank(state.eligible_grades, req, weights)
        for c in candidates:
            self.retrieval_agent.attach_citations(c)
        return {"scored_candidates": candidates}

    # --- Node 4B: Trade-Offs ---
    def tradeoff_node(self, state: MaterialSelectionState) -> Dict[str, Any]:
        primary = state.scored_candidates[0]
        alternatives = state.scored_candidates[1:5] if len(state.scored_candidates) > 1 else []
        trade_offs = TradeOffAgent.evaluate_trade_offs(primary, alternatives)
        return {"trade_offs": trade_offs}

    # --- Node 5: Explanation ---
    def explain_node(self, state: MaterialSelectionState) -> Dict[str, Any]:
        primary = state.scored_candidates[0] if state.scored_candidates else None
        alternatives = state.scored_candidates[1:5] if len(state.scored_candidates) > 1 else []
        explanation = self.explanation_agent.generate_explanation(
            mode=state.mode,
            primary=primary,
            top_alternatives=alternatives,
            trade_offs=state.trade_offs,
            req=state.active_engineering_req or EngineeringRequirements(),
            weights=state.active_weights or PriorityWeights(),
            assumptions=state.assumptions,
            retrieved_snippets=state.retrieved_snippets,
            bottleneck=state.bottleneck
        )
        return {"explanation": explanation}

    # --- Node 6: Bottleneck Explanation ---
    def bottleneck_node(self, state: MaterialSelectionState) -> Dict[str, Any]:
        explanation = self.explanation_agent.generate_explanation(
            mode=state.mode,
            primary=None,
            top_alternatives=[],
            trade_offs=[],
            req=state.active_engineering_req or EngineeringRequirements(),
            weights=state.active_weights or PriorityWeights(),
            assumptions=state.assumptions,
            retrieved_snippets=state.retrieved_snippets,
            bottleneck=state.bottleneck
        )
        return {"explanation": explanation}

    # --- Node 7: Assembly ---
    def package_node(self, state: MaterialSelectionState) -> Dict[str, Any]:
        primary = state.scored_candidates[0] if state.scored_candidates else None
        alternatives = state.scored_candidates[1:5] if len(state.scored_candidates) > 1 else []
        w = state.active_weights or PriorityWeights()
        
        excluded_candidates: List[ScoredCandidate] = []
        for g, check in state.excluded_grades:
            from src.scoring import calculate_compatibility_breakdown, extract_candidate_highlights
            bd = calculate_compatibility_breakdown(g, state.active_engineering_req or EngineeringRequirements(), w)
            st, lim = extract_candidate_highlights(g, bd)
            excluded_candidates.append(ScoredCandidate(
                grade=g, score_breakdown=bd, constraint_check=check, key_strengths=st, key_limitations=lim
            ))

        pkg = RecommendationPackage(
            mode=state.mode,
            primary_recommendation=primary,
            top_alternatives=alternatives,
            all_eligible_candidates=state.scored_candidates,
            excluded_candidates=excluded_candidates,
            bottleneck_analysis=state.bottleneck,
            trade_offs=state.trade_offs,
            assumptions_made=state.assumptions,
            applied_weights={
                "corrosion": w.corrosion,
                "strength": w.strength,
                "cost": w.cost,
                "formability": w.formability,
                "weldability": w.weldability
            },
            engineering_rationale=state.explanation
        )
        return {"result_package": pkg}

    def build(self):
        builder = StateGraph(MaterialSelectionState)
        builder.add_node("interpret_node", self.interpret_node)
        builder.add_node("retrieve_node", self.retrieve_node)
        builder.add_node("constraint_node", self.constraint_node)
        builder.add_node("scoring_node", self.scoring_node)
        builder.add_node("tradeoff_node", self.tradeoff_node)
        builder.add_node("explain_node", self.explain_node)
        builder.add_node("bottleneck_node", self.bottleneck_node)
        builder.add_node("package_node", self.package_node)

        builder.set_entry_point("interpret_node")
        builder.add_edge("interpret_node", "retrieve_node")
        builder.add_edge("retrieve_node", "constraint_node")

        builder.add_conditional_edges(
            "constraint_node",
            self.check_eligibility_route,
            {
                "scoring_node": "scoring_node",
                "bottleneck_node": "bottleneck_node"
            }
        )

        builder.add_edge("scoring_node", "tradeoff_node")
        builder.add_edge("tradeoff_node", "explain_node")
        builder.add_edge("explain_node", "package_node")
        builder.add_edge("bottleneck_node", "package_node")
        builder.add_edge("package_node", END)

        return builder.compile()


_GRAPH_EXECUTOR = None

def get_recommendation_graph():
    global _GRAPH_EXECUTOR
    if _GRAPH_EXECUTOR is None:
        builder = WorkflowGraphBuilder()
        _GRAPH_EXECUTOR = builder.build()
    return _GRAPH_EXECUTOR
