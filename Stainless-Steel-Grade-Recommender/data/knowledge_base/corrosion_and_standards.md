# Stainless Steel Corrosion Mechanisms, Standards & Selection Rules

## Corrosion Modes in Stainless Steel

### 1. Pitting & Crevice Corrosion
Pitting occurs when aggressive anions (chiefly chloride ions, $Cl^-$) locally penetrate and destroy the microscopic passive chromium oxide ($Cr_2O_3$) film.
- **Pitting Resistance Equivalent Number (PREN)**:
  $$\text{PREN} = \%Cr + 3.3 \times \%Mo + 16 \times \%N$$
- **Environmental PREN Criteria**:
  - Rural/Urban atmospheric (indoor/dry): $\text{PREN} \ge 16$ (e.g. 430, J4, 201)
  - Coastal marine air ($<5$ km from coast): $\text{PREN} \ge 22$ (e.g. 316L, J216L, J-444, J-2101)
  - Severe coastal splash / brackish water: $\text{PREN} \ge 32$ (e.g. 317LMN, J-2205, J-31803)
  - Seawater immersion & hot brine ($>40^\circ\text{C}$): $\text{PREN} \ge 40$ (e.g. J-32750, J-32760 Super Duplex, 904L)

### 2. Stress Corrosion Cracking (SCC)
SCC requires three simultaneous factors:
1. Susceptible microstructure (standard austenitic 304/316 with 8%–10% Ni are most susceptible).
2. Tensile stress (residual from welding/bending or applied operational loads).
3. Corrosive environment (chlorides above 60°C).
- **Immunity Strategy**:
  - Switch to **Ferritic stainless steels** (e.g., J-444, J-441, J-439, EN 1.4003) — immune to chloride SCC.
  - Switch to **Duplex stainless steels** (e.g., J-2205, J-2101) — dual phase blocks crack propagation.
  - Switch to **High-Nickel Super Austenitic** (e.g., J-904L with 25% Ni).

### 3. Intergranular Corrosion (IGC) / Sensitization
Occurs when carbon precipitates chromium carbides ($Cr_{23}C_6$) at grain boundaries upon exposure between 450°C and 850°C.
- **Standards for Evaluation**:
  - ASTM A262 Practice A: Oxalic Acid Etch Test (Screening)
  - ASTM A262 Practice B: Boiling Ferric Sulfate–Sulfuric Acid
  - ASTM A262 Practice C: Boiling 65% Nitric Acid (Huey Test)
  - ASTM A262 Practice E: Copper–Copper Sulfate–16% Sulfuric Acid (Detects susceptibility to IGC)
- **Prevention**: Use "L" grades ($C \le 0.030\%$) or stabilized grades with Ti (321, 409L, 439) or Nb (347, 441, 444).

---

## Hard Constraints vs. User Priorities in Material Selection

### Hard Constraints (Go / No-Go Eligibility)
A grade **fails** if it violates any essential constraint:
1. **Service Temperature**: Operating temperature must be within $[\text{Min Temp}, \text{Max Continuous Temp}]$.
2. **Yield Strength**: Grade must achieve $YS_{\text{min}} \ge YS_{\text{required}}$.
3. **Tensile Strength**: Grade must achieve $UTS_{\text{min}} \ge UTS_{\text{required}}$.
4. **Mandatory Non-Magnetic**: If non-magnetic behavior is mandatory, any ferromagnetic grade (Ferritic, Martensitic, Duplex) is eliminated ($\mu_r \gg 1$).
5. **Weldability Threshold**: If extensive field welding without post-weld heat treatment is mandatory, untempered martensitic grades are eliminated.
6. **Chemical / Composition Limits**: User-specified element ranges (e.g., $Mo \ge 2.0\%$, $Ni \le 1.0\%$).

### User Priorities (Weighted Optimization)
Used to rank all acceptable grades using a normalized multi-attribute utility model:
$$\text{Compatibility Score} = \sum_{i} \left( w_i \times C_i \right) \quad \text{where } \sum w_i = 1.0$$
Attributes:
- Corrosion compatibility ($C_{\text{corr}}$)
- Strength compatibility ($C_{\text{strength}}$)
- Cost compatibility ($C_{\text{cost}}$)
- Formability compatibility ($C_{\text{form}}$)
- Weldability compatibility ($C_{\text{weld}}$)
- Temperature margin compatibility ($C_{\text{temp}}$)
- Weight/Density compatibility ($C_{\text{density}}$)

This ensures that the final recommendation is mathematically transparent and directly reflects the user's engineering priorities.
