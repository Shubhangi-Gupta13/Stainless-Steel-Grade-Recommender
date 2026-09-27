"""Report Generator: Produces comprehensive engineering decision-support dossiers"""

from datetime import datetime
from src.models import RecommendationPackage


class ReportGenerator:
    """Formats full technical recommendation package into downloadable markdown document"""

    @classmethod
    def generate_dossier(cls, package: RecommendationPackage) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = []

        lines.append("# 🛡️ STAINLESS STEEL GRADE SELECTION DOSSIER")
        lines.append("### AI-Powered Metallurgical Decision-Support System")
        lines.append(f"**Date Generated**: {timestamp} | **Operating Mode**: {package.mode.upper()}")
        lines.append("---")
        lines.append("")

        if package.primary_recommendation:
            prim = package.primary_recommendation
            p_grd = prim.grade
            p_sc = prim.score_breakdown

            lines.append("## 🏆 PRIMARY RECOMMENDATION")
            lines.append(f"### **Grade: {p_grd.grade_name}** ({p_grd.family})")
            lines.append(f"**AISI / ASTM Equivalent**: `{p_grd.equivalent_aisi or 'N/A'}` | **BIS (IS 6911) Equivalent**: `{p_grd.equivalent_bis or 'N/A'}`")
            lines.append(f"**EN/DIN**: `{p_grd.equivalent_en or 'N/A'}` | **UNS**: `{p_grd.equivalent_uns or 'N/A'}` | **Overall Compatibility Score**: `{p_sc.final_score}%`")
            lines.append("")

            # Technical Summary Table
            lines.append("### Key Technical Properties & Specification")
            lines.append("| Metallurgical Property | Value / Specification | Benchmark Context |")
            lines.append("| :--- | :--- | :--- |")
            lines.append(f"| **Standard Equivalents** | AISI: {p_grd.equivalent_aisi} \| BIS: {p_grd.equivalent_bis} | EN: {p_grd.equivalent_en} \| UNS: {p_grd.equivalent_uns} |")
            lines.append(f"| **Microstructure** | {p_grd.microstructure} | {p_grd.magnetic_behavior} |")
            lines.append(f"| **Yield Strength (0.2% Proof)** | `{p_grd.mechanical_properties.yield_strength_min_mpa} MPa min` | Baseline: 304 is 205 MPa |")
            lines.append(f"| **Tensile Strength (UTS)** | `{p_grd.mechanical_properties.tensile_strength_min_mpa} MPa min` | Elongation: {p_grd.mechanical_properties.elongation_min_pct}% |")
            lines.append(f"| **Pitting Resistance (PREN)** | `{p_grd.corrosion_properties.pren}` | Cr: {p_grd.composition.Cr_min or 0}% - {p_grd.composition.Cr_max or 0}%, Mo: {p_grd.composition.Mo_min or 0}% |")
            if p_grd.corrosion_properties.cpt_c is not None:
                lines.append(f"| **Critical Pitting Temp (CPT)** | `{p_grd.corrosion_properties.cpt_c}°C` | ASTM G150 electrochemical test |")
            lines.append(f"| **Service Temperature Range** | `{p_grd.temperature_capability.min_service_temp_c}°C to {p_grd.temperature_capability.max_continuous_temp_c}°C` | Continuous service capability |")
            lines.append(f"| **Formability & Drawability** | Score: `{p_grd.manufacturing_properties.formability_score}/10` | LDR: {p_grd.manufacturing_properties.deep_drawability_ldr or 'N/A'} |")
            lines.append(f"| **Weldability & Consumables** | Score: `{p_grd.manufacturing_properties.weldability_score}/10` | {p_grd.manufacturing_properties.recommended_welding} |")
            lines.append(f"| **Commercial Cost Index** | `{p_grd.commercial.relative_cost_index}/10` ({p_grd.commercial.cost_band}) | Market availability: {p_grd.commercial.market_availability} |")
            lines.append("")

            lines.append("### Key Advantages & Strengths")
            for st in prim.key_strengths:
                lines.append(f"- ✅ {st}")
            lines.append("")

            lines.append("### Operational Boundaries & Limitations")
            for lim in prim.key_limitations:
                lines.append(f"- ⚠️ {lim}")
            lines.append("")

            # Alternatives
            if package.top_alternatives:
                lines.append("## 🥈 TOP ALTERNATIVE CANDIDATES")
                lines.append("| Rank | Grade | AISI Equivalent | BIS (IS 6911) | Family | Compatibility | YS (MPa) | PREN | Cost | Primary Trade-Off Summary |")
                lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
                for alt in package.top_alternatives:
                    a_g = alt.grade
                    a_sc = alt.score_breakdown
                    to_text = next((t.summary_text for t in package.trade_offs if t.alternative_grade == a_g.grade_name), "Alternative option")
                    lines.append(f"| #{alt.rank} | **{a_g.grade_name}** | {a_g.equivalent_aisi} | {a_g.equivalent_bis} | {a_g.family} | `{a_sc.final_score}%` | {a_g.mechanical_properties.yield_strength_min_mpa} | {a_g.corrosion_properties.pren} | {a_g.commercial.relative_cost_index}/10 | {to_text} |")
                lines.append("")

            # Detailed Trade-Off Analysis
            if package.trade_offs:
                lines.append("## ⚖️ DETAILED TRADE-OFF & SENSITIVITY MATRIX")
                for t in package.trade_offs:
                    lines.append(f"### {package.primary_recommendation.grade.grade_name} vs. {t.alternative_grade} (Score Δ: {t.score_difference}%)")
                    lines.append(f"- **Summary**: {t.summary_text}")
                    if t.advantages_of_primary:
                        lines.append(f"- **Gains by choosing {package.primary_recommendation.grade.grade_name}**: {', '.join(t.advantages_of_primary)}")
                    if t.sacrifices_of_primary:
                        lines.append(f"- **Sacrifices vs {t.alternative_grade}**: {', '.join(t.sacrifices_of_primary)}")
                    lines.append("")

        elif package.bottleneck_analysis:
            b = package.bottleneck_analysis
            lines.append("## ⚠️ BOTTLENECK CONSTRAINT AUDIT")
            lines.append("No single stainless steel grade satisfied all active hard constraints simultaneously.")
            lines.append("")
            lines.append("### Primary Conflicting Constraints")
            for c in b.conflicting_constraints:
                lines.append(f"- ❌ {c}")
            lines.append("")
            lines.append("### Recommended Constraint Relaxations")
            for s in b.relaxation_suggestions:
                lines.append(f"- 💡 {s}")
            lines.append("")

        # Rationale
        lines.append("## 📝 DETAILED ENGINEERING RATIONALE")
        lines.append(package.engineering_rationale)
        lines.append("")

        # Applied Weights & Assumptions
        lines.append("## ⚙️ AUDIT TRAIL & SYSTEM METADATA")
        lines.append(f"**Applied Priority Weights**: {package.applied_weights}")
        if package.assumptions_made:
            lines.append("**System Assumptions Made**:")
            for a in package.assumptions_made:
                lines.append(f"- {a}")
        lines.append("")
        lines.append(f"> **Important Engineering Notice**: {package.decision_disclaimer}")

        return "\n".join(lines)
