# Duplex & Super Duplex Stainless Steels - Technical Reference & Engineering Datasheets

## Overview & Metallurgy
Duplex stainless steels feature a dual-phase microstructure consisting of approximately equal proportions of austenite (FCC) and ferrite (BCC) (typically 40%–60% of each phase). This balanced dual-phase morphology combines the beneficial properties of both austenitic and ferritic steels:
1. **High Mechanical Strength**: Yield strength is typically 2× that of conventional austenitic stainless steels (400–550 MPa minimum YS compared to 170–205 MPa for 304L/316L).
2. **Stress Corrosion Cracking (SCC) Immunity**: The continuous ferrite matrix and phase boundaries arrest transgranular and intergranular stress corrosion cracks in chloride-containing media.
3. **Pitting & Crevice Corrosion Resistance**: High chromium (21%–26%), molybdenum (up to 5%), and intentional nitrogen alloying (0.10%–0.32%) yield high Pitting Resistance Equivalent Numbers (PREN).
4. **Ferromagnetic Behavior**: Due to ~50% ferrite content, all duplex grades are magnetic in all conditions.

---

## Pitting Resistance Equivalent Number (PREN)
Pitting resistance is quantified using the standard metallurgical correlation:
$$\text{PREN} = \%Cr + 3.3 \times \%Mo + 16 \times \%N$$
For tungsten-bearing super duplex grades (e.g., J-32760 / UNS S32760):
$$\text{PREN}_W = \%Cr + 3.3 \times (\%Mo + 0.5 \times \%W) + 16 \times \%N$$

### PREN Benchmark Values (Jindal Stainless Technical Data):
- **J-2101 (Lean Duplex UNS S32101)**: $\text{PREN} \approx 26.0$ (Comparable to 316L, 2× Yield Strength)
- **J-2304 (Lean Duplex UNS S32304)**: $\text{PREN} \approx 25.0$ (Comparable to 316L, cost-effective replacement)
- **J-31803 (Standard Duplex UNS S31803)**: $\text{PREN} \approx 34.0$ (Critical pitting temperature CPT: 50°C)
- **J-2205 (Standard Duplex UNS S32205)**: $\text{PREN} \approx 35.0$ (Critical pitting temperature CPT: 55°C, CCT: 20°C)
- **J-32750 (Super Duplex UNS S32750)**: $\text{PREN} \approx 42.0$ (Critical pitting temperature CPT: 70°C, CCT: 45°C)
- **J-32760 (Super Duplex UNS S32760)**: $\text{PREN} \ge 42.5$ (Critical pitting temperature CPT: 85°C, CCT: 50°C)

---

## Critical Pitting & Crevice Corrosion Temperatures
As determined by ASTM G150 (CPT) and ASTM G48 Method F (CCT):
- **ASTM 304**: $\text{CPT} = -2^\circ\text{C}$, $\text{CCT} = -5^\circ\text{C}$
- **ASTM 316L**: $\text{CPT} = 20^\circ\text{C}$, $\text{CCT} = -5^\circ\text{C}$
- **J-2101**: $\text{CPT} = 20^\circ\text{C}$, $\text{CCT} = -5^\circ\text{C}$
- **J-2304**: $\text{CPT} = 25^\circ\text{C}$, $\text{CCT} = -5^\circ\text{C}$
- **J-31803**: $\text{CPT} = 50^\circ\text{C}$, $\text{CCT} = 15^\circ\text{C}$
- **J-2205**: $\text{CPT} = 55^\circ\text{C}$, $\text{CCT} = 20^\circ\text{C}$
- **J-32750**: $\text{CPT} = 70^\circ\text{C}$, $\text{CCT} = 45^\circ\text{C}$
- **J-32760**: $\text{CPT} = 85^\circ\text{C}$, $\text{CCT} = 50^\circ\text{C}$

---

## Service Temperature Limitations & Embrittlement Phenomena
> [!WARNING]
> Duplex stainless steels must **NOT** be specified for continuous service above 250°C–300°C. 
> Exposure between 350°C and 550°C causes **475°C embrittlement** (spinodal decomposition of ferrite into chromium-rich $\alpha'$ and iron-rich $\alpha$). 
> Exposure between 600°C and 900°C causes rapid precipitation of intermetallic **sigma ($\sigma$)** and **chi ($\chi$)** phases, causing severe loss of impact toughness and corrosion resistance.

---

## Fabrication & Welding Guidelines
- **Weldability**: Duplex steels have good weldability, but heat input must be controlled between **0.5 and 2.5 kJ/mm** (0.2–1.5 kJ/mm for super duplex) to prevent excessive ferrite in the heat-affected zone (HAZ).
- **Consumables**: Over-alloyed filler metal with elevated nickel is required to maintain austenitic reformation in the weld seam:
  - J-2101: AWS ER2209 or proprietary lean duplex filler
  - J-2205 / J-31803: AWS ER2209 (22% Cr, 9% Ni, 3% Mo, 0.15% N)
  - J-32750 / J-32760: AWS ER2594 (25% Cr, 9% Ni, 4% Mo, 0.25% N, W)
- **Forming**: Higher yield strength (450–550 MPa) requires ~2× forming force compared to 304/316. Springback is greater and must be compensated for during bending.

---

## Applications & JSL References
- **J2101 / J2304**: Storage tanks (palm oil, wine, slurry, water/sewage), civil bridges, sluice gates, water heaters.
- **J2205 / J31803**: Offshore oil & gas topsides, sour gas pipelines, marine cargo chemical tankers, pulp & paper digesters, flue gas desulfurization.
- **J32750 / J32760**: Seawater RO desalination pumps, subsea manifolds, mining autoclave leaching, marine scrubbers.
