"""Scoring Agent: Executes deterministic multi-attribute compatibility scoring and ranking"""

from typing import List, Tuple
from src.models import (
    GradeRecord,
    EngineeringRequirements,
    PriorityWeights,
    HardConstraintCheck,
    ScoredCandidate
)
from src.scoring import (
    calculate_compatibility_breakdown,
    extract_candidate_highlights
)


class ScoringAgent:
    """Calculates normalized component compatibility and overall weighted score"""

    @classmethod
    def score_and_rank(
        cls,
        eligible_grades: List[Tuple[GradeRecord, HardConstraintCheck]],
        req: EngineeringRequirements,
        weights: PriorityWeights
    ) -> List[ScoredCandidate]:
        """
        Calculates compatibility scores for all eligible candidates and returns them sorted by final score.
        """
        candidates: List[ScoredCandidate] = []

        for grade, check in eligible_grades:
            breakdown = calculate_compatibility_breakdown(grade, req, weights)
            strengths, limitations = extract_candidate_highlights(grade, breakdown)

            candidate = ScoredCandidate(
                grade=grade,
                score_breakdown=breakdown,
                constraint_check=check,
                key_strengths=strengths,
                key_limitations=limitations
            )
            candidates.append(candidate)

        # Sort descending by final score
        candidates.sort(key=lambda c: c.score_breakdown.final_score, reverse=True)

        # Assign ranks
        for idx, c in enumerate(candidates, start=1):
            c.rank = idx

        return candidates
