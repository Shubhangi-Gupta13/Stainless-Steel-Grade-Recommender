# 🛡️ Jindal Stainless — AI-Powered Stainless Steel Grade Recommender

An explainable, metallurgical decision-support system that recommends the optimal stainless steel grade based on engineering requirements, environmental constraints, and user-defined priority weights.

This application transforms an Agentic Retrieval-Augmented Generation (RAG) framework into a deterministic, auditable engineering advisor for material selection.

---

## 🎯 Core Selection Philosophy

```text
Application ➔ Understand Requirements ➔ Apply Hard Constraints ➔ Calculate Compatibility ➔ Apply Weighted Priorities ➔ Rank Grades ➔ Explain Recommendation ➔ Surface Trade-offs
```

The system is designed as an **engineering decision-support tool**, not an opaque authority. It explicitly surfaces all assumptions, demonstrates why alternatives were ranked lower, highlights what is gained versus sacrificed, and allows real-time interactive "What-If?" sensitivity analysis.

---

## 🏛️ Architectural Adaptation from `Know_Your_Laws`

| Architectural Layer | Know Your Laws Reference | Stainless Steel Grade Recommender |
| :--- | :--- | :--- |
| **Domain Corpus** | Legal statutes (BNSS, IT Act, CP Act) | Jindal Stainless Limited (JSL) Technical Datasheets, ASTM A240, EN 10088, JIS G4305 |
| **Knowledge Representation** | Unstructured PDF pages & FAISS chunks | Structured Grade Database (56 verified grades) + Multi-document Markdown Knowledge Base |
| **Agentic Workflow** | Query Rewriter ➔ Retriever ➔ Evaluator ➔ Corrective Web Search | UI Agent ➔ Interpretation Layer ➔ Constraint Agent ➔ Scoring Engine ➔ Trade-off Agent ➔ Explanation Agent |
| **Decision Logic** | LLM text synthesis | **Deterministic multi-attribute mathematical model** (no hallucinated scores) + LLM RAG explanation |
| **Explainability** | Legal citations (`[BNSS 2023, p. 4]`) | Metallurgical citations (`[JSL Datasheet: J2205 UNS S32205, ASTM G150, PREN 35]`) |
| **User Modes** | Professional vs. Normal | **Mode 1: Fabricator/Basic** vs. **Mode 2: Metallurgist/Scientist** |

---

## 🚀 Two Distinct User Interfaces / Modes

### 🧑 Mode 1: Fabricator / Basic User ("Quick Recommendation")
Intended for fabricators, customers, procurement staff, and non-metallurgists.
- **No Metallurgical Jargon**: Eliminates intimidating terms like PREN, pitting potential, Cr/Ni/Mo ratios, and phase stability.
- **Application-Centric Questions**:
  - *What are you making?* (Food equipment, Kitchenware, Structural components, Chemical tanks, Marine parts, Drone/UAV components, etc.)
  - *Operating Environment?* (Indoor/dry, Coastal/marine, Saltwater splash, High temperature, Unknown)
  - *Service Temperature?* (Below 0°C, 0–100°C, 100–300°C, 300–500°C, Above 500°C)
  - *Qualitative Scales*: Corrosion resistance & Strength (Not important to Critical), Formability (Low/Med/High), Cost (Lowest possible to Performance-driven).
  - *Non-Magnetic Requirement*: Simple Yes / No / Not important / I don't know.
- **Automatic Internal Interpretation**:
  - Translates "Coastal/marine" ➔ Chloride Exposure = High, PREN threshold $\ge 23.0$.
  - Translates "Below 0°C" ➔ Sub-zero toughness constraint, restricts to austenitic FCC lattice.
  - Transparently logs all assumptions when "I don't know" or "Unknown" is selected.

### 🔬 Mode 2: Metallurgist / Engineer / Scientist ("Engineering Recommendation")
Direct numerical and microstructural control for materials scientists:
- **Strict Distinction between Hard Constraints & User Priorities**:
  - **Hard Constraints (Go / No-Go Eligibility)**:
    - Minimum Yield Strength $R_{p0.2}$ (MPa)
    - Minimum Tensile Strength $R_m$ (MPa)
    - Minimum Elongation $A_{50\text{mm}}$ (%)
    - Maximum Hardness (HRB / HRC / BHN)
    - Service Temperature Range ($T_{\text{min}}$ and $T_{\text{max}}$ in °C)
    - Minimum Pitting Resistance Equivalent Number (PREN)
    - Mandatory Non-Magnetic ($\mu_r \le 1.05$)
    - Microstructural Family Filter (Austenitic Cr-Ni, Austenitic Cr-Mn, Duplex, Ferritic, Martensitic)
    - Chemical Composition Limits (e.g. $Mo_{\text{min}} \ge 2.0\%$)
  - **User Priorities (Weighted Utility Optimization)**:
    - Corrosion weight ($w_1$), Strength weight ($w_2$), Cost weight ($w_3$), Formability weight ($w_4$), Weldability weight ($w_5$).
- **Bottleneck Constraint Diagnosis**:
  If no grade satisfies 100% of the hard constraints, the system **does not hallucinate a recommendation**. It pinpoints the conflicting constraints (e.g., Yield Strength $\ge 700$ MPa + Mandatory Non-Magnetic) and displays the closest candidate grades with their specific deficiencies.

---

## 🧮 Recommendation & Scoring Engine

### 1. Normalization of Physical Dimensions
Properties with different engineering units (MPa, °C, PREN, cost index) are normalized to $[0.0, 1.0]$:
- **Corrosion Compatibility ($C_{\text{corr}}$)**:
  $$C_{\text{corr}} = 0.6 \times \text{clamp}\left(\frac{\text{PREN}}{42.0}, 0.2, 1.0\right) + 0.4 \times \frac{\text{Score}_{\text{general}}}{10}$$
- **Strength Compatibility ($C_{\text{strength}}$)**:
  $$C_{\text{strength}} = \text{clamp}\left(\frac{YS}{YS_{\text{req}}}, 0.2, 1.0\right) \quad \text{or} \quad \text{clamp}\left(\frac{YS}{550}, 0.25, 1.0\right)$$
- **Commercial Cost Compatibility ($C_{\text{cost}}$)**:
  $$C_{\text{cost}} = 1.0 - \frac{\text{CostIndex} - 3.5}{9.8 - 3.5} \quad (\text{Lower cost yields higher score})$$
- **Formability & Weldability Compatibility**:
  Derived from elongation %EL, Limit Drawing Ratio (LDR), Erichsen cupping values, and consumable welding performance.

### 2. Multi-Attribute Weighted Scoring Formula
$$\text{Final Compatibility Score} = \frac{\sum_{i=1}^{n} w_i \times C_i}{\sum_{i=1}^{n} w_i} \times 100\%$$

The score is **deterministic and rule-based in code**. The LLM is never permitted to invent numbers.

---

## ⚖️ Trade-off & Comparison Engine

The system calculates exact pairwise differences between the Primary Recommendation (Rank 1) and Alternatives (Rank 2–5):
$$\Delta \text{Corrosion} = C_{\text{corr}}(A) - C_{\text{corr}}(B)$$
$$\Delta \text{Strength} = YS(A) - YS(B)$$
$$\Delta \text{Cost} = \text{CostIndex}(A) - \text{CostIndex}(B)$$

### Real-Time "What-If?" Priority Simulator
Allows the user to adjust sliders on the results screen (e.g., shifting Corrosion from 40% ➔ 20% and Cost from 10% ➔ 30%) and watch the ranking re-order instantaneously.

---

## 📊 Knowledge Base & Verified JSL Grades

The database includes **56 verified stainless steel grades** sourced directly from Jindal Stainless Limited technical datasheets:

1. **Austenitic Cr-Ni (300 Series & High-Temp)**:
   - J-304, 304*, J-304L, J-304LN, J-304H, J-305
   - J-316, J-316L, J-316LN, J-316Ti, J-317L, J-317LMN, J-904L
   - J-301, J-301L, J-301LN, J-321, J-347, J-309S, J-310S, UNS S30815 (253 MA), EN 1.4828, EN 1.4841
2. **Duplex & Super Duplex**:
   - J-2101 (Lean Duplex UNS S32101, PREN 26, YS 450 MPa)
   - J-2304 (Lean Duplex UNS S32304, PREN 25, YS 400 MPa)
   - J-2205 (Standard Duplex UNS S32205, PREN 35, YS 450 MPa, CPT 55°C)
   - J-31803 (Standard Duplex UNS S31803, PREN 34)
   - J-32750 (Super Duplex UNS S32750, PREN 42, YS 550 MPa, CPT 70°C)
   - J-32760 (Super Duplex with W UNS S32760, PREN 42.5, CPT 85°C)
3. **Austenitic Cr-Mn (200 Series)**:
   - J-201, J-201L, J-201LN, J-202, J-204, J-204Cu, J216L, JSL AUS, J-4, J4-16Cr, JSL U DD
4. **Ferritic & Stabilized Alloys**:
   - EN 1.4003 (3CR12 Utility Ferritic, 250× mild steel life, 4.7× wear resistance)
   - J-409L, J-409Ni, J-410S, J-430, J-430SM, J-432, J-436L, J-439, J-441, J-444, J-445
5. **Martensitic & Tool Steels**:
   - J-410, J-410DB (Disc Brake Special), J-415 (Ni-Mo High Toughness), J-420J2, EN 1.4116, J-431

---

## 🛠️ Project Structure

```text
Know_Your_Laws-Agentic-AI--main/
├── data/
│   ├── grades_database.json          # 56 structured JSL grades with full metallurgy metrics
│   └── knowledge_base/               # Technical datasheets, ASTM/EN standards, corrosion data
│       ├── duplex_stainless_steels.md
│       ├── austenitic_cr_ni_steels.md
│       ├── austenitic_cr_mn_200_series.md
│       ├── ferritic_stainless_steels.md
│       ├── martensitic_stainless_steels.md
│       └── corrosion_and_standards.md
├── src/
│   ├── config.py                     # Configuration, credentials, models, file paths
│   ├── models.py                     # Strongly-typed Pydantic schemas
│   ├── knowledge_base.py             # Knowledge Base loader, queries, citations
│   ├── scoring.py                    # Deterministic math scoring engine, normalization, bottlenecks
│   ├── report_generator.py           # Formats downloadable engineering dossiers
│   ├── agents/
│   │   ├── interpretation_layer.py   # Translates layman inputs to engineering requirements
│   │   ├── constraint_agent.py       # Hard constraint Go/No-Go audit & bottleneck detection
│   │   ├── scoring_agent.py          # Deterministic ranking & component breakdown
│   │   ├── retrieval_agent.py        # Knowledge base search & datasheet citation enrichment
│   │   ├── tradeoff_agent.py         # Pairwise comparison & What-If sensitivity simulator
│   │   ├── explanation_agent.py      # Transparent engineering rationales (LLM + offline fallback)
│   │   └── recommendation_agent.py   # Master orchestrator producing recommendation packages
│   └── graph_builder/
│       └── workflow_graph.py         # LangGraph StateGraph pipeline
├── streamlit_app.py                  # Full-stack interactive Streamlit web application
├── requirements.txt                  # Python dependencies
└── README.md                         # Complete documentation
```

---

## 💻 Running Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables (Optional)
If you wish to use an external LLM (Groq) for generative explanations, create a `.env` file:
```env
GROQ_API_KEY="your_groq_api_key_here"
```
*(Note: If no API key is provided, the system seamlessly runs its built-in deterministic metallurgical reasoning engine offline with 100% functionality).*

### 3. Launch the Application
```bash
python -m streamlit run streamlit_app.py
```
Open your browser at `http://localhost:8501`.
