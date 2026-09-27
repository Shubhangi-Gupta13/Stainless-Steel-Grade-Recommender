"""Deterministic, rule-based recommendation and scoring engine with hard constraint filtering and trade-off analysis"""

from typing import List, Dict, Any, Tuple, Optional
from src.models import (
    GradeRecord,
    EngineeringRequirements,
    PriorityWeights,
    HardConstraintCheck,
    GradeScoreBreakdown,
    ScoredCandidate,
    TradeOffComparison,
    BottleneckAnalysis
)


def evaluate_hard_constraints(
    grade: GradeRecord,
    req: EngineeringRequirements
) -> HardConstraintCheck:
    """
    Evaluates mandatory GO/NO-GO constraints.
    Returns HardConstraintCheck with passed status, failure reasons, and warnings.
    """
    failed_reasons = []
    warning_reasons = []

    # 1. Non-magnetic mandatory check
    if req.non_magnetic_mandatory:
        if "non-magnetic" not in grade.magnetic_behavior.lower() or grade.magnetic_permeability_relative > 1.05:
            failed_reasons.append(
                f"Fails mandatory non-magnetic requirement: Grade is {grade.magnetic_behavior.lower()} "
                f"(relative permeability μr ≈ {grade.magnetic_permeability_relative})."
            )

    # 2. Maximum magnetic permeability check
    if req.max_magnetic_permeability is not None:
        if grade.magnetic_permeability_relative > req.max_magnetic_permeability:
            failed_reasons.append(
                f"Permeability ({grade.magnetic_permeability_relative}) exceeds maximum allowable limit ({req.max_magnetic_permeability})."
            )

    # 3. Yield Strength minimum requirement
    if req.min_yield_strength_mpa is not None:
        if grade.mechanical_properties.yield_strength_min_mpa < req.min_yield_strength_mpa:
            failed_reasons.append(
                f"Yield strength ({grade.mechanical_properties.yield_strength_min_mpa} MPa) is below required minimum ({req.min_yield_strength_mpa} MPa)."
            )

    # 4. Tensile Strength minimum requirement
    if req.min_tensile_strength_mpa is not None:
        if grade.mechanical_properties.tensile_strength_min_mpa < req.min_tensile_strength_mpa:
            failed_reasons.append(
                f"Tensile strength ({grade.mechanical_properties.tensile_strength_min_mpa} MPa) is below required minimum ({req.min_tensile_strength_mpa} MPa)."
            )

    # 5. Elongation minimum requirement
    if req.min_elongation_pct is not None:
        if grade.mechanical_properties.elongation_min_pct < req.min_elongation_pct:
            failed_reasons.append(
                f"Elongation ({grade.mechanical_properties.elongation_min_pct}%) is below minimum required ductility ({req.min_elongation_pct}%)."
            )

    # 6. Hardness maximum requirement
    if req.max_hardness_hrb is not None:
        if grade.mechanical_properties.hardness_hrb_val > req.max_hardness_hrb:
            failed_reasons.append(
                f"Hardness ({grade.mechanical_properties.hardness_max}) exceeds allowable maximum ({req.max_hardness_hrb} HRB)."
            )

    # 7. Minimum service temperature
    if req.min_service_temp_c is not None:
        if grade.temperature_capability.min_service_temp_c > req.min_service_temp_c:
            failed_reasons.append(
                f"Cannot operate at minimum service temperature {req.min_service_temp_c}°C (Grade lower capability is {grade.temperature_capability.min_service_temp_c}°C)."
            )

    # 8. Maximum continuous service temperature
    if req.max_service_temp_c is not None:
        if grade.temperature_capability.max_continuous_temp_c < req.max_service_temp_c:
            failed_reasons.append(
                f"Continuous temperature capability ({grade.temperature_capability.max_continuous_temp_c}°C) is below operating requirement ({req.max_service_temp_c}°C)."
            )

    # 9. Minimum PREN / Pitting resistance
    if req.min_pren is not None:
        if grade.corrosion_properties.pren < req.min_pren:
            failed_reasons.append(
                f"PREN ({grade.corrosion_properties.pren}) is below specified minimum threshold ({req.min_pren})."
            )

    # 10. Maximum budget / Cost index
    if req.max_budget_cost_index is not None:
        if grade.commercial.relative_cost_index > req.max_budget_cost_index:
            failed_reasons.append(
                f"Relative cost index ({grade.commercial.relative_cost_index}/10) exceeds specified budget ceiling ({req.max_budget_cost_index}/10)."
            )

    # 11. Minimum weldability score
    if req.weldability_min_score is not None:
        if grade.manufacturing_properties.weldability_score < req.weldability_min_score:
            failed_reasons.append(
                f"Weldability score ({grade.manufacturing_properties.weldability_score}/10) does not meet minimum threshold ({req.weldability_min_score}/10)."
            )

    # 12. Minimum formability score
    if req.formability_min_score is not None:
        if grade.manufacturing_properties.formability_score < req.formability_min_score:
            failed_reasons.append(
                f"Formability score ({grade.manufacturing_properties.formability_score}/10) does not meet minimum threshold ({req.formability_min_score}/10)."
            )

    # 13. Allowed microstructure / family filtering
    if req.allowed_microstructures:
        matched = any(
            allowed.lower() in grade.family.lower() or allowed.lower() in grade.microstructure.lower()
            for allowed in req.allowed_microstructures
        )
        if not matched:
            failed_reasons.append(
                f"Microstructure '{grade.family}' is not in selected allowed families: {', '.join(req.allowed_microstructures)}."
            )

    # 14. Alloying element limits
    comp = grade.composition
    if req.cr_min is not None and (comp.Cr_min or 0.0) < req.cr_min:
        failed_reasons.append(f"Chromium min ({comp.Cr_min}%) is below required {req.cr_min}%.")
    if req.ni_max is not None and (comp.Ni_max or 0.0) > req.ni_max:
        failed_reasons.append(f"Nickel max ({comp.Ni_max}%) exceeds allowable {req.ni_max}%.")
    if req.mo_min is not None and (comp.Mo_min or 0.0) < req.mo_min:
        failed_reasons.append(f"Molybdenum min ({comp.Mo_min}%) is below required {req.mo_min}%.")
    if req.c_max is not None and (comp.C_max or 0.0) > req.c_max:
        failed_reasons.append(f"Carbon max ({comp.C_max}%) exceeds allowable limit {req.c_max}%.")

    # Warnings for edge cases
    if grade.family == "Duplex Stainless Steel" and (req.max_service_temp_c or 0) > 280:
        warning_reasons.append(
            "Service temperature approaches duplex 475°C spinodal decomposition limit; ensure long-term thermal stability."
        )

    passed = len(failed_reasons) == 0
    status = "PASSED" if passed else "FAILED"
    if passed and warning_reasons:
        status = "WARNING"

    return HardConstraintCheck(
        passed=passed,
        status=status,
        failed_reasons=failed_reasons,
        warning_reasons=warning_reasons
    )


def calculate_compatibility_breakdown(
    grade: GradeRecord,
    req: EngineeringRequirements,
    weights: PriorityWeights
) -> GradeScoreBreakdown:
    """
    Computes normalized compatibility scores (0.0 - 1.0) for individual engineering attributes
    and aggregates them into a final weighted score (0.0 - 100.0%).
    Deterministic and fully auditable.
    """
    # 1. Corrosion Compatibility (0.0 - 1.0)
    # Base on PREN normalized against 45.0, combined with general corrosion rating
    pren_norm = min(1.0, max(0.2, grade.corrosion_properties.pren / 42.0))
    gen_corr_norm = grade.corrosion_properties.general_corrosion_score / 10.0
    corrosion_compat = 0.6 * pren_norm + 0.4 * gen_corr_norm

    # Adjust for specific environmental severity if specified
    if req.chloride_exposure == "High" or "Marine" in req.environment_type or "Coastal" in req.environment_type:
        # Boost grades with PREN >= 30, penalize PREN < 20 in severe chloride
        if grade.corrosion_properties.pren >= 34.0:
            corrosion_compat = min(1.0, corrosion_compat * 1.15)
        elif grade.corrosion_properties.pren < 22.0:
            corrosion_compat = max(0.1, corrosion_compat * 0.70)

    # 2. Strength Compatibility (0.0 - 1.0)
    ys = grade.mechanical_properties.yield_strength_min_mpa
    if req.min_yield_strength_mpa and req.min_yield_strength_mpa > 0:
        ratio = ys / req.min_yield_strength_mpa
        # 1.0 if exactly met, slight bonus up to 1.1 for safety factor, scaled to 1.0
        strength_compat = min(1.0, max(0.2, 0.8 + 0.2 * (ratio - 1.0) if ratio >= 1.0 else ratio * 0.8))
    else:
        # Normalized against 600 MPa scale
        strength_compat = min(1.0, max(0.25, ys / 550.0))

    # 3. Cost Compatibility (0.0 - 1.0) - Lower cost is better!
    # Cost index ranges from 3.5 (budget ferritics) to 9.8 (super austenitics/duplex)
    cost_index = grade.commercial.relative_cost_index
    cost_compat = max(0.05, min(1.0, 1.0 - ((cost_index - 3.5) / (9.8 - 3.5))))

    # 4. Formability Compatibility (0.0 - 1.0)
    form_base = grade.manufacturing_properties.formability_score / 10.0
    el_norm = min(1.0, grade.mechanical_properties.elongation_min_pct / 50.0)
    formability_compat = 0.6 * form_base + 0.4 * el_norm

    # 5. Weldability Compatibility (0.0 - 1.0)
    weldability_compat = grade.manufacturing_properties.weldability_score / 10.0

    # 6. Temperature Compatibility (0.0 - 1.0)
    if req.max_service_temp_c and req.max_service_temp_c > 0:
        margin = grade.temperature_capability.max_continuous_temp_c - req.max_service_temp_c
        temp_compat = min(1.0, max(0.3, 0.7 + (margin / 500.0)))
    else:
        temp_compat = min(1.0, grade.temperature_capability.max_continuous_temp_c / 1000.0)

    # Aggregate weighted score
    w_sum = (
        weights.corrosion +
        weights.strength +
        weights.cost +
        weights.formability +
        weights.weldability +
        weights.temperature_margin
    )
    if w_sum <= 0:
        w_sum = 1.0

    weighted_score = (
        weights.corrosion * corrosion_compat +
        weights.strength * strength_compat +
        weights.cost * cost_compat +
        weights.formability * formability_compat +
        weights.weldability * weldability_compat +
        weights.temperature_margin * temp_compat
    ) / w_sum

    final_pct = round(weighted_score * 100.0, 1)

    return GradeScoreBreakdown(
        corrosion_compat=round(corrosion_compat, 3),
        strength_compat=round(strength_compat, 3),
        cost_compat=round(cost_compat, 3),
        formability_compat=round(formability_compat, 3),
        weldability_compat=round(weldability_compat, 3),
        temperature_compat=round(temp_compat, 3),
        final_score=final_pct
    )


def extract_candidate_highlights(
    grade: GradeRecord,
    breakdown: GradeScoreBreakdown
) -> Tuple[List[str], List[str]]:
    """Generates specific strengths and limitations for a candidate based on technical data"""
    strengths = []
    limitations = []

    # Strengths
    if grade.corrosion_properties.pren >= 34.0:
        strengths.append(f"Exceptional pitting and crevice corrosion resistance (PREN {grade.corrosion_properties.pren})")
    elif grade.corrosion_properties.pren >= 23.0:
        strengths.append(f"Proven marine and chloride corrosion resistance (PREN {grade.corrosion_properties.pren})")

    if grade.mechanical_properties.yield_strength_min_mpa >= 400:
        strengths.append(f"High mechanical strength (Yield Strength {grade.mechanical_properties.yield_strength_min_mpa} MPa) enabling structural weight reduction")
    elif grade.mechanical_properties.elongation_min_pct >= 40:
        strengths.append(f"Excellent ductility and deep drawability ({grade.mechanical_properties.elongation_min_pct}% elongation)")

    if grade.commercial.relative_cost_index <= 5.0:
        strengths.append(f"Cost-effective material choice (relative cost index {grade.commercial.relative_cost_index}/10)")

    if "non-magnetic" in grade.magnetic_behavior.lower():
        strengths.append("Non-magnetic in annealed condition")

    if grade.temperature_capability.max_continuous_temp_c >= 900:
        strengths.append(f"High oxidation resistance up to {grade.temperature_capability.max_continuous_temp_c}°C")

    # Limitations
    for lim in grade.limitations[:2]:
        limitations.append(lim)

    return strengths, limitations


def compare_two_grades(
    primary: ScoredCandidate,
    alternative: ScoredCandidate
) -> TradeOffComparison:
    """Calculates granular trade-offs between two scored candidates"""
    p_grd = primary.grade
    a_grd = alternative.grade
    p_sc = primary.score_breakdown
    a_sc = alternative.score_breakdown

    score_diff = round(p_sc.final_score - a_sc.final_score, 1)
    corr_delta = round((p_sc.corrosion_compat - a_sc.corrosion_compat) * 100, 1)
    strength_delta = p_grd.mechanical_properties.yield_strength_min_mpa - a_grd.mechanical_properties.yield_strength_min_mpa
    cost_delta = round(p_grd.commercial.relative_cost_index - a_grd.commercial.relative_cost_index, 1)
    form_delta = round((p_sc.formability_compat - a_sc.formability_compat) * 100, 1)
    weld_delta = round((p_sc.weldability_compat - a_sc.weldability_compat) * 100, 1)

    advantages = []
    sacrifices = []

    # Advantages of Primary over Alternative
    if corr_delta > 5:
        advantages.append(f"Higher corrosion resistance (PREN {p_grd.corrosion_properties.pren} vs {a_grd.corrosion_properties.pren}, +{corr_delta}% score)")
    if strength_delta > 40:
        advantages.append(f"Higher yield strength (+{strength_delta} MPa, {p_grd.mechanical_properties.yield_strength_min_mpa} vs {a_grd.mechanical_properties.yield_strength_min_mpa} MPa)")
    if cost_delta < -0.5:
        advantages.append(f"Lower raw material cost (Cost index {p_grd.commercial.relative_cost_index} vs {a_grd.commercial.relative_cost_index})")
    if form_delta > 5:
        advantages.append(f"Superior cold forming & drawability (+{form_delta}% formability score)")
    if "non-magnetic" in p_grd.magnetic_behavior.lower() and "magnetic" in a_grd.magnetic_behavior.lower() and "non-magnetic" not in a_grd.magnetic_behavior.lower():
        advantages.append("Non-magnetic behavior (alternative is magnetic)")

    # Sacrifices when choosing Primary over Alternative
    if cost_delta > 0.5:
        sacrifices.append(f"Higher material cost (Cost index {p_grd.commercial.relative_cost_index} vs {a_grd.commercial.relative_cost_index} for {a_grd.grade_name})")
    if strength_delta < -40:
        sacrifices.append(f"Lower yield strength ({p_grd.mechanical_properties.yield_strength_min_mpa} MPa vs {a_grd.mechanical_properties.yield_strength_min_mpa} MPa)")
    if corr_delta < -5:
        sacrifices.append(f"Lower corrosion performance (PREN {p_grd.corrosion_properties.pren} vs {a_grd.corrosion_properties.pren})")
    if form_delta < -5:
        sacrifices.append(f"Reduced elongation and cold drawability ({p_grd.mechanical_properties.elongation_min_pct}% vs {a_grd.mechanical_properties.elongation_min_pct}%)")

    # Generate synthesis summary
    summary_parts = []
    if advantages:
        summary_parts.append(f"Choosing {p_grd.grade_name} gives {advantages[0].lower()}")
    if sacrifices:
        summary_parts.append(f"while sacrificing {sacrifices[0].lower()}")
    summary_text = ", ".join(summary_parts) + "." if summary_parts else f"{p_grd.grade_name} offers a more balanced overall compatibility score."

    return TradeOffComparison(
        primary_grade=p_grd.grade_name,
        alternative_grade=a_grd.grade_name,
        score_difference=score_diff,
        corrosion_delta=corr_delta,
        strength_delta_mpa=float(strength_delta),
        cost_delta_index=cost_delta,
        formability_delta=form_delta,
        weldability_delta=weld_delta,
        advantages_of_primary=advantages,
        sacrifices_of_primary=sacrifices,
        summary_text=summary_text
    )


def diagnose_bottleneck_constraints(
    all_grades: List[GradeRecord],
    req: EngineeringRequirements
) -> BottleneckAnalysis:
    """
    Analyzes why NO grade passed hard constraints.
    Pinpoints conflicting requirements and lists the closest candidates with their specific deficiencies.
    """
    failure_counts = {}
    candidate_deficiencies = []

    for g in all_grades:
        check = evaluate_hard_constraints(g, req)
        if not check.passed:
            for r in check.failed_reasons:
                key = r.split(":")[0] if ":" in r else r[:40]
                failure_counts[key] = failure_counts.get(key, 0) + 1
            
            # Record candidates failing the fewest constraints (closest candidates)
            candidate_deficiencies.append({
                "grade_name": g.grade_name,
                "family": g.family,
                "failed_count": len(check.failed_reasons),
                "failed_reasons": check.failed_reasons
            })

    candidate_deficiencies.sort(key=lambda x: x["failed_count"])
    closest = candidate_deficiencies[:5]

    # Formulate relaxation suggestions
    conflicts = sorted(failure_counts.keys(), key=lambda k: failure_counts[k], reverse=True)
    suggestions = []
    if req.non_magnetic_mandatory and req.min_yield_strength_mpa and req.min_yield_strength_mpa > 350:
        suggestions.append(
            "Conflict: 'Non-Magnetic Mandatory' eliminates all Duplex and Martensitic grades, but high yield strength (>350 MPa) is difficult for standard annealed austenitics. Consider cold-worked temper 301LN, 304*, or lean duplex if mild magnetism can be tolerated."
        )
    if req.min_pren and req.min_pren > 30 and req.max_budget_cost_index and req.max_budget_cost_index < 6.0:
        suggestions.append(
            "Conflict: High PREN (>30) requires Molybdenum alloying, which increases cost beyond the budget ceiling. Consider lean duplex J-2101 or stabilized ferritic J-444."
        )
    if req.max_service_temp_c and req.max_service_temp_c > 350 and any("duplex" in f.lower() for f in req.allowed_microstructures):
        suggestions.append(
            "Conflict: Service temperature exceeds 300°C where duplex steels suffer 475°C embrittlement. Relax microstructure restriction to include high-temperature austenitic grades (e.g. 309S, 310S, EN 1.4828)."
        )

    if not suggestions:
        suggestions.append("Consider relaxing the top failing constraints: " + "; ".join(conflicts[:2]))

    return BottleneckAnalysis(
        is_bottleneck=True,
        conflicting_constraints=conflicts[:4],
        closest_candidates=closest,
        relaxation_suggestions=suggestions
    )
