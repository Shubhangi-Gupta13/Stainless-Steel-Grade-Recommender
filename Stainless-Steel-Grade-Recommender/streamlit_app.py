"""
Stainless Steel Grade Recommender
AI-Powered Metallurgical Decision-Support System
Architectural reference: Know Your Laws - Agentic AI
Adapted for: Stainless Steel Material Selection & Jindal Stainless Grade Catalog
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List

from src.models import (
    FabricatorRequirements,
    EngineeringRequirements,
    PriorityWeights,
    RecommendationPackage
)
from src.agents.recommendation_agent import RecommendationAgent
from src.agents.tradeoff_agent import TradeOffAgent
from src.knowledge_base import get_knowledge_base
from src.grade_converter import get_grade_converter
from src.report_generator import ReportGenerator

# ----------------------------------------------------------------------
# Page Config & Custom Styling
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Stainless Steel Advisor | AI Material Selection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .hero-recommendation {
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
        color: white !important;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(15,23,42,0.18);
    }
    .hero-recommendation h2, .hero-recommendation h3, .hero-recommendation p {
        color: white !important;
    }
    .badge-pass {
        background-color: #dcfce7;
        color: #15803d;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 2px;
    }
    .badge-fail {
        background-color: #fee2e2;
        color: #b91c1c;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 2px;
    }
    .badge-warn {
        background-color: #fef3c7;
        color: #b45309;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 2px;
    }
    .tradeoff-box {
        background-color: #ffffff;
        border-left: 4px solid #3b82f6;
        padding: 14px 18px;
        margin-bottom: 12px;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Initialize Backend Services
# ----------------------------------------------------------------------
@st.cache_resource
def load_engine():
    return RecommendationAgent(), get_knowledge_base(), get_grade_converter()

rec_agent, kb, converter = load_engine()


# ----------------------------------------------------------------------
# Sidebar Navigation & Information
# ----------------------------------------------------------------------
with st.sidebar:
    st.title("🛡️ Stainless Advisor")
    st.caption("AI-Powered Metallurgy Decision-Support System")
    st.markdown("---")

    selected_nav = st.radio(
        "Navigation",
        [
            "🧭 Recommender System",
            "🔄 Grade Converter (JSL ⇄ AISI ⇄ BIS)",
            "📊 Grade Catalog & Explorer",
            "📖 Metallurgical Knowledge Base"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("### ⚙️ Core Selection Philosophy")
    st.info(
        "**Application** ➔ **Requirements** ➔ **Hard Constraints** ➔ "
        "**Compatibility** ➔ **Weighted Priorities** ➔ "
        "**Recommendation** ➔ **Explanation** ➔ **Trade-offs**"
    )

    st.markdown("### 📚 Database Scope")
    st.markdown(
        f"- **{len(kb.get_all_grades())} Verified Stainless Grades**\n"
        "- Austenitic (300 & 200 Series)\n"
        "- Duplex & Super Duplex\n"
        "- Ferritic & Stabilized Alloys\n"
        "- Martensitic & Tool Steels"
    )


# ----------------------------------------------------------------------
# NAVIGATION 1: RECOMMENDER SYSTEM
# ----------------------------------------------------------------------
if selected_nav == "🧭 Recommender System":
    st.title("🛡️ Stainless Steel Material Advisor")
    st.markdown(
        "An explainable engineering decision-support tool that recommends the most suitable stainless steel grade "
        "based on your application requirements, hard constraints, and weighted priorities."
    )

    # Mode Selector Tabs
    tab_mode1, tab_mode2 = st.tabs([
        "🧑 Mode 1: Fabricator / Quick Selection",
        "🔬 Mode 2: Metallurgist / Engineering Specification"
    ])

    # ------------------------------------------------------------------
    # MODE 1: FABRICATOR / BASIC USER
    # ------------------------------------------------------------------
    with tab_mode1:
        st.subheader("🛠️ Application-Oriented Questionnaire")
        st.markdown(
            "Designed for fabricators, procurement specialists, and engineers without deep metallurgical terminology. "
            "Our internal translation layer automatically converts simple answers into rigorous physical properties."
        )

        col_f1, col_f2 = st.columns(2)

        with col_f1:
            fab_app = st.selectbox(
                "1. What are you making?",
                [
                    "Food equipment",
                    "Kitchen equipment",
                    "Structural component",
                    "Chemical equipment",
                    "Marine/coastal component",
                    "Architectural application",
                    "Heat exchanger",
                    "Pipe/tube",
                    "Automotive component",
                    "Drone/UAV component",
                    "Other"
                ],
                index=0
            )

            fab_env = st.selectbox(
                "2. What environment will the component operate in?",
                [
                    "Indoor/dry",
                    "Outdoor",
                    "Coastal/marine",
                    "High humidity",
                    "Saltwater/chloride exposure",
                    "Chemical environment",
                    "High-temperature environment",
                    "Low-temperature environment",
                    "Unknown"
                ],
                index=0
            )

            fab_temp = st.selectbox(
                "3. What service temperature will it experience?",
                [
                    "Below 0°C",
                    "0–100°C",
                    "100–300°C",
                    "300–500°C",
                    "Above 500°C"
                ],
                index=1
            )

            fab_corr = st.select_slider(
                "4. How important is corrosion resistance?",
                options=["Not important", "Low", "Medium", "High", "Critical"],
                value="Medium"
            )

            fab_str = st.select_slider(
                "5. How important is mechanical strength?",
                options=["Not important", "Low", "Medium", "High", "Critical"],
                value="Medium"
            )

        with col_f2:
            fab_mag = st.radio(
                "6. Does the component need to be non-magnetic?",
                ["Yes", "No", "Not important", "I don't know"],
                index=2,
                horizontal=True
            )

            fab_form = st.select_slider(
                "7. How important is ease of fabrication / formability?",
                options=["Low", "Medium", "High"],
                value="Medium"
            )

            fab_cost = st.selectbox(
                "8. How important is cost?",
                [
                    "Lowest possible cost",
                    "Cost-sensitive",
                    "Balanced",
                    "Performance is more important than cost"
                ],
                index=2
            )

            fab_proc = st.selectbox(
                "9. What manufacturing process will be used?",
                [
                    "Sheet forming",
                    "Rolling",
                    "Welding",
                    "Machining",
                    "Casting",
                    "Tube/pipe fabrication",
                    "Other"
                ],
                index=0
            )

            fab_scale = st.selectbox(
                "10. What is the approximate production scale?",
                [
                    "Prototype/small batch",
                    "Medium production",
                    "Large production"
                ],
                index=1
            )

        fab_submit = st.button("🚀 Recommend Optimal Grade (Fabricator Mode)", type="primary", use_container_width=True)

        if fab_submit:
            fab_input = FabricatorRequirements(
                application=fab_app,
                environment=fab_env,
                service_temperature=fab_temp,
                corrosion_importance=fab_corr,
                strength_importance=fab_str,
                non_magnetic=fab_mag,
                formability_importance=fab_form,
                cost_importance=fab_cost,
                manufacturing_process=fab_proc,
                production_scale=fab_scale
            )
            with st.spinner("Processing requirements through Agentic Pipeline..."):
                package = rec_agent.process_recommendation(fab_input)
                st.session_state["recommendation_package"] = package
                st.session_state["active_eng_req"] = rec_agent.kb.get_all_grades()  # helper
                st.session_state["last_mode"] = "fabricator"

    # ------------------------------------------------------------------
    # MODE 2: METALLURGIST / ENGINEER / SCIENTIST
    # ------------------------------------------------------------------
    with tab_mode2:
        st.subheader("🔬 Precision Engineering Specification")
        st.markdown(
            "Direct control over numerical property thresholds, metallurgy phase constraints, and explicit weighting. "
            "Distinguishes strictly between **Hard Constraints** (Go/No-Go eligibility) and **User Priorities** (weighted ranking)."
        )

        with st.expander("📌 Section A: Hard Constraints (Mandatory Go / No-Go Eligibility)", expanded=True):
            col_e1, col_e2, col_e3 = st.columns(3)

            with col_e1:
                e_min_ys = st.number_input("Minimum Yield Strength Rp0.2 (MPa)", min_value=0.0, max_value=850.0, value=0.0, step=25.0)
                e_min_uts = st.number_input("Minimum Tensile Strength Rm (MPa)", min_value=0.0, max_value=1000.0, value=0.0, step=25.0)
                e_min_el = st.number_input("Minimum Elongation A50mm (%)", min_value=0.0, max_value=60.0, value=0.0, step=5.0)

            with col_e2:
                e_min_pren = st.number_input("Minimum Pitting Resistance (PREN)", min_value=0.0, max_value=50.0, value=0.0, step=1.0)
                e_max_cost = st.slider("Maximum Budget Ceiling (Cost Index 1-10)", min_value=3.5, max_value=10.0, value=10.0, step=0.5)
                e_non_mag = st.checkbox("Non-Magnetic Mandatory (Eliminate Ferritic, Duplex, Martensitic)", value=False)

            with col_e3:
                e_min_temp = st.number_input("Min Operating Temperature (°C)", min_value=-269.0, max_value=50.0, value=-40.0, step=10.0)
                e_max_temp = st.number_input("Max Operating Temperature (°C)", min_value=0.0, max_value=1200.0, value=300.0, step=50.0)
                e_min_weld = st.slider("Minimum Weldability Score (1-10)", min_value=1.0, max_value=10.0, value=5.0, step=0.5)

            col_fam, col_elem = st.columns(2)
            with col_fam:
                e_allowed_fam = st.multiselect(
                    "Allowed Microstructural Families (Leave blank for all)",
                    ["Austenitic Cr-Ni", "Austenitic Cr-Mn", "Duplex Stainless Steel", "Super Duplex Stainless Steel", "Ferritic Stainless Steel", "Martensitic Stainless Steel"],
                    default=[]
                )
            with col_elem:
                e_mo_min = st.number_input("Minimum Molybdenum % (e.g., 2.0% for Mo-bearing)", min_value=0.0, max_value=5.0, value=0.0, step=0.5)

        with st.expander("⚖️ Section B: User Priority Weights (Weighted Optimization Model)", expanded=True):
            st.markdown("Set relative importance weights for candidate ranking. The system normalizes these automatically.")
            col_w1, col_w2, col_w3 = st.columns(3)
            with col_w1:
                w_corr = st.slider("Corrosion Resistance Weight", 0, 100, 40)
                w_str = st.slider("Mechanical Strength Weight", 0, 100, 25)
            with col_w2:
                w_cost = st.slider("Cost Efficiency Weight", 0, 100, 15)
                w_form = st.slider("Formability / Drawability Weight", 0, 100, 10)
            with col_w3:
                w_weld = st.slider("Weldability Weight", 0, 100, 10)
                w_temp = st.slider("Temperature Margin Weight", 0, 100, 0)

            total_raw_w = w_corr + w_str + w_cost + w_form + w_weld + w_temp
            st.caption(f"Current Normalized Distribution: Corrosion: {round(w_corr/total_raw_w*100)}% | Strength: {round(w_str/total_raw_w*100)}% | Cost: {round(w_cost/total_raw_w*100)}% | Formability: {round(w_form/total_raw_w*100)}% | Weld: {round(w_weld/total_raw_w*100)}%")

        eng_submit = st.button("🔬 Run Metallurgical Selection Engine (Engineering Mode)", type="primary", use_container_width=True)

        if eng_submit:
            eng_input = EngineeringRequirements(
                min_yield_strength_mpa=e_min_ys if e_min_ys > 0 else None,
                min_tensile_strength_mpa=e_min_uts if e_min_uts > 0 else None,
                min_elongation_pct=e_min_el if e_min_el > 0 else None,
                min_pren=e_min_pren if e_min_pren > 0 else None,
                max_budget_cost_index=e_max_cost if e_max_cost < 10.0 else None,
                non_magnetic_mandatory=e_non_mag,
                min_service_temp_c=e_min_temp,
                max_service_temp_c=e_max_temp,
                weldability_min_score=e_min_weld if e_min_weld > 1.0 else None,
                allowed_microstructures=e_allowed_fam,
                mo_min=e_mo_min if e_mo_min > 0 else None
            )
            norm_weights = PriorityWeights(
                corrosion=w_corr / total_raw_w,
                strength=w_str / total_raw_w,
                cost=w_cost / total_raw_w,
                formability=w_form / total_raw_w,
                weldability=w_weld / total_raw_w,
                temperature_margin=w_temp / total_raw_w
            )
            with st.spinner("Executing Deterministic Constraint Audit & Compatibility Scoring..."):
                package = rec_agent.process_recommendation(eng_input, custom_weights=norm_weights)
                st.session_state["recommendation_package"] = package
                st.session_state["last_mode"] = "engineering"
                st.session_state["active_eng_input"] = eng_input

    # ------------------------------------------------------------------
    # DISPLAY RECOMMENDATION RESULTS
    # ------------------------------------------------------------------
    if "recommendation_package" in st.session_state:
        pkg: RecommendationPackage = st.session_state["recommendation_package"]
        st.markdown("---")

        # Scenario A: Bottleneck Conflict (No grade satisfies all constraints)
        if not pkg.primary_recommendation and pkg.bottleneck_analysis:
            b = pkg.bottleneck_analysis
            st.error("### ⚠️ No Grade in the Database Satisfies All Specified Constraints")
            st.markdown(
                "Our system does not force an invalid recommendation. Instead, the constraint engine has isolated "
                "the mutually conflicting parameters preventing grade eligibility:"
            )

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.markdown("#### ❌ Conflicting Constraints")
                for c in b.conflicting_constraints:
                    st.markdown(f"- **{c}**")

            with col_b2:
                st.markdown("#### 💡 Relaxation Suggestions")
                for s in b.relaxation_suggestions:
                    st.markdown(f"- {s}")

            st.markdown("#### 🔍 Closest Candidates & Specific Deficiencies")
            closest_df = pd.DataFrame([
                {
                    "Grade": item["grade_name"],
                    "Family": item["family"],
                    "Violations Count": item["failed_count"],
                    "First Failure Reason": item["failed_reasons"][0] if item["failed_reasons"] else "N/A"
                }
                for item in b.closest_candidates
            ])
            st.dataframe(closest_df, use_container_width=True)

        # Scenario B: Valid Recommendations Found
        elif pkg.primary_recommendation:
            prim = pkg.primary_recommendation
            p_grd = prim.grade
            p_sc = prim.score_breakdown

            # HERO CARD
            st.markdown(
                f"""
                <div class="hero-recommendation">
                    <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Primary Recommendation</span>
                    <h1 style="color: white; margin-top: 8px; margin-bottom: 4px;">{p_grd.grade_name} <span style="font-size: 1.6rem; opacity: 0.9;">({p_grd.family})</span></h1>
                    <h3 style="color: #93c5fd; margin-top: 0;">Overall Weighted Compatibility: <strong>{p_sc.final_score}%</strong></h3>
                    <p style="font-size: 1.05rem; line-height: 1.5; color: #e2e8f0;">
                        {p_grd.corrosion_properties.chloride_suitability}. Verified Yield Strength of <strong>{p_grd.mechanical_properties.yield_strength_min_mpa} MPa</strong>, PREN of <strong>{p_grd.corrosion_properties.pren}</strong>, and continuous temperature capability up to <strong>{p_grd.temperature_capability.max_continuous_temp_c}°C</strong>.
                    </p>
                    <div style="margin-top: 12px;">
                        <span class="badge-pass">✔ All Hard Constraints Passed</span>
                        <span class="badge-pass">✔ {p_grd.magnetic_behavior}</span>
                        <span class="badge-pass">✔ Cost Index: {p_grd.commercial.relative_cost_index}/10</span>
                        <span class="badge-pass">🇺🇸 AISI: {p_grd.equivalent_aisi or 'Proprietary'}</span>
                        <span class="badge-pass">🇮🇳 BIS: {p_grd.equivalent_bis or 'IS 6911 Special'}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Quick Metric Columns
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Yield Strength (Rp0.2)", f"{p_grd.mechanical_properties.yield_strength_min_mpa} MPa", help="Minimum proof stress")
            m2.metric("Pitting PREN", f"{p_grd.corrosion_properties.pren}", help="%Cr + 3.3%Mo + 16%N")
            m3.metric("Critical Pitting Temp", f"{p_grd.corrosion_properties.cpt_c}°C" if p_grd.corrosion_properties.cpt_c is not None else "N/A", help="ASTM G150 CPT")
            m4.metric("Ductility (A50mm)", f"{p_grd.mechanical_properties.elongation_min_pct}%", help="Elongation at break")
            m5.metric("Relative Cost Index", f"{p_grd.commercial.relative_cost_index}/10", help="Commercial relative pricing scale")

            st.markdown("### 🏆 Top 5 Ranked Material Candidates")
            top_candidates = [prim] + pkg.top_alternatives
            ranking_data = []
            for c in top_candidates:
                g = c.grade
                ranking_data.append({
                    "Rank": f"#{c.rank}",
                    "Grade Name": g.grade_name,
                    "AISI Equivalent": g.equivalent_aisi or "-",
                    "BIS (IS 6911)": g.equivalent_bis or "-",
                    "Microstructural Family": g.family,
                    "Compatibility Score": f"{c.score_breakdown.final_score}%",
                    "YS (MPa)": g.mechanical_properties.yield_strength_min_mpa,
                    "UTS (MPa)": g.mechanical_properties.tensile_strength_min_mpa,
                    "Elongation (%)": f"{g.mechanical_properties.elongation_min_pct}%",
                    "PREN": g.corrosion_properties.pren,
                    "Cost Index": f"{g.commercial.relative_cost_index}/10",
                    "Magnetic": "Non-Mag" if "non-magnetic" in g.magnetic_behavior.lower() else "Magnetic",
                    "Key Advantage": c.key_strengths[0] if c.key_strengths else "Balanced performance"
                })
            st.dataframe(pd.DataFrame(ranking_data), use_container_width=True, hide_index=True)

            # Visual Radar Chart & Sensitivity Analysis
            col_chart, col_sens = st.columns([1.1, 0.9])

            with col_chart:
                st.markdown("#### 🕸️ Multi-Property Comparison (Plotly Radar)")
                categories = ["Corrosion", "Strength", "Cost<br>Efficiency", "Formability", "Weldability"]
                fig_radar = go.Figure()

                colors = ["#1e3a8a", "#0284c7", "#10b981", "#f59e0b", "#8b5cf6"]
                for i, cand in enumerate(top_candidates[:4]):
                    bd = cand.score_breakdown
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[
                            bd.corrosion_compat * 100,
                            bd.strength_compat * 100,
                            bd.cost_compat * 100,
                            bd.formability_compat * 100,
                            bd.weldability_compat * 100
                        ],
                        theta=categories,
                        fill='toself' if i == 0 else None,
                        name=f"{cand.grade.grade_name} ({bd.final_score}%)",
                        line=dict(color=colors[i % len(colors)], width=3 if i == 0 else 1.5)
                    ))

                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    margin=dict(l=70, r=40, t=30, b=30),
                    height=380
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            with col_sens:
                st.markdown("#### 🎛️ Interactive \"What-If?\" Priority Simulator")
                st.caption("Change priority weights in real time to observe how the material decision dynamically shifts:")

                sim_corr = st.slider("Simulate Corrosion Priority %", 0, 100, int(pkg.applied_weights.get("corrosion", 0.3) * 100), key="sim_corr")
                sim_str = st.slider("Simulate Strength Priority %", 0, 100, int(pkg.applied_weights.get("strength", 0.25) * 100), key="sim_str")
                sim_cost = st.slider("Simulate Cost Priority %", 0, 100, int(pkg.applied_weights.get("cost", 0.2) * 100), key="sim_cost")

                sim_total = sim_corr + sim_str + sim_cost + 1e-5
                sim_weights = PriorityWeights(
                    corrosion=sim_corr / sim_total * 0.7,
                    strength=sim_str / sim_total * 0.7,
                    cost=sim_cost / sim_total * 0.7,
                    formability=0.15,
                    weldability=0.15
                )

                # Re-simulate scores on the fly!
                active_eng = st.session_state.get("active_eng_input", EngineeringRequirements())
                sim_results = TradeOffAgent.simulate_what_if(top_candidates, active_eng, sim_weights)

                st.markdown("**Simulated Ranking Under New Priorities:**")
                for name, score, rank in sim_results[:4]:
                    rank_icon = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else "4️⃣"))
                    st.markdown(f"{rank_icon} **{name}** — Score: `{score}%` (Rank #{rank})")

            # Trade-Off Breakdown Section
            st.markdown("### ⚖️ Explicit Trade-Off Analysis (What You Gain vs. Sacrifice)")
            for t in pkg.trade_offs[:3]:
                st.markdown(
                    f"""
                    <div class="tradeoff-box">
                        <h4 style="margin-top: 0; color: #1e3a8a;">{prim.grade.grade_name} vs. {t.alternative_grade} (Score Difference: +{t.score_difference}%)</h4>
                        <p style="margin-bottom: 6px;"><em>{t.summary_text}</em></p>
                        <div style="font-size: 0.95rem;">
                            <strong>✅ Advantages Gained with {prim.grade.grade_name}:</strong> {', '.join(t.advantages_of_primary) if t.advantages_of_primary else 'Balanced compatibility across all categories'}<br>
                            <strong>⚠️ Sacrifices / Disadvantages vs {t.alternative_grade}:</strong> {', '.join(t.sacrifices_of_primary) if t.sacrifices_of_primary else 'None significant'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Detailed Engineering Rationale
            st.markdown("### 📝 Explainable Engineering Rationale")
            st.markdown(pkg.engineering_rationale)

            # Expandable Full Metallurgical Dossier
            with st.expander(f"🔬 Deep Metallurgical Datasheet: {prim.grade.grade_name}", expanded=False):
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown("#### Chemical Composition (% wt)")
                    comp_dict = {k.replace('_', ' '): v for k, v in prim.grade.composition.dict().items() if v is not None and v > 0}
                    st.table(pd.DataFrame(list(comp_dict.items()), columns=["Element", "Specification Value"]))

                with col_m2:
                    st.markdown("#### Physical & Mechanical Properties")
                    phys_dict = {
                        "Yield Strength (MPa)": prim.grade.mechanical_properties.yield_strength_min_mpa,
                        "Tensile Strength (MPa)": prim.grade.mechanical_properties.tensile_strength_min_mpa,
                        "Elongation (%)": prim.grade.mechanical_properties.elongation_min_pct,
                        "Hardness Max": prim.grade.mechanical_properties.hardness_max,
                        "Density (kg/m3)": prim.grade.physical_properties.density_kg_m3,
                        "Thermal Conductivity (W/m.K)": prim.grade.physical_properties.thermal_conductivity_w_mk,
                        "Thermal Expansion (µm/m/°C)": prim.grade.physical_properties.thermal_expansion_coeff_um_m_c,
                        "Electrical Resistivity (µΩ.m)": prim.grade.physical_properties.electrical_resistivity_uohm_m
                    }
                    st.table(pd.DataFrame(list(phys_dict.items()), columns=["Property", "Value"]))

                st.markdown(f"**Verified Source**: `{prim.grade.source_reference}`")
                st.markdown(f"**Governing Standards**: `{', '.join(prim.grade.standards)}`")

            # Download Decision-Support Dossier
            dossier_content = ReportGenerator.generate_dossier(pkg)
            st.download_button(
                label="📄 Download Full Engineering Selection Dossier (.md)",
                data=dossier_content,
                file_name=f"JSL_Selection_Dossier_{prim.grade.grade_name}.md",
                mime="text/markdown",
                use_container_width=True
            )


# ----------------------------------------------------------------------
# NAVIGATION 2: GRADE CONVERTER (JSL ⇄ AISI ⇄ BIS)
# ----------------------------------------------------------------------
elif selected_nav == "🔄 Grade Converter (JSL ⇄ AISI ⇄ BIS)":
    st.title("🔄 Multi-Standard Stainless Steel Grade Converter")
    st.markdown(
        "Bidirectional cross-reference tool mapping **Jindal Stainless (JSL)** trade names to equivalent international and Indian standards: "
        "**AISI / ASTM**, **BIS (IS 6911)**, **EN / DIN / W.Nr.**, **UNS**, and **JIS**."
    )

    tab_conv1, tab_conv2, tab_conv3 = st.tabs([
        "🔍 Single Grade Translator & Datasheet",
        "📋 Full Multi-Standard Equivalence Matrix",
        "🇮🇳 BIS (IS 6911) Nomenclature & Standard Guide"
    ])

    # ------------------------------------------------------------------
    # TAB 1: SINGLE GRADE TRANSLATOR
    # ------------------------------------------------------------------
    with tab_conv1:
        st.subheader("⚡ Search & Translate Any Grade Designation")
        st.markdown(
            "Enter any brand name, AISI number, BIS code, or EN standard (e.g. `J-304`, `316L`, `04Cr18Ni10`, "
            "`J-204Cu`, `N2`, `J4`, `N1`, `J-2205`, `02Cr22Ni5Mo3N`, `409L`, `1.4301`)."
        )

        col_q1, col_q2 = st.columns([1.2, 1.0])
        with col_q1:
            query_input = st.text_input("Type any grade query or standard:", value="", placeholder="e.g. 304, J-316L, 04Cr18Ni10, 204Cu, N2, 2205...")
        with col_q2:
            all_g = converter.grades
            dropdown_options = ["-- Select from catalog --"] + [
                f"{g.grade_name}  (AISI: {g.equivalent_aisi or 'Proprietary'} | BIS: {g.equivalent_bis or 'N/A'})"
                for g in all_g
            ]
            selected_dropdown = st.selectbox("Or choose from verified JSL catalog:", dropdown_options, index=0)

        # Determine target query
        active_query = ""
        if query_input.strip():
            active_query = query_input.strip()
        elif selected_dropdown != "-- Select from catalog --":
            active_query = selected_dropdown.split(" ")[0].strip()
        else:
            active_query = "J-304"  # Default preview

        res = converter.convert_grade(active_query)

        if not res:
            # Fallback multi-match search
            matches = converter.search_all_matches(active_query)
            if matches:
                st.warning(f"Multiple potential matches found for '{active_query}'. Please choose one:")
                match_choice = st.selectbox("Matching grades:", [m["jsl_name"] for m in matches])
                res = converter.convert_grade(match_choice)
            else:
                st.error(f"❌ No matching stainless steel grade found for '{active_query}'. Try searching by AISI (e.g. '304', '316L'), BIS (e.g. '04Cr18Ni10', 'N2'), or JSL brand (e.g. 'J-204Cu').")

        if res:
            st.markdown("---")
            # Designation Cards in Grid
            st.markdown(f"### 🛡️ Designation Cross-Reference for **{res['jsl_name']}**")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <small style="color: #64748b; font-weight: 700; text-transform: uppercase;">🏭 JSL Trade Name</small>
                        <h2 style="color: #1e3a8a; margin: 4px 0;">{res['jsl_name']}</h2>
                        <span style="font-size: 0.9rem; color: #475569;">Family: <strong>{res['family']}</strong></span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <small style="color: #64748b; font-weight: 700; text-transform: uppercase;">🇺🇸 AISI / ASTM Designation</small>
                        <h2 style="color: #0369a1; margin: 4px 0;">{res['equivalent_aisi']}</h2>
                        <span style="font-size: 0.9rem; color: #475569;">Standard: <strong>ASTM A240 / A480</strong></span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c3:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <small style="color: #64748b; font-weight: 700; text-transform: uppercase;">🇮🇳 BIS (IS 6911) Designation</small>
                        <h2 style="color: #047857; margin: 4px 0;">{res['equivalent_bis']}</h2>
                        <span style="font-size: 0.9rem; color: #475569;">Bureau of Indian Standards</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            c4, c5, c6 = st.columns(3)
            with c4:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <small style="color: #64748b; font-weight: 700; text-transform: uppercase;">🇪🇺 EN / DIN / W.Nr.</small>
                        <h3 style="color: #4338ca; margin: 6px 0;">{res['equivalent_en']}</h3>
                        <span style="font-size: 0.85rem; color: #475569;">European Standard EN 10088-2</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c5:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <small style="color: #64748b; font-weight: 700; text-transform: uppercase;">🌐 UNS (Unified Number)</small>
                        <h3 style="color: #b45309; margin: 6px 0;">{res['equivalent_uns']}</h3>
                        <span style="font-size: 0.85rem; color: #475569;">SAE / ASTM Unified System</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c6:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <small style="color: #64748b; font-weight: 700; text-transform: uppercase;">🇯🇵 JIS Designation</small>
                        <h3 style="color: #be123c; margin: 6px 0;">{res['equivalent_jis']}</h3>
                        <span style="font-size: 0.85rem; color: #475569;">Japanese Industrial Standard</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Details tabs: Properties & Composition
            st.markdown("#### 🔬 Technical Profile & Chemical Composition")
            col_t1, col_t2 = st.columns([1, 1])

            with col_t1:
                st.markdown("**Key Physical & Mechanical Properties**")
                prop_df = pd.DataFrame([
                    {"Property": "Yield Strength (Rp0.2 min)", "Value": f"{res['yield_strength_mpa']} MPa"},
                    {"Property": "Tensile Strength (Rm min)", "Value": f"{res['tensile_strength_mpa']} MPa"},
                    {"Property": "Elongation (A50 min)", "Value": f"{res['elongation_pct']}%"},
                    {"Property": "PREN (Pitting Resistance)", "Value": f"{res['pren']}"},
                    {"Property": "Relative Cost Index", "Value": f"{res['cost_index']}/10"},
                    {"Property": "Magnetic Behavior", "Value": res['magnetic_behavior']},
                    {"Property": "Microstructure", "Value": res['microstructure']}
                ])
                st.table(prop_df)

            with col_t2:
                st.markdown("**Nominal Alloying Composition**")
                st.info(f"**Key Elements**: {res['nominal_composition']}")

                st.markdown("**Typical Industrial Applications**")
                for app in res["typical_applications"]:
                    st.markdown(f"- {app}")

                st.markdown(f"**Governing Standards**: `{', '.join(res['standards'])}`")
                st.caption(f"Datasheet Source: {res['source_reference']}")

    # ------------------------------------------------------------------
    # TAB 2: FULL MULTI-STANDARD MATRIX
    # ------------------------------------------------------------------
    with tab_conv2:
        st.subheader("📋 Master Stainless Steel Equivalence Matrix")
        st.markdown("Explore and download the complete cross-reference matrix connecting all 56 verified JSL grades with their international equivalents.")

        col_f_fam, col_f_search = st.columns([1, 2])
        with col_f_fam:
            fam_opts = ["All", "Austenitic (300 Series)", "Austenitic (200 Series)", "Duplex", "Ferritic", "Martensitic"]
            sel_matrix_fam = st.selectbox("Filter Matrix by Microstructural Family:", fam_opts, index=0)

        df_matrix = converter.get_conversion_dataframe(family_filter=sel_matrix_fam)
        st.dataframe(df_matrix, use_container_width=True, hide_index=True)

        csv_data = df_matrix.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Equivalence Matrix as CSV",
            data=csv_data,
            file_name=f"JSL_Stainless_Equivalence_Matrix_{sel_matrix_fam}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # ------------------------------------------------------------------
    # TAB 3: BIS (IS 6911) NOMENCLATURE & METALLURGY GUIDE
    # ------------------------------------------------------------------
    with tab_conv3:
        st.subheader("🇮🇳 Understanding BIS (IS 6911) Stainless Steel Designation System")
        st.markdown(
            "The **Bureau of Indian Standards (BIS)** governs stainless steel plate, sheet, and strip under **IS 6911:2017** "
            "(Stainless Steel Plate, Sheet and Strip — Specification). The Indian designation system conveys explicit metallurgical compositions "
            "and standardized series codes:"
        )

        with st.expander("📖 1. Standard Cr-Ni Austenitic Series (e.g. 04Cr18Ni10 for AISI 304)", expanded=True):
            st.markdown(
                """
                In IS 6911, standard austenitic grades are named according to their nominal carbon, chromium, and nickel contents:
                - **`04Cr18Ni10`**: Represents **AISI 304** (max 0.04% C, ~18% Cr, ~10% Ni).
                - **`02Cr18Ni11`**: Represents **AISI 304L** (extra-low carbon, max 0.02% C for intergranular corrosion prevention).
                - **`02Cr17Ni12Mo2`**: Represents **AISI 316L** (low carbon, ~17% Cr, ~12% Ni, and 2-2.5% Molybdenum for chloride resistance).
                - **`07Cr19Ni10`**: Represents high-carbon standard 304 for elevated temperature service.
                """
            )

        with st.expander("📖 2. Cr-Mn Low-Nickel 200 Series (N1, N2, N3 & 201S)", expanded=True):
            st.markdown(
                """
                India is the world leader in Cr-Mn austenitic stainless steels developed to conserve nickel:
                - **`N1` (IS 6911)**: Corresponds to **J4 / JSL U DD** (ultra-deep drawing Cr-Mn-Cu steel with 1% Ni and 1.5% Cu).
                - **`N2` (IS 6911)**: Corresponds to **J-204Cu** (AISI 204Cu / 08Cr16Ni3Mn8Cu2 with ~3% Ni and 2% Cu).
                - **`N3` (IS 6911)**: Corresponds to **JSL AUS** (high-performance 4% Ni austenitic grade).
                - **`201S` (IS 6911)**: Corresponds to **J-201L** (low-carbon 201 grade for structural applications).
                """
            )

        with st.expander("📖 3. Duplex & Super Duplex Stainless Steels (e.g. 02Cr22Ni5Mo3N)", expanded=True):
            st.markdown(
                """
                Duplex stainless steels possess a mixed 50/50 austenite-ferrite matrix:
                - **`02Cr22Ni5Mo3N`**: Official BIS designation for **2205 Duplex (UNS S31803 / S32205 / J-2205)**.
                  Indicates 0.02% C, 22% Cr, 5% Ni, 3% Mo, and Nitrogen alloying.
                - **`02Cr25Ni7Mo4N`**: Official BIS designation for **2507 Super Duplex (UNS S32750 / J-2507)**.
                  PREN ≥ 42, engineered for offshore oil & gas and marine desalination.
                """
            )

        with st.expander("📖 4. Ferritic & Martensitic Grades (e.g. 02Cr12Ti for 409L)", expanded=True):
            st.markdown(
                """
                - **`02Cr12Ti`**: Official BIS designation for **AISI 409L / J-409L** (12% Cr titanium-stabilized ferritic for automotive exhaust).
                - **`04Cr17`**: Official BIS designation for **AISI 430 / J-430** (17% Cr ferritic for indoor architectural panels and kitchenware).
                - **`20Cr13` & `30Cr13`**: Official BIS designations for **AISI 420 / J-420** (martensitic cutlery and blade steels).
                """
            )


# ----------------------------------------------------------------------
# NAVIGATION 3: GRADE CATALOG & EXPLORER
# ----------------------------------------------------------------------
elif selected_nav == "📊 Grade Catalog & Explorer":
    st.title("📊 Stainless Steel Grade Catalog & Visual Explorer")
    st.markdown("Browse all authentic Jindal Stainless Limited (JSL) grades with verified mechanical and corrosion metrics.")

    all_grades = kb.get_all_grades()

    # Filters
    col_sel_fam, col_search = st.columns([1, 1])
    with col_sel_fam:
        fam_filter = st.multiselect(
            "Filter by Family",
            options=sorted(list(set(g.family for g in all_grades))),
            default=[]
        )
    with col_search:
        search_query = st.text_input("🔍 Search Grade Name, AISI, BIS, or Application", "")

    filtered_grades = all_grades
    if fam_filter:
        filtered_grades = [g for g in filtered_grades if g.family in fam_filter]
    if search_query:
        q = search_query.lower()
        filtered_grades = [
            g for g in filtered_grades
            if q in g.grade_name.lower()
            or q in (g.equivalent_aisi or "").lower()
            or q in (g.equivalent_bis or "").lower()
            or any(q in a.lower() for a in g.aliases)
            or any(q in app.lower() for app in g.typical_applications)
        ]

    st.markdown(f"**Showing {len(filtered_grades)} matching grades**")

    # Interactive Scatter Chart: PREN vs CPT
    st.subheader("📈 Pitting Resistance (PREN) vs Critical Pitting Temp (CPT)")
    scatter_data = []
    for g in filtered_grades:
        scatter_data.append({
            "Grade": g.grade_name,
            "Family": g.family,
            "PREN": g.corrosion_properties.pren,
            "CPT (°C)": g.corrosion_properties.cpt_c if g.corrosion_properties.cpt_c is not None else -10,
            "Yield Strength (MPa)": g.mechanical_properties.yield_strength_min_mpa,
            "Cost Index": g.commercial.relative_cost_index
        })
    df_scatter = pd.DataFrame(scatter_data)

    fig_scatter = px.scatter(
        df_scatter,
        x="PREN",
        y="CPT (°C)",
        color="Family",
        size="Yield Strength (MPa)",
        hover_name="Grade",
        hover_data=["Cost Index", "Yield Strength (MPa)"],
        title="Pitting Resistance Equivalent Number (PREN) vs Critical Pitting Temperature (°C)",
        height=450
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Master Table
    table_rows = []
    for g in filtered_grades:
        table_rows.append({
            "Grade Name": g.grade_name,
            "AISI / ASTM": g.equivalent_aisi or "-",
            "BIS (IS 6911)": g.equivalent_bis or "-",
            "Family": g.family,
            "Yield Strength (MPa)": g.mechanical_properties.yield_strength_min_mpa,
            "Tensile Strength (MPa)": g.mechanical_properties.tensile_strength_min_mpa,
            "Elongation (%)": g.mechanical_properties.elongation_min_pct,
            "PREN": g.corrosion_properties.pren,
            "Cost Index": g.commercial.relative_cost_index,
            "Magnetic Behavior": g.magnetic_behavior,
            "Max Temp (°C)": g.temperature_capability.max_continuous_temp_c,
            "Primary Applications": ", ".join(g.typical_applications[:2])
        })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True)


# ----------------------------------------------------------------------
# NAVIGATION 4: METALLURGICAL KNOWLEDGE BASE
# ----------------------------------------------------------------------
elif selected_nav == "📖 Metallurgical Knowledge Base":
    st.title("📖 Metallurgical Reference & Technical Datasheets")
    st.markdown("Searchable technical reference corpus containing physical metallurgy principles, corrosion tests, and welding recommendations.")

    docs = kb.knowledge_docs
    doc_titles = sorted(list(set(d["doc_title"] for d in docs)))

    sel_doc = st.selectbox("Select Technical Guide / Article", doc_titles)
    matching_sections = [d for d in docs if d["doc_title"] == sel_doc]

    for sec in matching_sections:
        with st.expander(sec["section_title"], expanded=True):
            st.markdown(sec["text"])
