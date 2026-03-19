"""Deliverables assembly node — collects final outputs."""

from __future__ import annotations

from ..state import ContentState


async def assemble_deliverables(state: ContentState, *_args) -> dict:
    """Assemble all generated artefacts into a final deliverables dict."""
    mode = state.get("mode", "B")
    deliverables: dict = {"mode": mode}

    if mode in ("A", "B"):
        deliverables["wechat_article"] = state.get("wechat_draft", "")
        deliverables["xiaohongshu_note"] = state.get("xiaohongshu_draft", "")
        deliverables["platform_adaptation"] = state.get("platform_adaptation", "")
        deliverables["audit_report"] = state.get("audit_report", "")
        deliverables["audit_score"] = state.get("audit_score", 0)
        deliverables["image_prompts"] = state.get("image_prompts", "")
    elif mode == "C":
        deliverables["retrospective_report"] = state.get("retrospective_report", "")
        deliverables["insight_memo"] = state.get("insight_memo", "")
        deliverables["topic_material_report"] = state.get("topic_material_report", "")
    elif mode == "D":
        deliverables["platform_adaptation"] = state.get("platform_adaptation", "")
        deliverables["audit_report"] = state.get("audit_report", "")
        deliverables["audit_score"] = state.get("audit_score", 0)

    return {
        "final_deliverables": deliverables,
        "current_stage": "completed",
        "messages": [{"role": "assistant", "content": f"[交付] 模式 {mode} 全部产出已汇总完毕"}],
    }
