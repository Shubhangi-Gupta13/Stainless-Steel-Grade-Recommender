"""
Grade Converter Engine
Translates between Jindal Stainless (JSL) designations, AISI/ASTM, Bureau of Indian Standards (BIS IS 6911),
European (EN/DIN), UNS, and Japanese (JIS) standards.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
from src.knowledge_base import get_knowledge_base
from src.models import GradeRecord


class GradeConverter:
    """Provides bidirectional translation between JSL, AISI, BIS, EN, UNS, and JIS specifications"""

    def __init__(self):
        self.kb = get_knowledge_base()
        self.grades = self.kb.get_all_grades()

    def convert_grade(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Translates a query string (JSL code, AISI number, or BIS designation) into full equivalent standards.
        Returns a rich comparison dictionary if found.
        """
        if not query or not query.strip():
            return None

        clean_q = query.strip().upper()
        # Clean common prefixes / suffixes for flexible matching
        simplified_q = clean_q.replace("J-", "").replace("J", "").replace("AISI", "").replace("SUS", "").replace("IS", "").strip()

        best_match: Optional[GradeRecord] = None

        # 1. Exact match on JSL grade name
        for g in self.grades:
            if g.grade_name.upper() == clean_q or g.grade_name.upper().replace("-", "") == clean_q.replace("-", ""):
                best_match = g
                break

        # 2. Exact match on BIS designation (IS 6911)
        if not best_match:
            for g in self.grades:
                bis_upper = g.equivalent_bis.upper()
                if clean_q in bis_upper or simplified_q == bis_upper.split("(")[0].strip():
                    best_match = g
                    break

        # 3. Match on AISI designation
        if not best_match:
            for g in self.grades:
                aisi_upper = g.equivalent_aisi.upper()
                if clean_q == aisi_upper or simplified_q in aisi_upper:
                    best_match = g
                    break

        # 4. Match on UNS or EN number
        if not best_match:
            for g in self.grades:
                if clean_q in g.equivalent_uns.upper() or clean_q in g.equivalent_en.upper():
                    best_match = g
                    break

        # 5. Match on aliases
        if not best_match:
            for g in self.grades:
                for alias in g.aliases:
                    if clean_q == alias.upper() or simplified_q in alias.upper():
                        best_match = g
                        break
                if best_match:
                    break

        if not best_match:
            return None

        return self._format_grade_conversion(best_match)

    def search_all_matches(self, query: str) -> List[Dict[str, Any]]:
        """Searches across all standards and returns all matching grades"""
        if not query or not query.strip():
            return [self._format_grade_conversion(g) for g in self.grades]

        clean_q = query.strip().upper()
        results = []
        for g in self.grades:
            searchable = (
                f"{g.grade_name} {g.equivalent_aisi} {g.equivalent_bis} "
                f"{g.equivalent_en} {g.equivalent_uns} {g.equivalent_jis} "
                f"{' '.join(g.aliases)} {' '.join(g.typical_applications)}"
            ).upper()

            if clean_q in searchable:
                results.append(self._format_grade_conversion(g))

        return results

    def _format_grade_conversion(self, g: GradeRecord) -> Dict[str, Any]:
        """Formats a GradeRecord into a clean cross-reference conversion dictionary"""
        comp = g.composition
        cr_str = f"{comp.Cr_min or 0}% - {comp.Cr_max or 0}%" if comp.Cr_min else f"≤ {comp.Cr_max}%"
        ni_str = f"{comp.Ni_min or 0}% - {comp.Ni_max or 0}%" if comp.Ni_min else (f"≤ {comp.Ni_max}%" if comp.Ni_max else "-")
        mo_str = f"{comp.Mo_min or 0}% - {comp.Mo_max or 0}%" if comp.Mo_min else (f"≤ {comp.Mo_max}%" if comp.Mo_max else "-")

        return {
            "jsl_name": g.grade_name,
            "equivalent_aisi": g.equivalent_aisi or "N/A",
            "equivalent_bis": g.equivalent_bis or "N/A",
            "equivalent_en": g.equivalent_en or "N/A",
            "equivalent_uns": g.equivalent_uns or "N/A",
            "equivalent_jis": g.equivalent_jis or "N/A",
            "family": g.family,
            "microstructure": g.microstructure,
            "yield_strength_mpa": g.mechanical_properties.yield_strength_min_mpa,
            "tensile_strength_mpa": g.mechanical_properties.tensile_strength_min_mpa,
            "elongation_pct": g.mechanical_properties.elongation_min_pct,
            "pren": g.corrosion_properties.pren,
            "cost_index": g.commercial.relative_cost_index,
            "magnetic_behavior": g.magnetic_behavior,
            "nominal_composition": f"Cr: {cr_str} | Ni: {ni_str} | Mo: {mo_str}",
            "typical_applications": g.typical_applications,
            "standards": g.standards,
            "source_reference": g.source_reference
        }

    def get_conversion_dataframe(self, family_filter: Optional[str] = None) -> pd.DataFrame:
        """Generates a complete multi-standard conversion table as a Pandas DataFrame"""
        rows = []
        for g in self.grades:
            if family_filter and family_filter != "All" and g.family != family_filter:
                continue

            comp = g.composition
            cr = f"{comp.Cr_min or 0}-{comp.Cr_max or 0}%"
            ni = f"{comp.Ni_min or 0}-{comp.Ni_max or 0}%" if comp.Ni_min else f"<{comp.Ni_max or 0}%"
            mo = f"{comp.Mo_min or 0}-{comp.Mo_max or 0}%" if (comp.Mo_min or comp.Mo_max) else "-"

            rows.append({
                "JSL Grade": g.grade_name,
                "AISI / ASTM": g.equivalent_aisi,
                "BIS (IS 6911)": g.equivalent_bis,
                "EN / DIN": g.equivalent_en,
                "UNS No.": g.equivalent_uns,
                "JIS": g.equivalent_jis,
                "Family": g.family,
                "Yield Strength (MPa)": g.mechanical_properties.yield_strength_min_mpa,
                "PREN": g.corrosion_properties.pren,
                "Cr %": cr,
                "Ni %": ni,
                "Mo %": mo,
                "Cost Index": f"{g.commercial.relative_cost_index}/10"
            })

        return pd.DataFrame(rows)


# Singleton instance
_CONVERTER_INSTANCE = None

def get_grade_converter() -> GradeConverter:
    global _CONVERTER_INSTANCE
    if _CONVERTER_INSTANCE is None:
        _CONVERTER_INSTANCE = GradeConverter()
    return _CONVERTER_INSTANCE
