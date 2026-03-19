"""State schemas for the content creation graph."""

from __future__ import annotations

import operator
from typing import Annotated, Any, Literal

from typing_extensions import TypedDict


class AgentOutput(TypedDict, total=False):
    """Standard envelope that every agent node returns."""

    output: str
    key_summary: list[str]
    next_agent_focus: list[str]
    pending_human_confirmations: list[str]


class ContentState(TypedDict, total=False):
    """Top-level graph state shared across all nodes."""

    # ── user input ──────────────────────────────────────────────
    user_request: str
    mode: Literal["A", "B", "C", "D"]
    materials: dict[str, Any]
    target_platforms: list[str]
    constraints: list[str]

    # ── intermediate artefacts (set by agent nodes) ─────────────
    topic_material_report: str
    creative_brief: str
    research_pack: str
    wechat_draft: str
    xiaohongshu_draft: str
    platform_adaptation: str
    audit_report: str
    audit_decision: Literal["pass", "fail"]
    audit_score: int
    revision_items: list[dict[str, str]]
    image_prompts: str
    retrospective_report: str
    insight_memo: str

    # ── control flow ────────────────────────────────────────────
    revision_count: int
    current_stage: str
    error: str

    # ── human-in-the-loop ───────────────────────────────────────
    topic_confirmed: bool
    draft_confirmed: bool
    publish_confirmed: bool

    # ── conversation log (append-only) ──────────────────────────
    messages: Annotated[list[dict[str, str]], operator.add]

    # ── final deliverables ──────────────────────────────────────
    final_deliverables: dict[str, Any]
