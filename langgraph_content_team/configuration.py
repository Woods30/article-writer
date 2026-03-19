"""Central configuration for the content creation graph."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


@dataclass(frozen=True)
class Configuration:
    """All tunables for the content-creation graph."""

    # ── models ──────────────────────────────────────────────────
    planner_model: str = "openai:gpt-4o-mini"
    writer_model: str = "openai:gpt-4o-mini"
    researcher_model: str = "openai:gpt-4o-mini"
    auditor_model: str = "openai:gpt-4o-mini"

    # ── workflow ────────────────────────────────────────────────
    max_revision_rounds: int = 2
    audit_pass_threshold: int = 70
    min_candidate_topics: int = 5

    # ── search ──────────────────────────────────────────────────
    search_api: Optional[str] = None  # "tavily" | None
    search_max_results: int = 5

    # ── OpenAI ──────────────────────────────────────────────────
    openai_base_url: Optional[str] = None

    @classmethod
    def from_runnable_config(cls, config: Optional[RunnableConfig] = None) -> "Configuration":
        configurable = (config or {}).get("configurable", {})
        init_kwargs: dict[str, Any] = {}
        for f in cls.__dataclass_fields__:
            if f in configurable:
                init_kwargs[f] = configurable[f]
        base_url = (
            init_kwargs.get("openai_base_url")
            or os.getenv("AGNO_OPENAI_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
        )
        if base_url:
            init_kwargs["openai_base_url"] = base_url
            os.environ["OPENAI_BASE_URL"] = base_url
        return cls(**init_kwargs)

    def _parse_provider_model(self, model_str: str) -> tuple[str, str]:
        if ":" in model_str:
            provider, model = model_str.split(":", 1)
            return provider, model
        return "openai", model_str

    def get_model(self, role: str = "planner"):
        from langchain_openai import ChatOpenAI

        model_map = {
            "planner": self.planner_model,
            "writer": self.writer_model,
            "researcher": self.researcher_model,
            "auditor": self.auditor_model,
        }
        model_str = model_map.get(role, self.planner_model)
        _provider, model_name = self._parse_provider_model(model_str)

        kwargs: dict[str, Any] = {"model": model_name, "temperature": 0.7}
        if self.openai_base_url:
            kwargs["base_url"] = self.openai_base_url
        return ChatOpenAI(**kwargs)
