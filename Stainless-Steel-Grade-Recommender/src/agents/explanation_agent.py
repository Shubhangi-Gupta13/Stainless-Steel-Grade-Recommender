"""Explanation Agent: Generates transparent, auditable engineering rationales grounded in retrieved technical facts"""

from typing import List, Dict, Any, Optional
from src.models import (
    ScoredCandidate,
    TradeOffComparison,
    EngineeringRequirements,
    PriorityWeights,
    BottleneckAnalysis
)
from src.config import Config


class ExplanationAgent:
    """Produces explainable decision-support narratives with technical citations"""

    def __init__(self):
        self.llm = Config.get_llm()

    def generate_explanation(
        self,
        mode: str,
        primary: Optional[ScoredCandidate],
        top_alternatives: List[ScoredCandidate],
        trade_offs: List[TradeOffComparison],
        req: EngineeringRequirements,
        weights: PriorityWeights,
        assumptions: List[str],
        retrieved_snippets: List[Dict[str, Any]],
        bottleneck: Optional[BottleneckAnalysis] = None
    ) -> str:
        """
        Generates structured markdown explanation.
        Uses LLM if available; otherwise employs deterministic metallurgical synthesis.
        """
        # If no grade satisfied all constraints
        if not primary or (bottleneck and bottleneck.is_bottleneck):
            return self._generate_bottleneck_explanation(bottleneck, req)

        if self.llm:
            try:
                return self._generate_llm_explanation(
                    mode=mode,
                    primary=primary,
                    top_alternatives=top_alternatives,
                    trade_offs=trade_offs,
                    req=req,
                    weights=weights,
                    assumptions=assumptions,
                    retrieved_snippets=retrieved_snippets
                )
            except Exception as e:
                print(f"LLM explanation generation encountered error: {e}. Falling back to deterministic engine.")

        return self._generate_deterministic_explanation(
            mode=mode,
            primary=primary,
            top_alternatives=top_alternatives,
            trade_offs=trade_offs,
            req=req,
            weights=weights,
            assumptions=assumptions,
            retrieved_snippets=retrieved_snippets
        )

    def _generate_bottleneck_explanation(
        self,
        bottleneck: Optional[BottleneckAnalysis],
        req: EngineeringRequirements
    ) -> str:
        """Generates clear guidance when no candidate satisfies all hard constraints"""
        if not bottleneck:
            return "No grade in the current database satisfies all specified constraints."

        lines = [
            "### ⚠️ Constraint Conflict Detected: No Grade Fully Satisfies All Constraints",
            "",
            "The recommendation engine evaluated all available stainless steel grades against your mandatory hard constraints. "
            "Currently, **no single grade meets 100% of the active requirements**.",
            "",
            "#### Primary Conflicting Constraints:",
        ]
        for c in bottleneck.conflicting_constraints:
            lines.append(f"- **{c}**")

        lines.extend([
            "",
            "#### Closest Candidate Grades & Deficiencies:",
        ])
        for c in bottleneck.closest_candidates:
            lines.append(f"- **{c['grade_name']}** ({c['family']}): Failed {c['failed_count']} constraint(s)")
            for r in c['failed_reasons']:
                lines.append(f"  - ❌ {r}")

        lines.extend([
            "",
            "#### Engineering Recommendations for Constraint Relaxation:",
        ])
        for s in bottleneck.relaxation_suggestions:
            lines.append(f"- 💡 {s}")

        lines.extend([
            "",
            "> **Decision-Support Notice**: Adjust or relax one of the conflicting parameters in the input panel to see viable candidate grades."
        ])
        return "\n".join(lines)

    def _generate_deterministic_explanation(
        self,
        mode: str,
        primary: ScoredCandidate,
        top_alternatives: List[ScoredCandidate],
        trade_offs: List[TradeOffComparison],
        req: EngineeringRequirements,
        weights: PriorityWeights,
        assumptions: List[str],
        retrieved_snippets: List[Dict[str, Any]]
    ) -> str:
        """Rigorous, deterministic template-driven engineering rationale grounded in JSL data"""
        p_grd = primary.grade
        p_sc = primary.score_breakdown

        lines = []

        # 1. Headline summary
        lines.append(f"### Engineering Decision-Support Rationale: **{p_grd.grade_name}** ({primary.score_breakdown.final_score}% Match)")
        lines.append("")
        lines.append(
            f"**{p_grd.grade_name}** ({p_grd.family}, {p_grd.microstructure}) is recommended as the optimal material choice "
            f"for this application based on your specified operating constraints and user priority weights."
        )
        lines.append("")

        # 2. Why this grade was recommended
        lines.append("#### 1. Why Was This Grade Recommended?")
        lines.append(
            f"- **Constraint Satisfaction**: Successfully satisfied all mandatory hard constraints including "
            f"temperature capability ({p_grd.temperature_capability.min_service_temp_c}°C to {p_grd.temperature_capability.max_continuous_temp_c}°C), "
            f"yield strength ({p_grd.mechanical_properties.yield_strength_min_mpa} MPa min), and magnetic requirements ({p_grd.magnetic_behavior})."
        )
        lines.append(
            f"- **Environmental Suitability**: {p_grd.corrosion_properties.chloride_suitability} (PREN {p_grd.corrosion_properties.pren})."
        )
        if p_grd.corrosion_properties.cpt_c is not None:
            lines.append(
                f"- **Verified Critical Pitting Temperature**: CPT = {p_grd.corrosion_properties.cpt_c}°C as per ASTM G150."
            )
        lines.append(
            f"- **Manufacturing Compatibility**: Formability score {p_grd.manufacturing_properties.formability_score}/10 "
            f"and weldability score {p_grd.manufacturing_properties.weldability_score}/10 ({p_grd.manufacturing_properties.recommended_welding})."
        )
        lines.append("")

        # 3. Contributing Properties vs User Priority Weights
        lines.append("#### 2. Property Contribution Analysis & Weight Influence")
        weight_contributions = [
            ("Corrosion Resistance", weights.corrosion, p_sc.corrosion_compat),
            ("Mechanical Strength", weights.strength, p_sc.strength_compat),
            ("Commercial Cost Efficiency", weights.cost, p_sc.cost_compat),
            ("Formability & Ductility", weights.formability, p_sc.formability_compat),
            ("Weldability", weights.weldability, p_sc.weldability_compat)
        ]
        weight_contributions.sort(key=lambda x: x[1] * x[2], reverse=True)

        highest = weight_contributions[0]
        lowest = [x for x in weight_contributions if x[1] > 0][-1] if any(x[1] > 0 for x in weight_contributions) else weight_contributions[-1]

        lines.append(
            f"- **Primary Score Driver**: **{highest[0]}** (weight {round(highest[1]*100)}%) contributed most heavily to the winning compatibility score "
            f"with a normalized property compatibility of {round(highest[2]*100)}%."
        )
        lines.append(
            f"- **Lower Impact Factor**: **{lowest[0]}** (weight {round(lowest[1]*100)}%) had minimal influence on the ranking because of the lower assigned priority weight."
        )
        lines.append("")

        # 4. Key Limitations
        lines.append("#### 3. Known Limitations & Operating Boundaries")
        for lim in p_grd.limitations:
            lines.append(f"- ⚠️ {lim}")
        lines.append("")

        # 5. Major Trade-Offs against Top Alternatives
        lines.append("#### 4. Trade-Off Analysis Against Alternatives")
        if trade_offs:
            for t in trade_offs[:3]:
                lines.append(f"- **Compared to {t.alternative_grade}** (Score: {round(primary.score_breakdown.final_score - t.score_difference, 1)}%):")
                if t.advantages_of_primary:
                    lines.append(f"  - **Advantage gained**: {'; '.join(t.advantages_of_primary)}.")
                if t.sacrifices_of_primary:
                    lines.append(f"  - **Trade-off / Sacrifice**: {'; '.join(t.sacrifices_of_primary)}.")
                if not t.advantages_of_primary and not t.sacrifices_of_primary:
                    lines.append(f"  - {t.summary_text}")
        else:
            lines.append("- No immediate close alternatives met all hard constraints.")
        lines.append("")

        # 6. Assumptions Made
        if assumptions:
            lines.append("#### 5. Stated Engineering Assumptions")
            for a in assumptions:
                lines.append(f"- ℹ️ {a}")
            lines.append("")

        # 7. Citations & References
        lines.append("#### 6. Verified Datasheet References & Standards")
        for cit in primary.citations:
            lines.append(f"- 📄 {cit}")
        for doc in retrieved_snippets[:2]:
            lines.append(f"- 📚 [{doc['doc_title']}: {doc['section_title']}]")

        return "\n".join(lines)

    def _generate_llm_explanation(
        self,
        mode: str,
        primary: ScoredCandidate,
        top_alternatives: List[ScoredCandidate],
        trade_offs: List[TradeOffComparison],
        req: EngineeringRequirements,
        weights: PriorityWeights,
        assumptions: List[str],
        retrieved_snippets: List[Dict[str, Any]]
    ) -> str:
        """Generates contextual explanation via LLM grounded strictly in provided facts"""
        p_grd = primary.grade
        trade_off_text = "\n".join([
            f"- {t.alternative_grade}: {t.summary_text} (Advantage: {', '.join(t.advantages_of_primary)} | Sacrifice: {', '.join(t.sacrifices_of_primary)})"
            for t in trade_offs[:3]
        ])
        snippets_text = "\n\n".join([
            f"[{s['doc_title']} - {s['section_title']}]:\n{s['text'][:400]}"
            for s in retrieved_snippets[:2]
        ])

        system_prompt = (
            "You are an expert metallurgical engineering advisor for Jindal Stainless Limited. "
            "Your task is to write a transparent, rigorous, and explainable material selection report. "
            "Do NOT fabricate material properties. Ground all claims strictly in the provided data. "
            "Ensure the explanation directly answers: 1) Why recommended, 2) Requirements satisfied, "
            "3) Property contributions vs weights, 4) Limitations, 5) Trade-offs vs alternatives, "
            "and 6) Sources cited."
        )

        user_prompt = f"""
PRIMARY RECOMMENDATION:
Grade: {p_grd.grade_name} ({p_grd.family})
Compatibility Score: {primary.score_breakdown.final_score}%
Yield Strength: {p_grd.mechanical_properties.yield_strength_min_mpa} MPa
PREN: {p_grd.corrosion_properties.pren}
CPT: {p_grd.corrosion_properties.cpt_c}°C
Cost Index: {p_grd.commercial.relative_cost_index}/10
Limitations: {', '.join(p_grd.limitations)}
Datasheet Citation: {p_grd.source_reference}

USER PRIORITIES:
Corrosion: {round(weights.corrosion*100)}% | Strength: {round(weights.strength*100)}% | Cost: {round(weights.cost*100)}% | Formability: {round(weights.formability*100)}% | Weldability: {round(weights.weldability*100)}%

ALTERNATIVES & TRADE-OFFS:
{trade_off_text}

ASSUMPTIONS:
{', '.join(assumptions)}

RETRIEVED TECHNICAL KNOWLEDGE:
{snippets_text}

Write an explainable engineering rationale in markdown format. Audience mode: {mode}.
"""
        response = self.llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        return response.content
