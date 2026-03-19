# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a **LangGraph-based multi-agent content creation platform** (article-writer). It contains:

- `langgraph_content_team/` — LangGraph implementation with 9 agent nodes, 4 workflow modes (A/B/C/D)
- `agno_runtime/` + `agno_registry/` — Legacy Agno YAML-based runtime
- `openclaw_content_team/` — Legacy OpenClaw JSON bundle

### Running the application (LangGraph)

```bash
# Validate graph compilation
python3 -m langgraph_content_team validate

# Show graph nodes and edges
python3 -m langgraph_content_team show-graph

# Dry-run (no LLM calls, no API key needed)
python3 -m langgraph_content_team run --input "test" --dry-run

# Live run (requires OPENAI_API_KEY)
python3 -m langgraph_content_team run --input "帮我创作一篇文章"

# Mode D — shortest pipeline for quick testing
python3 -m langgraph_content_team run --mode D \
  --input "改写" --material wechat_original_article "原文内容"
```

### Running the application (legacy Agno)

See `README.md` for Agno runtime commands. Key commands:
- `python3 -m agno_runtime --registry-root agno_registry validate`
- `python3 -m agno_runtime --registry-root agno_registry list-teams`

### Non-obvious caveats

- **No automated test suite.** Validation is done via `validate` CLI command and dry-run.
- **No linter configuration.** Code style checks are not enforced.
- **Live execution** requires `OPENAI_API_KEY`. Without it, only `validate`, `show-graph`, and `--dry-run` work.
- **Mode D** (platform_adapter → quality_auditor → assemble) is the shortest pipeline — use it for quick end-to-end testing (~20s).
- **Mode B** (full 7-step pipeline) is the most comprehensive and takes ~60–90s per run with `gpt-4o-mini`.
- **Audit gate**: quality_auditor must score ≥ 70 with no hard-veto items. On failure, auto-revision loops up to 2 rounds before escalating.
- The `.cursor/environment.json` has been deleted so snapshot-managed environment settings take effect.
- **Graph compilation** is fast (~0.7s) and does not require an API key — use `validate` or `show-graph` for quick sanity checks after code changes.
