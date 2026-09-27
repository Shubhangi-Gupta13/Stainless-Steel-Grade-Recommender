"""Recommendation Agent: Orchestrates the multi-agent workflow and produces the final decision-support dossier"""

from typing import Union, Dict, Any, List, Optional
from src.knowledge_base import get_knowledge_base
from src.models import (
    FabricatorRequirements,
    EngineeringRequirements,
    PriorityWeights,
    RecommendationPackage,
    ScoredCandidate
)
from src.agents.interpretation_layer import InterpretationLayer
from src.agents.constraint_agent import ConstraintAgent
from src.agents.scoring_agent import ScoringAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.tradeoff_agent import TradeOffAgent
from src.agents.explanation_agent import ExplanationAgent


class RecommendationAgent:
    """Master agent coordinating interpretation, retrieval, constraints, scoring, trade-offs, and explanation"""

    def __init__(self):
        self.kb = get_knowledge_base()
        self.retrieval_agent = RetrievalAgent()
        self.explanation_agent = ExplanationAgent()

    def process_recommendation(
        self,
        user_input: Union[FabricatorRequirements, EngineeringRequirements],
        custom_weights: Optional[PriorityWeights] = None
    ) -> RecommendationPackage:
        """
        Executes end-to-end material selection workflow:
        Input -> Interpretation -> Hard Constraints -> Compatibility Scoring -> Trade-Offs -> Explanation -> Decision Package
        """
        assumptions: List[str] = []
        is_fabricator = isinstance(user_input, FabricatorRequirements)
        mode = "fabricator" if is_fabricator else "engineering"

        # 1. Interpret requirements
        if is_fabricator:
            eng_req, default_weights, assumptions = InterpretationLayer.interpret(user_input)
            weights = custom_weights or default_weights
            app_desc = user_input.application
            env_desc = user_input.environment
        else:
            eng_req = user_input
            weights = custom_weights or PriorityWeights()
            app_desc = eng_req.environment_type
            env_desc = eng_req.chloride_exposure

        # 2. Retrieve relevant technical context from knowledge base
        retrieved_snippets = self.retrieval_agent.retrieve_context_for_query(
            application_context=app_desc,
            environment_context=env_desc,
            top_k=4
        )

        # 3. Apply hard constraints Go / No-Go audit
        all_grades = self.kb.get_all_grades()
        eligible_tuples, excluded_tuples, bottleneck = ConstraintAgent.audit_grades(
            all_grades=all_grades,
            req=eng_req
        )

        # Handle excluded candidate models
        excluded_candidates: List[ScoredCandidate] = []
        for g, check in excluded_tuples:
            from src.scoring import calculate_compatibility_breakdown, extract_candidate_highlights
            bd = calculate_compatibility_breakdown(g, eng_req, weights)
            st, lim = extract_candidate_highlights(g, bd)
            excluded_candidates.append(ScoredCandidate(
                grade=g,
                score_breakdown=bd,
                constraint_check=check,
                key_strengths=st,
                key_limitations=lim
            ))

        # 4. If no grades pass hard constraints:
        if not eligible_tuples:
            explanation = self.explanation_agent.generate_explanation(
                mode=mode,
                primary=None,
                top_alternatives=[],
                trade_offs=[],
                req=eng_req,
                weights=weights,
                assumptions=assumptions,
                retrieved_snippets=retrieved_snippets,
                bottleneck=bottleneck
            )
            return RecommendationPackage(
                mode=mode,
                primary_recommendation=None,
                top_alternatives=[],
                all_eligible_candidates=[],
                excluded_candidates=excluded_candidates,
                bottleneck_analysis=bottleneck,
                trade_offs=[],
                assumptions_made=assumptions,
                applied_weights={
                    "corrosion": weights.corrosion,
                    "strength": weights.strength,
                    "cost": weights.cost,
                    "formability": weights.formability,
                    "weldability": weights.weldability
                },
                engineering_rationale=explanation
            )

        # 5. Score and rank eligible grades
        scored_candidates = ScoringAgent.score_and_rank(
            eligible_grades=eligible_tuples,
            req=eng_req,
            weights=weights
        )

        # Enrich candidates with citations
        for c in scored_candidates:
            self.retrieval_agent.attach_citations(c)

        # Identify Primary Recommendation and Top 4 Alternatives (Top 5 total)
        primary = scored_candidates[0]
        top_alternatives = scored_candidates[1:5] if len(scored_candidates) > 1 else []

        # 6. Evaluate pairwise trade-offs
        trade_offs = TradeOffAgent.evaluate_trade_offs(
            primary=primary,
            alternatives=top_alternatives
        )

        # 7. Generate transparent engineering explanation
        explanation = self.explanation_agent.generate_explanation(
            mode=mode,
            primary=primary,
            top_alternatives=top_alternatives,
            trade_offs=trade_offs,
            req=eng_req,
            weights=weights,
            assumptions=assumptions,
            retrieved_snippets=retrieved_snippets,
            bottleneck=None
        )

        return RecommendationPackage(
            mode=mode,
            primary_recommendation=primary,
            top_alternatives=top_alternatives,
            all_eligible_candidates=scored_candidates,
            excluded_candidates=excluded_candidates,
            bottleneck_analysis=None,
            trade_offs=trade_offs,
            assumptions_made=assumptions,
            applied_weights={
                "corrosion": weights.corrosion,
                "strength": weights.strength,
                "cost": weights.cost,
                "formability": weights.formability,
                "weldability": weights.weldability
            },
            engineering_rationale=explanation
        )
