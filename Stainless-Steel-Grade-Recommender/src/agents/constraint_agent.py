"""Constraint Agent: Enforces mandatory engineering rules and identifies bottlenecks"""

from typing import List, Tuple, Optional
from src.models import (
    GradeRecord,
    EngineeringRequirements,
    HardConstraintCheck,
    BottleneckAnalysis
)
from src.scoring import evaluate_hard_constraints, diagnose_bottleneck_constraints


class ConstraintAgent:
    """Evaluates mandatory requirements and isolates eligible candidate pool"""

    @classmethod
    def audit_grades(
        cls,
        all_grades: List[GradeRecord],
        req: EngineeringRequirements
    ) -> Tuple[List[Tuple[GradeRecord, HardConstraintCheck]], List[Tuple[GradeRecord, HardConstraintCheck]], Optional[BottleneckAnalysis]]:
        """
        Filters all grades into (eligible_pool, excluded_pool, bottleneck_analysis).
        If eligible_pool is empty, returns bottleneck analysis pinpointing the exact conflict.
        """
        eligible = []
        excluded = []

        for grade in all_grades:
            check = evaluate_hard_constraints(grade, req)
            if check.passed:
                eligible.append((grade, check))
            else:
                excluded.append((grade, check))

        bottleneck = None
        if not eligible:
            bottleneck = diagnose_bottleneck_constraints(all_grades, req)

        return eligible, excluded, bottleneck
