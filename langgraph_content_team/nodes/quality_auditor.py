"""Quality Auditor — scores and gates content quality."""

from __future__ import annotations

import json
import re

from langchain_core.runnables import RunnableConfig

from ..configuration import Configuration
from ..prompts import QUALITY_AUDITOR_PROMPT
from ..state import ContentState


def _parse_audit_json(text: str) -> dict:
    """Best-effort extraction of JSON from LLM output."""
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    else:
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start != -1 and brace_end != -1:
            text = text[brace_start : brace_end + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "total_score": 0,
            "decision": "fail",
            "hard_veto_items": ["无法解析审核结果"],
            "revision_items": [],
            "summary": "审核报告解析失败",
        }


async def quality_auditor(state: ContentState, config: RunnableConfig) -> dict:
    """Audit content quality with 3-dimensional scoring."""
    cfg = Configuration.from_runnable_config(config)
    llm = cfg.get_model("auditor")

    draft_content = ""
    if state.get("wechat_draft"):
        draft_content += f"## 公众号稿件\n{state['wechat_draft']}\n\n"
    if state.get("xiaohongshu_draft"):
        draft_content += f"## 小红书稿件\n{state['xiaohongshu_draft']}"

    prompt = QUALITY_AUDITOR_PROMPT.format(
        draft_content=draft_content or "(无初稿)",
        adaptation_content=state.get("platform_adaptation", "(无适配方案)"),
    )
    response = await llm.ainvoke(prompt)
    audit = _parse_audit_json(response.content)

    total = audit.get("total_score", 0)
    hard_veto = audit.get("hard_veto_items", [])
    has_veto = bool(hard_veto and hard_veto != [""] and hard_veto != [])
    decision = "pass" if (total >= cfg.audit_pass_threshold and not has_veto) else "fail"

    revision_count = state.get("revision_count", 0) + (1 if decision == "fail" else 0)

    return {
        "audit_report": response.content,
        "audit_decision": decision,
        "audit_score": total,
        "revision_items": audit.get("revision_items", []),
        "revision_count": revision_count,
        "current_stage": "audit_done",
        "messages": [
            {
                "role": "assistant",
                "content": (
                    f"[质量审核官] 审核完成 — 总分 {total}，"
                    f"结论：{'通过 ✅' if decision == 'pass' else '退回 ❌'}"
                ),
            }
        ],
    }
