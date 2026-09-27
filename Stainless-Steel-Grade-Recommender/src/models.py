"""Data models and schemas for Stainless Steel Grade Recommender"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class ChemicalComposition(BaseModel):
    C_max: Optional[float] = None
    C_min: Optional[float] = None
    Mn_min: Optional[float] = None
    Mn_max: Optional[float] = None
    P_max: Optional[float] = None
    S_max: Optional[float] = None
    Si_min: Optional[float] = None
    Si_max: Optional[float] = None
    Cr_min: Optional[float] = None
    Cr_max: Optional[float] = None
    Ni_min: Optional[float] = None
    Ni_max: Optional[float] = None
    Mo_min: Optional[float] = None
    Mo_max: Optional[float] = None
    N_min: Optional[float] = None
    N_max: Optional[float] = None
    Cu_min: Optional[float] = None
    Cu_max: Optional[float] = None
    Ti_min: Optional[float] = None
    Ti_max: Optional[float] = None
    Nb_min: Optional[float] = None
    Nb_max: Optional[float] = None
    W_min: Optional[float] = None
    W_max: Optional[float] = None
    V_min: Optional[float] = None
    V_max: Optional[float] = None
    Ce_min: Optional[float] = None
    Ce_max: Optional[float] = None


class MechanicalProperties(BaseModel):
    yield_strength_min_mpa: float = Field(..., description="Minimum 0.2% Proof Stress / Yield Strength in MPa")
    tensile_strength_min_mpa: float = Field(..., description="Minimum Ultimate Tensile Strength in MPa")
    elongation_min_pct: float = Field(..., description="Minimum percentage elongation at fracture")
    hardness_max: str = Field(..., description="Maximum hardness string (HRB, HRC, or BHN)")
    hardness_hrb_val: float = Field(90.0, description="Normalized HRB numerical value")
    modulus_of_elasticity_gpa: float = Field(200.0, description="Young's Modulus in GPa")


class PhysicalProperties(BaseModel):
    density_kg_m3: float = Field(7800.0, description="Density in kg/m3")
    thermal_conductivity_w_mk: float = Field(15.0, description="Thermal conductivity in W/m.K")
    thermal_expansion_coeff_um_m_c: float = Field(16.0, description="Coefficient of thermal expansion in µm/m/°C")
    electrical_resistivity_uohm_m: float = Field(0.72, description="Electrical resistivity in µΩ.m")


class CorrosionProperties(BaseModel):
    pren: float = Field(..., description="Pitting Resistance Equivalent Number")
    cpt_c: Optional[float] = Field(None, description="Critical Pitting Temperature in °C per ASTM G150")
    cct_c: Optional[float] = Field(None, description="Critical Crevice Temperature in °C per ASTM G48")
    general_corrosion_score: float = Field(7.0, description="Scale 1-10 of general acid/media resistance")
    pitting_resistance_score: float = Field(7.0, description="Scale 1-10 of localized pitting resistance")
    chloride_suitability: str = ""
    scc_resistance: str = ""
    sensitization_resistance: str = ""


class TemperatureCapability(BaseModel):
    min_service_temp_c: float = Field(-196.0, description="Minimum safe service temperature in °C")
    max_continuous_temp_c: float = Field(800.0, description="Maximum continuous operating temperature in °C")
    intermittent_service_temp_c: float = Field(850.0, description="Maximum intermittent service temperature in °C")
    scaling_temperature_c: float = Field(850.0, description="Destructive scaling temperature in °C")


class ManufacturingProperties(BaseModel):
    formability_score: float = Field(8.0, description="Scale 1-10 of cold formability / drawability")
    deep_drawability_ldr: Optional[float] = Field(None, description="Limit Drawing Ratio (LDR)")
    erichsen_cupping_mm: Optional[float] = Field(None, description="Erichsen cupping value in mm")
    weldability_score: float = Field(8.5, description="Scale 1-10 of weldability")
    machinability_score: float = Field(6.0, description="Scale 1-10 of machinability")
    recommended_welding: str = ""


class CommercialProperties(BaseModel):
    relative_cost_index: float = Field(5.0, description="Relative cost index 1 (lowest) to 10 (highest)")
    cost_band: str = "Moderate"
    market_availability: str = "High"


class GradeRecord(BaseModel):
    grade_name: str
    aliases: List[str] = Field(default_factory=list)
    family: str
    microstructure: str
    magnetic_behavior: str
    magnetic_permeability_relative: float = 1.02
    composition: ChemicalComposition
    mechanical_properties: MechanicalProperties
    physical_properties: PhysicalProperties
    corrosion_properties: CorrosionProperties
    temperature_capability: TemperatureCapability
    manufacturing_properties: ManufacturingProperties
    commercial: CommercialProperties
    typical_applications: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    standards: List[str] = Field(default_factory=list)
    equivalent_aisi: str = Field("", description="Equivalent AISI / ASTM grade designation")
    equivalent_bis: str = Field("", description="Equivalent Bureau of Indian Standards (IS 6911) grade designation")
    equivalent_en: str = Field("", description="Equivalent European EN / DIN specification")
    equivalent_uns: str = Field("", description="Unified Numbering System (UNS) designation")
    equivalent_jis: str = Field("", description="Japanese Industrial Standard (JIS) designation")
    source_reference: str
    confidence: str = "Verified (JSL Technical Datasheet)"


# ----------------------------------------------------------------------
# User Requirements Schemas
# ----------------------------------------------------------------------

class FabricatorRequirements(BaseModel):
    """Mode 1: Non-technical fabricator / procurement inputs"""
    application: str = "Food equipment"
    environment: str = "Indoor/dry"
    service_temperature: str = "0–100°C"
    corrosion_importance: str = "Medium"
    strength_importance: str = "Medium"
    non_magnetic: str = "Not important"
    formability_importance: str = "Medium"
    cost_importance: str = "Balanced"
    manufacturing_process: str = "Sheet forming"
    production_scale: str = "Medium production"
    custom_notes: Optional[str] = ""


class EngineeringRequirements(BaseModel):
    """Mode 2: Advanced metallurgical & engineering inputs"""
    # Hard numerical constraints
    min_yield_strength_mpa: Optional[float] = None
    min_tensile_strength_mpa: Optional[float] = None
    min_elongation_pct: Optional[float] = None
    max_hardness_hrb: Optional[float] = None
    min_service_temp_c: Optional[float] = None
    max_service_temp_c: Optional[float] = None
    min_pren: Optional[float] = None
    max_budget_cost_index: Optional[float] = None
    
    # Categorical & Boolean Hard Constraints
    non_magnetic_mandatory: bool = False
    max_magnetic_permeability: Optional[float] = None
    weldability_min_score: Optional[float] = None
    formability_min_score: Optional[float] = None
    allowed_microstructures: List[str] = Field(default_factory=list)
    required_product_form: Optional[str] = None
    
    # Alloying limits
    cr_min: Optional[float] = None
    ni_max: Optional[float] = None
    mo_min: Optional[float] = None
    c_max: Optional[float] = None
    
    # Environmental exposure
    environment_type: str = "General Atmospheric"
    chloride_exposure: str = "Low"
    acidic_exposure: Optional[str] = None


class PriorityWeights(BaseModel):
    """User-defined weighted priorities for multi-attribute scoring (sum to 1.0)"""
    corrosion: float = 0.30
    strength: float = 0.25
    cost: float = 0.20
    formability: float = 0.15
    weldability: float = 0.10
    temperature_margin: float = 0.0
    density_efficiency: float = 0.0


# ----------------------------------------------------------------------
# Evaluation & Recommendation Results
# ----------------------------------------------------------------------

class HardConstraintCheck(BaseModel):
    passed: bool
    status: str  # "PASSED", "FAILED", "WARNING"
    failed_reasons: List[str] = Field(default_factory=list)
    warning_reasons: List[str] = Field(default_factory=list)


class GradeScoreBreakdown(BaseModel):
    corrosion_compat: float
    strength_compat: float
    cost_compat: float
    formability_compat: float
    weldability_compat: float
    temperature_compat: float
    final_score: float  # 0.0 - 100.0%


class ScoredCandidate(BaseModel):
    grade: GradeRecord
    score_breakdown: GradeScoreBreakdown
    constraint_check: HardConstraintCheck
    rank: int = 0
    key_strengths: List[str] = Field(default_factory=list)
    key_limitations: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)


class TradeOffComparison(BaseModel):
    primary_grade: str
    alternative_grade: str
    score_difference: float
    corrosion_delta: float
    strength_delta_mpa: float
    cost_delta_index: float
    formability_delta: float
    weldability_delta: float
    advantages_of_primary: List[str] = Field(default_factory=list)
    sacrifices_of_primary: List[str] = Field(default_factory=list)
    summary_text: str = ""


class BottleneckAnalysis(BaseModel):
    is_bottleneck: bool
    conflicting_constraints: List[str] = Field(default_factory=list)
    closest_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    relaxation_suggestions: List[str] = Field(default_factory=list)


class RecommendationPackage(BaseModel):
    mode: str  # "fabricator" or "engineering"
    primary_recommendation: Optional[ScoredCandidate] = None
    top_alternatives: List[ScoredCandidate] = Field(default_factory=list)
    all_eligible_candidates: List[ScoredCandidate] = Field(default_factory=list)
    excluded_candidates: List[ScoredCandidate] = Field(default_factory=list)
    bottleneck_analysis: Optional[BottleneckAnalysis] = None
    trade_offs: List[TradeOffComparison] = Field(default_factory=list)
    assumptions_made: List[str] = Field(default_factory=list)
    applied_weights: Dict[str, float] = Field(default_factory=dict)
    engineering_rationale: str = ""
    decision_disclaimer: str = (
        "This recommendation is an engineering decision-support tool based on supplied inputs, "
        "published Jindal Stainless technical datasheets, ASTM/EN standards, and stated assumptions. "
        "Final material selection for critical components should always be verified with qualified "
        "metallurgical testing and operating stress analysis."
    )
