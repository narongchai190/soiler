# S.O.I.L.E.R. Operations Runbook

## Running the Application

### Windows
```cmd
scripts\run.cmd cli      # CLI mode
scripts\run.cmd cli -q   # Quiet mode
scripts\run.cmd web      # Streamlit dashboard
```

### Unix/Mac
```bash
./scripts/run.sh cli     # CLI mode
./scripts/run.sh cli -q  # Quiet mode
./scripts/run.sh web     # Streamlit dashboard
```

### Direct Python
```bash
python main.py           # Full verbose
python main.py -q        # Quiet mode
python main.py -i        # Interactive input
streamlit run streamlit_app.py  # Web dashboard
```

## Expected Output

### Successful Run
```
✅ ANALYSIS COMPLETE
Session: SESSION-YYYYMMDD-XXXXXX
Agents Executed: 8
Observations: 7
🌱 S.O.I.L.E.R. Analysis Complete!
```

### Key Metrics in Report
- Soil Health Score: 0-100
- Target Yield: kg/rai
- Total Investment: THB
- Expected ROI: percentage

## Common Failures & Fixes

### 1. UTF-8 Console Encoding (Windows)

**Symptom:**
```
UnicodeEncodeError: 'charmap' codec can't encode characters
```

**Fix:**
```cmd
set PYTHONIOENCODING=utf-8
python main.py
```
Or use `scripts\run.cmd` which sets this automatically.

### 2. Missing Dependencies

**Symptom:**
```
ModuleNotFoundError: No module named 'pydantic'
```

**Fix:**
```bash
pip install -r requirements.txt
```

### 3. Agent Response Error

**Symptom:**
```
AttributeError: 'dict' object has no attribute 'success'
```

**Fix:** This was fixed in v0.1.0. Update to latest version.

### 4. Missing Weather API Key

**Symptom:** Weather data shows simulated values, not live data.

**Note:** This is expected behavior. The app uses simulated data by default.

**Fix (optional):** Set `OPENWEATHERMAP_API_KEY` in `.env`

## Agent Log Interpretation

Each agent logs with format: `[HH:MM:SS] [AgentName] LEVEL: message`

| Agent | Role | Key Outputs |
|-------|------|-------------|
| SoilSeriesExpert | Soil identification | Soil series name, match confidence |
| SoilChemistryExpert | pH/NPK analysis | Nutrient levels, deficiencies |
| CropBiologyExpert | Crop requirements | Growth stages, yield potential |
| PestDiseaseExpert | Risk assessment | Pest/disease warnings |
| ClimateExpert | Weather analysis | Rainfall, temperature suitability |
| FertilizerExpert | Fertilizer calc | Formula, application schedule |
| MarketCostExpert | Cost/ROI | Investment, profit projection |
| ChiefReporter | Report generation | Executive summary |

### Log Levels
- `INFO`: Normal processing steps
- `DEBUG`: Detailed calculations
- `WARNING`: Non-critical issues (e.g., over budget)
- `ERROR`: Agent failures (pipeline continues)

## Reproducing Issues

### Quick Smoke Test
```bash
pytest tests/test_pipeline.py::TestPipeline::test_full_pipeline_execution -v
```

### Test Specific Agent
```python
from agents.soil_series_agent import SoilSeriesAgent
agent = SoilSeriesAgent(verbose=True)
result = agent.process({"location": "Phrae", "texture": "clay loam"})
print(result.success, result.payload)
```

### Capture Full Debug Output
```bash
python main.py 2>&1 | tee debug.log
```

## Health Checks

```bash
# Syntax check
python -m py_compile main.py

# Quick test
pytest -q

# Full pipeline
python main.py -q
```
