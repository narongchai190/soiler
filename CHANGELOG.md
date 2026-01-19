# Changelog

All notable changes to S.O.I.L.E.R. will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
