# S.O.I.L.E.R. Architecture Diagram

## System Overview

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              S.O.I.L.E.R. SYSTEM ARCHITECTURE                          │
│                 Soil Optimization & Intelligent Land Expert Recommender                │
└────────────────────────────────────────────────────────────────────────────────────────┘

                                    USER INTERFACES
    ┌──────────────────────────────────────┬──────────────────────────────────────┐
    │           CLI Mode                   │          Web Dashboard Mode          │
    │          (main.py)                   │       (streamlit_app.py)             │
    │                                      │                                       │
    │  $ python main.py -q                 │  $ streamlit run streamlit_app.py    │
    │  $ python main.py -i (interactive)  │                                       │
    │                                      │  Features:                            │
    │  Features:                           │  - Sidebar input forms               │
    │  - ASCII banner                      │  - Interactive map (Folium/OSM)      │
    │  - Rich console output               │  - 4 result tabs                     │
    │  - Progress indicators               │  - History panel                     │
    │  - Thai/English output               │  - Auto-save to database             │
    └──────────────────────┬───────────────┴──────────────────────┬───────────────┘
                           │                                       │
                           └───────────────┬───────────────────────┘
                                           │
                                           ▼
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                            ORCHESTRATION LAYER                                    │
    │                         (core/orchestrator.py)                                    │
    │                                                                                   │
    │  class SoilerOrchestrator:                                                       │
    │    - Manages 8-agent pipeline sequence                                            │
    │    - Passes observations between agents                                           │
    │    - Generates session IDs                                                        │
    │    - Handles errors gracefully                                                    │
    │    - Collects Thai observations for report                                        │
    │                                                                                   │
    │  def analyze(location, crop, ph, nitrogen, phosphorus, potassium, ...)           │
    │      → Returns: Executive Report (Dict)                                           │
    └──────────────────────────────────────┬───────────────────────────────────────────┘
                                           │
                                           ▼
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                            8-AGENT PIPELINE                                       │
    │                           (agents/*.py)                                           │
    │                                                                                   │
    │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
    │  │   STEP 1    │    │   STEP 2    │    │   STEP 3    │    │   STEP 4    │       │
    │  │             │    │             │    │             │    │             │       │
    │  │ SoilSeries  │───▶│ SoilChem    │───▶│ CropBiology │───▶│ PestDisease │       │
    │  │   Expert    │    │   Expert    │    │   Expert    │    │   Expert    │       │
    │  │             │    │             │    │             │    │             │       │
    │  │ Identifies  │    │ Analyzes    │    │ Calculates  │    │ Assesses    │       │
    │  │ soil series │    │ pH, N-P-K   │    │ yield       │    │ pest/disease│       │
    │  │ from texture│    │ deficiencies│    │ potential   │    │ risks       │       │
    │  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘       │
    │         │                  │                  │                  │               │
    │         │   observation_th │   observation_th │   observation_th │               │
    │         └──────────────────┴──────────────────┴──────────────────┘               │
    │                                                                                   │
    │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
    │  │   STEP 5    │    │   STEP 6    │    │   STEP 7    │    │   STEP 8    │       │
    │  │             │    │             │    │             │    │             │       │
    │  │  Climate    │───▶│ Fertilizer  │───▶│ MarketCost  │───▶│   Report    │       │
    │  │   Expert    │    │   Expert    │    │   Expert    │    │   Agent     │       │
    │  │             │    │             │    │             │    │             │       │
    │  │ Weather     │    │ Calculates  │    │ Computes    │    │ Generates   │       │
    │  │ suitability │    │ fertilizer  │    │ costs, ROI, │    │ executive   │       │
    │  │ assessment  │    │ schedule    │    │ break-even  │    │ summary     │       │
    │  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘       │
    │                                                                                   │
    │  Base Class: agents/base_agent.py                                                │
    │    - AgentProcessResponse (success, payload, error_message)                      │
    │    - Logging methods (think, log_action, log_result, log_warning, log_error)    │
    │    - Thai observation chain support                                               │
    └──────────────────────────────────────┬───────────────────────────────────────────┘
                                           │
                                           ▼
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                            DATA LAYER                                             │
    │                           (data/*.py)                                             │
    │                                                                                   │
    │  ┌───────────────────────┐    ┌───────────────────────┐                          │
    │  │   DatabaseManager     │    │    KnowledgeBase      │                          │
    │  │ (database_manager.py) │    │  (knowledge_base.py)  │                          │
    │  │                       │    │                       │                          │
    │  │ - SQLite persistence  │    │ - Soil series data    │                          │
    │  │ - Analysis history    │    │ - Crop requirements   │                          │
    │  │ - User sessions       │    │ - Fertilizer formulas │                          │
    │  │ - Export/import       │    │ - Market prices       │                          │
    │  │                       │    │                       │                          │
    │  │ Tables:               │    │ Static data for       │                          │
    │  │ - analysis_history    │    │ Phrae Province, TH    │                          │
    │  │ - user_sessions       │    │                       │                          │
    │  └───────────────────────┘    └───────────────────────┘                          │
    │               │                          │                                        │
    │               ▼                          ▼                                        │
    │  ┌───────────────────────┐    ┌───────────────────────┐                          │
    │  │   soiler_v1.db        │    │   master_data.json    │                          │
    │  │   (SQLite file)       │    │   (Static JSON)       │                          │
    │  └───────────────────────┘    └───────────────────────┘                          │
    └──────────────────────────────────────────────────────────────────────────────────┘

                                    SUPPORTING MODULES

    ┌──────────────────────────┐    ┌──────────────────────────┐
    │   core/schemas.py        │    │   utils/calculator.py    │
    │                          │    │   utils/logger.py        │
    │   Pydantic models:       │    │                          │
    │   - SoilData             │    │   - UILogger             │
    │   - AnalysisResult       │    │   - Utility calculations │
    │   - FertilizerRec        │    │                          │
    │   - AgentRequest/Response│    │                          │
    └──────────────────────────┘    └──────────────────────────┘
```

## Data Flow Diagram

```
                                    INPUT
                                      │
    ┌─────────────────────────────────┼─────────────────────────────────┐
    │                                 │                                  │
    │  User Inputs:                   │                                  │
    │  - Location (lat/lon or district)                                  │
    │  - Crop type (Riceberry Rice / Corn)                               │
    │  - Field size (rai)                                                │
    │  - Soil tests (pH, N, P, K)                                        │
    │  - Budget (THB)                                                    │
    │  - Options (irrigation, organic)                                   │
    │                                 │                                  │
    └─────────────────────────────────┼─────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │                         PROCESSING PIPELINE                         │
    │                                                                      │
    │   Input → [SoilSeries] → [SoilChem] → [CropBio] → [Pest]           │
    │                                                                      │
    │            → [Climate] → [Fertilizer] → [Market] → [Report]         │
    │                                                                      │
    │   Each agent:                                                        │
    │   1. Receives input + previous agent's observation_th               │
    │   2. Processes using knowledge base                                  │
    │   3. Returns AgentProcessResponse with payload + observation_th     │
    └─────────────────────────────────┬───────────────────────────────────┘
                                      │
                                      ▼
                                   OUTPUT
                                      │
    ┌─────────────────────────────────┼─────────────────────────────────┐
    │                                 │                                  │
    │  Executive Report:              │                                  │
    │  - Overall assessment (Thai)    │                                  │
    │  - Soil health score            │                                  │
    │  - Yield projections            │                                  │
    │  - Fertilizer schedule          │                                  │
    │  - Cost breakdown               │                                  │
    │  - ROI calculation              │                                  │
    │  - Risk assessment              │                                  │
    │  - Action plan                  │                                  │
    │  - Agent thought chain          │                                  │
    │                                 │                                  │
    └─────────────────────────────────┼─────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │                           STORAGE                                    │
    │                                                                      │
    │   Streamlit Mode: Auto-saves to data/soiler_v1.db                   │
    │   CLI Mode: Output only (no persistence)                             │
    └─────────────────────────────────────────────────────────────────────┘
```

## Agent Responsibility Matrix

```
┌─────────────────────┬────────────────────────────────────────────────────────┐
│ Agent               │ Responsibility                                          │
├─────────────────────┼────────────────────────────────────────────────────────┤
│ SoilSeriesExpert    │ Match location/texture to known soil series            │
│                     │ Output: series_name, match_score, characteristics       │
├─────────────────────┼────────────────────────────────────────────────────────┤
│ SoilChemistryExpert │ Analyze pH and NPK levels against crop requirements    │
│                     │ Output: health_score, nutrient_status, issues          │
├─────────────────────┼────────────────────────────────────────────────────────┤
│ CropBiologyExpert   │ Calculate yield potential and growth calendar          │
│                     │ Output: yield_targets, growth_calendar, critical_periods│
├─────────────────────┼────────────────────────────────────────────────────────┤
│ PestDiseaseExpert   │ Assess pest and disease risks for crop/season          │
│                     │ Output: pest_analysis, disease_analysis, ipm_plan      │
├─────────────────────┼────────────────────────────────────────────────────────┤
│ ClimateExpert       │ Evaluate weather suitability and risks                 │
│                     │ Output: suitability, weather_risks, planting_window    │
├─────────────────────┼────────────────────────────────────────────────────────┤
│ FertilizerExpert    │ Generate fertilizer application schedule               │
│                     │ Output: application_schedule, cost_analysis, budget_fit│
├─────────────────────┼────────────────────────────────────────────────────────┤
│ MarketCostExpert    │ Calculate costs, revenue, ROI, break-even              │
│                     │ Output: cost_analysis, profit_analysis, market_risks   │
├─────────────────────┼────────────────────────────────────────────────────────┤
│ ChiefReporter       │ Compile all analyses into executive report             │
│                     │ Output: executive_summary, dashboard, action_plan      │
└─────────────────────┴────────────────────────────────────────────────────────┘
```

## File Structure

```
soiler/
├── agents/                          # 8 AI Agents + Base Class
│   ├── __init__.py
│   ├── base_agent.py               # AgentProcessResponse, BaseAgent
│   ├── soil_series_agent.py        # Step 1: Soil identification
│   ├── soil_chemistry_agent.py     # Step 2: pH/NPK analysis
│   ├── crop_biology_agent.py       # Step 3: Yield calculation
│   ├── pest_disease_agent.py       # Step 4: Risk assessment
│   ├── climate_agent.py            # Step 5: Weather analysis
│   ├── fertilizer_formula_agent.py # Step 6: Fertilizer plan
│   ├── market_cost_agent.py        # Step 7: Financial analysis
│   └── report_agent.py             # Step 8: Report generation
│   └── (legacy: soil_agent.py, crop_agent.py, env_agent.py, etc.)
│
├── core/                            # Core Business Logic
│   ├── __init__.py
│   ├── orchestrator.py             # SoilerOrchestrator - Pipeline manager
│   └── schemas.py                  # Pydantic data models
│
├── data/                            # Data Layer
│   ├── __init__.py
│   ├── database_manager.py         # SQLite CRUD operations
│   ├── knowledge_base.py           # Static agricultural data
│   ├── master_data.json            # Reference data
│   └── soiler_v1.db                # SQLite database file
│
├── utils/                           # Utilities
│   ├── __init__.py
│   ├── calculator.py               # Math helpers
│   └── logger.py                   # UILogger for Streamlit
│
├── tests/                           # Test Suite
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_agents.py              # Agent unit tests (12 tests)
│   ├── test_pipeline.py            # Integration tests (5 tests)
│   └── test_ui_e2e.py              # Playwright E2E tests (3 tests)
│
├── scripts/                         # Run Scripts
│   ├── run.cmd                     # Windows launcher
│   └── run.sh                      # Unix launcher
│
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI
│
├── .streamlit/
│   └── config.toml                 # Streamlit theme config
│
├── main.py                          # CLI Entry Point
├── streamlit_app.py                 # Web Dashboard Entry Point
│
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies
├── .env.example                     # Environment variable template
├── .gitignore                       # Git ignore patterns
│
├── README.md                        # User documentation
├── TODO.md                          # Development backlog
├── RUNBOOK.md                       # Operations guide
├── RELEASE.md                       # Release process
├── CHANGELOG.md                     # Version history
├── AUDIT_REPORT.md                  # This audit report
├── AUDIT_FINDINGS.json              # Machine-readable findings
├── BACKLOG_AUDIT.md                 # Prioritized fixes
└── ARCHITECTURE_DIAGRAM.md          # This file
```

## Technology Stack

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           TECHNOLOGY STACK                                │
├──────────────────────────────────────────────────────────────────────────┤
│ Language          │ Python 3.10+ (tested on 3.10, 3.11, 3.12)           │
├───────────────────┼──────────────────────────────────────────────────────┤
│ Web Framework     │ Streamlit 1.28+                                      │
├───────────────────┼──────────────────────────────────────────────────────┤
│ Data Validation   │ Pydantic 2.0+                                        │
├───────────────────┼──────────────────────────────────────────────────────┤
│ CLI Output        │ Rich 13.0+ (graceful degradation if missing)         │
├───────────────────┼──────────────────────────────────────────────────────┤
│ Database          │ SQLite (via Python sqlite3)                          │
├───────────────────┼──────────────────────────────────────────────────────┤
│ Maps              │ Folium 0.14+ / OpenStreetMap                         │
├───────────────────┼──────────────────────────────────────────────────────┤
│ Data Processing   │ Pandas 2.0+                                          │
├───────────────────┼──────────────────────────────────────────────────────┤
│ Testing           │ pytest 7.0+, Playwright 1.40+                        │
├───────────────────┼──────────────────────────────────────────────────────┤
│ Linting           │ Ruff 0.1+                                            │
├───────────────────┼──────────────────────────────────────────────────────┤
│ CI/CD             │ GitHub Actions                                        │
├───────────────────┼──────────────────────────────────────────────────────┤
│ Localization      │ Thai language (TH dictionary in streamlit_app.py)    │
└───────────────────┴──────────────────────────────────────────────────────┘
```
