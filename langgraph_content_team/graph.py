"""
LangGraph-based content creation workflow.

Supports 4 modes:
  A — Start from research report
  B — Full pipeline from scratch
  C — Post-publication data retrospective
  D — Platform rewrite (WeChat → Xiaohongshu)

The graph uses conditional edges to route between modes and implements
a quality-gate loop (max 2 revision rounds) before final delivery.
"""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, StateGraph

from .nodes.data_analyst import data_analyst
from .nodes.deliverables import assemble_deliverables
from .nodes.illustrator import illustrator
from .nodes.platform_adapter import adapter_revision, platform_adapter
from .nodes.quality_auditor import quality_auditor
from .nodes.researcher import deep_researcher
from .nodes.route import route_mode
from .nodes.topic_strategist import topic_strategist
from .nodes.trend_analyst import trend_analyst
from .nodes.writer import lead_writer, writer_revision
from .state import ContentState

# ── Conditional edge helpers ────────────────────────────────────


def _after_route(state: ContentState) -> str:
    """Dispatch to the first node of the selected mode."""
    mode = state.get("mode", "B")
    return {
        "A": "topic_strategist",
        "B": "trend_analyst",
        "C": "data_analyst",
        "D": "platform_adapter",
    }.get(mode, "trend_analyst")


def _after_audit(state: ContentState) -> str:
    """Branch on audit outcome: pass → illustrator, fail → revision or escalate."""
    if state.get("audit_decision") == "pass":
        mode = state.get("mode", "B")
        if mode == "D":
            return "assemble"
        return "illustrator"

    max_rounds = 2
    if state.get("revision_count", 0) >= max_rounds:
        return "assemble"

    has_writer = any(
        item.get("owner", "").lower() == "writer"
        for item in state.get("revision_items", [])
    )
    if has_writer:
        return "writer_revision"
    return "adapter_revision"


def _after_writer_revision(_state: ContentState) -> str:
    return "adapter_revision"


def _after_adapter_revision(_state: ContentState) -> str:
    return "quality_auditor"


def _after_data_analyst(state: ContentState) -> str:
    """Mode C: data_analyst → trend_analyst → assemble."""
    return "trend_analyst_c"


# ── Graph builder ───────────────────────────────────────────────


def build_graph() -> StateGraph:
    """Construct and return the compiled content-creation graph."""

    g = StateGraph(ContentState)

    # ── Register nodes ──────────────────────────────────────────
    g.add_node("route_mode", route_mode)
    g.add_node("trend_analyst", trend_analyst)
    g.add_node("topic_strategist", topic_strategist)
    g.add_node("deep_researcher", deep_researcher)
    g.add_node("lead_writer", lead_writer)
    g.add_node("platform_adapter", platform_adapter)
    g.add_node("quality_auditor", quality_auditor)
    g.add_node("illustrator", illustrator)
    g.add_node("data_analyst", data_analyst)
    g.add_node("writer_revision", writer_revision)
    g.add_node("adapter_revision", adapter_revision)
    g.add_node("assemble", assemble_deliverables)

    # mode-C dedicated trend node (shares implementation)
    g.add_node("trend_analyst_c", trend_analyst)

    # ── Entry ───────────────────────────────────────────────────
    g.set_entry_point("route_mode")

    # ── After route: dispatch to correct mode ───────────────────
    g.add_conditional_edges(
        "route_mode",
        _after_route,
        {
            "trend_analyst": "trend_analyst",
            "topic_strategist": "topic_strategist",
            "data_analyst": "data_analyst",
            "platform_adapter": "platform_adapter",
        },
    )

    # ── Mode B: trend → topic → research → write → adapt → audit
    g.add_edge("trend_analyst", "topic_strategist")

    # ── Mode A & B share: topic → research → write → adapt → audit
    g.add_edge("topic_strategist", "deep_researcher")
    g.add_edge("deep_researcher", "lead_writer")
    g.add_edge("lead_writer", "platform_adapter")
    g.add_edge("platform_adapter", "quality_auditor")

    # ── Audit gate ──────────────────────────────────────────────
    g.add_conditional_edges(
        "quality_auditor",
        _after_audit,
        {
            "illustrator": "illustrator",
            "writer_revision": "writer_revision",
            "adapter_revision": "adapter_revision",
            "assemble": "assemble",
        },
    )

    # ── Revision loop ───────────────────────────────────────────
    g.add_edge("writer_revision", "adapter_revision")
    g.add_edge("adapter_revision", "quality_auditor")

    # ── After illustrator → assemble ────────────────────────────
    g.add_edge("illustrator", "assemble")

    # ── Mode C: data_analyst → trend_analyst_c → assemble ───────
    g.add_edge("data_analyst", "trend_analyst_c")
    g.add_edge("trend_analyst_c", "assemble")

    # ── Final ───────────────────────────────────────────────────
    g.add_edge("assemble", END)

    return g


def compile_graph(**kwargs):
    """Build, compile, and return the runnable graph."""
    return build_graph().compile(**kwargs)
