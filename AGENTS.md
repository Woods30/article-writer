# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is an **Agno-based multi-agent content creation platform** (article-writer). It contains:

- `agno_runtime/` — Python CLI that loads teams/agents from a YAML filesystem registry
- `agno_registry/` — YAML team/agent definitions (currently one team: `content-creation-team` with 9 agents)
- `openclaw_content_team/` — JSON-based legacy bundle (optional)

### Running the application

All commands are documented in `README.md`. Key commands:

```bash
# Validate registry structure
python3 -m agno_runtime --registry-root agno_registry validate

# List teams / agents
python3 -m agno_runtime --registry-root agno_registry list-teams
python3 -m agno_runtime --registry-root agno_registry list-agents --team content-creation-team

# Dry-run (no LLM call, no API key needed)
python3 -m agno_runtime --registry-root agno_registry --model openai:gpt-4o-mini \
  run-team --team content-creation-team --input "test" --dry-run

# Validate the openclaw JSON bundle
python3 openclaw_content_team/scripts/validate_bundle.py
```

### Non-obvious caveats

- **No automated test suite exists.** Validation is done via `validate` CLI command and `validate_bundle.py`.
- **No linter configuration** (no `pyproject.toml`, `setup.cfg`, `ruff.toml`, or `.flake8`). Code style checks are not enforced.
- **Live execution** (without `--dry-run`) requires `OPENAI_API_KEY` env var. Without it, only dry-run and validation commands work.
- **Missing tool implementations**: `googleSearch`, `fetch`, `runSkill`, `searchApi` tools referenced in agent manifests are not implemented in `agno_runtime/tools.py` (only `now_utc`, `read`, `write`, `edit` are built-in). Agents referencing missing tools will have those tools silently skipped at build time.
- The `.cursor/environment.json` has been deleted from the repo so snapshot-managed environment settings take effect.
