"""Trade-Off Agent: Analyzes pairwise trade-offs and runs interactive What-If sensitivity analysis"""

from typing import List, Dict, Any, Tuple
from src.models import (
    ScoredCandidate,
    TradeOffComparison,
    EngineeringRequirements,
    PriorityWeights
)
from src.scoring import compare_two_grades, calculate_compatibility_breakdown


class TradeOffAgent:
    """Analyzes differences between top candidates and provides priority sensitivity simulation"""

    @classmethod
    def evaluate_trade_offs(
        cls,
        primary: ScoredCandidate,
        alternatives: List[ScoredCandidate]
    ) -> List[TradeOffComparison]:
        """
        Generates pairwise comparisons between the primary recommendation and each alternative.
        """
        comparisons = []
        for alt in alternatives:
            comp = compare_two_grades(primary, alt)
            comparisons.append(comp)
        return comparisons

    @classmethod
    def simulate_what_if(
        cls,
        candidates: List[ScoredCandidate],
        req: EngineeringRequirements,
        new_weights: PriorityWeights
    ) -> List[Tuple[str, float, int]]:
        """
        Dynamically recalculates scores and ranks under hypothetical new priority weights.
        Returns list of (grade_name, new_score, new_rank).
        """
        resimulated = []
        for c in candidates:
            new_bd = calculate_compatibility_breakdown(c.grade, req, new_weights)
            resimulated.append({
                "grade_name": c.grade.grade_name,
                "score": new_bd.final_score,
                "candidate": c
            })

        resimulated.sort(key=lambda x: x["score"], reverse=True)
        results = []
        for rank, item in enumerate(resimulated, start=1):
            results.append((item["grade_name"], item["score"], rank))

        return results
