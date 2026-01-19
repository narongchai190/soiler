# S.O.I.L.E.R.

**Soil Optimization & Intelligent Land Expert Recommender**

A multi-agent AI system for precision agriculture analysis. Analyzes soil data, climate conditions, and market factors to provide actionable farming recommendations.

## Features

- 8 specialized AI agents working in a coordinated pipeline
- Soil series identification and chemistry analysis
- Crop biology and pest/disease assessment
- Climate and environmental analysis
- Fertilizer formula optimization
- Market cost and ROI analysis
- Executive report generation (Thai language support)

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd soiler

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

**Console Mode (CLI):**
```bash
python main.py           # Full verbose output
python main.py -q        # Quiet mode
python main.py -i        # Interactive mode with custom inputs
```

**Web Dashboard (Streamlit):**
```bash
streamlit run streamlit_app.py
```

## Architecture

```
soiler/
├── agents/           # 8 specialized AI agents
│   ├── base_agent.py         # Base class with response wrapper
│   ├── soil_series_agent.py  # Soil identification
│   ├── soil_chemistry_agent.py
│   ├── crop_biology_agent.py
│   ├── pest_disease_agent.py
│   ├── climate_agent.py
│   ├── fertilizer_formula_agent.py
│   ├── market_cost_agent.py
│   └── report_agent.py
├── core/
│   ├── orchestrator.py       # Pipeline coordinator
│   └── schemas.py            # Pydantic data models
├── data/
│   ├── knowledge_base.py     # Static agricultural data
│   └── database_manager.py   # SQLite persistence
├── utils/
│   └── calculator.py         # Utility calculations
├── main.py                   # CLI entry point
└── streamlit_app.py          # Web dashboard
```

## Pipeline Flow

1. **SoilSeriesExpert** - Identifies soil series from location/texture
2. **SoilChemistryExpert** - Analyzes pH, N-P-K levels
3. **CropBiologyExpert** - Assesses crop requirements
4. **PestDiseaseExpert** - Evaluates pest/disease risks
5. **ClimateExpert** - Analyzes weather patterns
6. **FertilizerExpert** - Calculates optimal fertilizer formula
7. **MarketCostExpert** - Computes costs and ROI
8. **ReportAgent** - Generates executive summary

## Environment Variables (Optional)

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENWEATHERMAP_API_KEY` | Weather API for live data | None (uses simulated data) |
| `GOOGLE_MAPS_API_KEY` | Maps integration in Streamlit | Fallback key provided |

## Troubleshooting

### Windows Console Encoding

If you see encoding errors with Thai characters:
```bash
set PYTHONIOENCODING=utf-8
python main.py
```

The application automatically handles this, but setting the environment variable can help in edge cases.

### Missing Dependencies

```bash
pip install --upgrade pydantic rich streamlit pandas
```

## Development

```bash
# Install dev dependencies
pip install pytest ruff

# Run tests
pytest

# Check code style
ruff check .
```

## License

[Add license information]
