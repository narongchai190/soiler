# Changelog

All notable changes to S.O.I.L.E.R. will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-24

### Added
- **Skill-first Agent Architecture**: Deterministic soil diagnosis and fertilizer planning
  - `soil_diagnosis()` skill with Thai Dept of Agriculture thresholds
  - `fertilizer_plan()` skill with crop-specific NPK targets
  - Skill-based agent wrappers for pipeline integration
- **RAG System with Citations**: Knowledge retrieval with source citations
  - 7 reference documents covering Thai agriculture standards
  - TF-IDF based search with relevance scoring
  - Citation formatting for grounded responses
- **Evaluation Suite**: 30 deterministic test cases
  - 10 soil diagnosis cases
  - 10 fertilizer planning cases
  - 10 RAG retrieval cases
- **E2E Smoke Tests**: Playwright-based UI testing
- **Selection Summary Panel**: Sidebar widget showing user selections

### Security
- Secret scanner with enhanced pattern detection
- CI enforcement of secret scanning
- SECURITY.md with key rotation instructions
- No secrets shipped in repository

### Fixed
- UTF-8 encoding issues on Windows console
- Streamlit widget state stability
- Sidebar dropdown inconsistencies
- Ruff lint errors (44 total fixed)

### DevOps
- `evals.yml` CI workflow for evaluation suite
- Database seeding mechanism for fresh installations
- Enhanced `.gitignore` for production safety
- Release readiness report generation

### Documentation
- RUNBOOK.md production runbook
- RELEASE.md release checklist
- Enhanced SECURITY.md with deployment guides

## [0.1.0] - 2026-01-19

### Added
- Initial release of S.O.I.L.E.R. multi-agent AI system
- 8 specialized agents for precision agriculture analysis
- CLI interface (`main.py`) with verbose/quiet/interactive modes
- Streamlit web dashboard (`streamlit_app.py`)
- SQLite database for persistence
- Thai language support in agent outputs

### Fixed
- Syntax error in `fertilizer_formula_agent.py` nested f-string (bfc87db)
- Windows console UTF-8 encoding for Thai characters (bfc87db)
- Orchestrator response handling - dict vs AgentResponse (bfc87db)

### Documentation
- README.md with setup and usage instructions (8c4bd52)
- TODO.md with prioritized backlog (8c4bd52)
- .env.example for optional API keys (8c4bd52)

### DevOps
- Run scripts for Windows/Unix (4cbff2f)
- requirements.txt and requirements-dev.txt (4cbff2f)
- Smoke tests with pytest - 17 tests (0c025b6)
- GitHub Actions CI workflow (684233e)
- Ruff lint configuration (a9b469b)

## Commits in this release

| Hash | Description |
|------|-------------|
| bfc87db | fix: resolve runtime errors and make app functional |
| 8c4bd52 | docs: add README, backlog, and env example |
| 4cbff2f | chore: add run scripts and reproducible setup |
| 0c025b6 | test: add smoke tests for agents and pipeline |
| 684233e | ci: add GitHub Actions workflow |
| a9b469b | chore: add minimal ruff lint config |
