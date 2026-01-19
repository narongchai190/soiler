# S.O.I.L.E.R. Backlog

## Priority Levels
- **P0**: Critical/Blocking - must fix before release
- **P1**: High priority - should complete soon
- **P2**: Medium priority - nice to have
- **P3**: Low priority - future consideration

---

## P0 - Critical

- [x] Fix syntax error in fertilizer_formula_agent.py (nested f-string)
- [x] Fix Windows console Unicode encoding for Thai characters
- [x] Fix orchestrator response handling (dict vs AgentResponse)

## P1 - High Priority

- [ ] Add unit tests for each agent's core logic
- [ ] Add integration test for full pipeline
- [ ] Implement proper error handling in orchestrator (graceful degradation)
- [ ] Add input validation for main.py CLI arguments
- [ ] Wire up `observation_th` properly in report (currently shows "No observation")

## P2 - Medium Priority

- [ ] Add logging framework (replace print statements)
- [ ] Add configuration file support (YAML/TOML)
- [ ] Implement caching for repeated API calls
- [ ] Add database migration scripts
- [ ] Improve Streamlit dashboard layout
- [ ] Add export functionality (PDF, Excel)
- [ ] Add Thai/English language toggle in UI
- [ ] Document all agents' input/output schemas

## P3 - Low Priority / Future

- [ ] Add support for additional crops
- [ ] Integrate real weather API (OpenWeatherMap)
- [ ] Add satellite imagery analysis
- [ ] Implement user authentication for web dashboard
- [ ] Add historical analysis tracking
- [ ] Mobile-responsive Streamlit theme
- [ ] Add API endpoint mode (FastAPI)
- [ ] Containerize with Docker

---

## Technical Debt

- [ ] Consolidate duplicate climate data in `climate_agent.py` and `env_agent.py`
- [ ] Remove unused imports across agents
- [ ] Standardize naming conventions (Thai vs English keys)
- [ ] Add type hints to all functions
- [ ] Reduce code duplication in agent `_execute` methods

---

## Done

- [x] Initial project setup
- [x] 8-agent pipeline implementation
- [x] Streamlit web dashboard
- [x] SQLite database integration
- [x] Thai language support in outputs
- [x] Basic README documentation
- [x] Git repository initialization
