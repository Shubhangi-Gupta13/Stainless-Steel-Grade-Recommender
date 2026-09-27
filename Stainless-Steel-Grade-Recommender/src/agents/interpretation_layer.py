"""Interpretation Layer: Translates Fabricator (layman) inputs into rigorous engineering parameters and priority weights"""

from typing import Tuple, List, Dict
from src.models import (
    FabricatorRequirements,
    EngineeringRequirements,
    PriorityWeights
)


class InterpretationLayer:
    """Translates layman intent to engineering requirements and tracks assumptions"""

    SCALE_WEIGHT_MAP = {
        "Not important": 0.05,
        "Low": 0.12,
        "Medium": 0.22,
        "High": 0.35,
        "Critical": 0.50
    }

    FORMABILITY_MAP = {
        "Low": 0.10,
        "Medium": 0.20,
        "High": 0.35
    }

    @classmethod
    def interpret(
        cls,
        fab: FabricatorRequirements
    ) -> Tuple[EngineeringRequirements, PriorityWeights, List[str]]:
        """
        Converts FabricatorRequirements into EngineeringRequirements and PriorityWeights.
        Returns (eng_req, weights, assumptions_list).
        """
        assumptions: List[str] = []
        eng_req = EngineeringRequirements()

        # 1. Application-driven requirements & assumptions
        app = fab.application
        if app == "Food equipment":
            eng_req.weldability_min_score = 7.5
            eng_req.environment_type = "Food acids and domestic sanitizing"
            assumptions.append("Food contact application requires non-toxic surface passivation and low elemental leaching.")
        elif app == "Kitchen equipment":
            eng_req.formability_min_score = 7.5
            eng_req.environment_type = "Domestic kitchen media"
            assumptions.append("Kitchen equipment requires high drawability and mirror polishability.")
        elif app == "Structural component":
            eng_req.min_yield_strength_mpa = 250.0
            eng_req.environment_type = "Structural load bearing"
            assumptions.append("Structural component requires minimum 0.2% proof stress ≥ 250 MPa.")
        elif app == "Chemical equipment":
            eng_req.environment_type = "Aggressive chemical media"
            eng_req.chloride_exposure = "High"
            assumptions.append("Chemical processing requires verified acid and intergranular corrosion resistance.")
        elif app == "Marine/coastal component":
            eng_req.environment_type = "Coastal marine environment"
            eng_req.chloride_exposure = "High"
            eng_req.min_pren = 23.0
            assumptions.append("Marine environment requires Molybdenum alloying (PREN ≥ 23.0) to resist chloride pitting.")
        elif app == "Architectural application":
            eng_req.environment_type = "Architectural exterior/interior"
            assumptions.append("Architectural application emphasizes surface polishability and atmospheric corrosion resistance.")
        elif app == "Heat exchanger":
            eng_req.environment_type = "Thermal cycle & fluid flow"
            eng_req.weldability_min_score = 8.0
            assumptions.append("Heat exchanger tubing requires resistance to chloride stress corrosion cracking and good weldability.")
        elif app == "Pipe/tube":
            eng_req.weldability_min_score = 8.5
            assumptions.append("Pipe/tube fabrication requires high weld integrity and uniform wall ductility.")
        elif app == "Automotive component":
            eng_req.environment_type = "Automotive thermal/exhaust or chassis"
            assumptions.append("Automotive components benefit from low thermal expansion and high thermal conductivity.")
        elif app == "Drone/UAV component":
            eng_req.min_yield_strength_mpa = 300.0
            assumptions.append("Drone/UAV components prioritize high strength-to-weight ratio; non-magnetic behavior is critical near navigation magnetometers.")

        # 2. Environment translation
        env = fab.environment
        if env == "Indoor/dry":
            eng_req.chloride_exposure = "Low"
        elif env == "Outdoor":
            eng_req.chloride_exposure = "Medium"
            if not eng_req.min_pren:
                eng_req.min_pren = 17.0
        elif env in ["Coastal/marine", "Saltwater/chloride exposure"]:
            eng_req.chloride_exposure = "High"
            eng_req.min_pren = max(eng_req.min_pren or 0.0, 23.0)
            assumptions.append("Coastal/saltwater exposure activates mandatory PREN threshold ≥ 23.0.")
        elif env == "High humidity":
            eng_req.chloride_exposure = "Medium"
        elif env == "Chemical environment":
            eng_req.chloride_exposure = "High"
            eng_req.min_pren = max(eng_req.min_pren or 0.0, 25.0)
        elif env == "High-temperature environment":
            eng_req.max_service_temp_c = 700.0
            assumptions.append("High-temperature environment activates thermal oxidation resistance checks.")
        elif env == "Low-temperature environment":
            eng_req.min_service_temp_c = -40.0
            assumptions.append("Sub-zero operating temperatures eliminate grades prone to ductile-to-brittle transition (DBTT).")
        elif env == "Unknown":
            eng_req.chloride_exposure = "Low"
            assumptions.append("Environment was specified as 'Unknown'; assumed standard indoor/atmospheric conditions.")

        # 3. Service Temperature Range
        temp_str = fab.service_temperature
        if "Below 0" in temp_str:
            eng_req.min_service_temp_c = -50.0
            eng_req.max_service_temp_c = 40.0
            eng_req.allowed_microstructures = ["Austenitic", "Austenitic Cr-Ni", "Austenitic Cr-Mn"]
            assumptions.append("Cryogenic/Sub-zero service requires FCC austenitic microstructure to prevent brittle fracture.")
        elif "0–100" in temp_str or "0-100" in temp_str:
            eng_req.min_service_temp_c = 0.0
            eng_req.max_service_temp_c = 100.0
        elif "100–300" in temp_str or "100-300" in temp_str:
            eng_req.min_service_temp_c = 20.0
            eng_req.max_service_temp_c = 300.0
        elif "300–500" in temp_str or "300-500" in temp_str:
            eng_req.min_service_temp_c = 20.0
            eng_req.max_service_temp_c = 500.0
            assumptions.append("Service in 300–500°C eliminates duplex steels due to 475°C spinodal decomposition embrittlement.")
        elif "Above 500" in temp_str:
            eng_req.min_service_temp_c = 20.0
            eng_req.max_service_temp_c = 750.0
            assumptions.append("Service above 500°C mandates heat-resistant or stabilized stainless steel grades.")

        # 4. Non-magnetic requirements
        mag = fab.non_magnetic
        if mag == "Yes":
            eng_req.non_magnetic_mandatory = True
            assumptions.append("Mandatory non-magnetic requirement eliminates Ferritic, Martensitic, and Duplex grades.")
        elif mag == "No":
            eng_req.non_magnetic_mandatory = False
        elif mag in ["Not important", "I don't know"]:
            eng_req.non_magnetic_mandatory = False
            if mag == "I don't know":
                assumptions.append("Magnetic behavior specified as 'I don't know'; magnetic behavior treated as non-constraining.")

        # 5. Manufacturing Process
        proc = fab.manufacturing_process
        if proc in ["Sheet forming", "Rolling"]:
            eng_req.formability_min_score = max(eng_req.formability_min_score or 0.0, 7.0)
        elif proc == "Welding":
            eng_req.weldability_min_score = max(eng_req.weldability_min_score or 0.0, 8.0)
            assumptions.append("Heavy welding process prioritizes low-carbon ('L') or stabilized (Ti/Nb) grades to prevent sensitization.")
        elif proc == "Machining":
            assumptions.append("Machining process favors grades with controlled chip formation.")

        # 6. User Priority Weights calculation
        raw_corr_w = cls.SCALE_WEIGHT_MAP.get(fab.corrosion_importance, 0.22)
        raw_str_w = cls.SCALE_WEIGHT_MAP.get(fab.strength_importance, 0.22)
        raw_form_w = cls.FORMABILITY_MAP.get(fab.formability_importance, 0.20)

        # Cost weighting
        cost_str = fab.cost_importance
        if cost_str == "Lowest possible cost":
            raw_cost_w = 0.40
            eng_req.max_budget_cost_index = 5.5
            assumptions.append("Lowest possible cost selected: active budget ceiling of cost index ≤ 5.5 applied.")
        elif cost_str == "Cost-sensitive":
            raw_cost_w = 0.30
            eng_req.max_budget_cost_index = 7.5
        elif cost_str == "Balanced":
            raw_cost_w = 0.20
        elif cost_str == "Performance is more important than cost":
            raw_cost_w = 0.08

        # Weldability weight from process
        raw_weld_w = 0.25 if proc == "Welding" else 0.10

        # Drone adjustment
        if app == "Drone/UAV component":
            raw_str_w = max(raw_str_w, 0.35)

        # Normalize weights so they sum to 1.0
        total_w = raw_corr_w + raw_str_w + raw_cost_w + raw_form_w + raw_weld_w
        weights = PriorityWeights(
            corrosion=round(raw_corr_w / total_w, 3),
            strength=round(raw_str_w / total_w, 3),
            cost=round(raw_cost_w / total_w, 3),
            formability=round(raw_form_w / total_w, 3),
            weldability=round(raw_weld_w / total_w, 3),
            temperature_margin=0.0,
            density_efficiency=0.0
        )

        return eng_req, weights, assumptions
