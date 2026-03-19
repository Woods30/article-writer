"""Mode routing node — determines which workflow (A/B/C/D) to run."""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from ..configuration import Configuration
from ..prompts import MODE_ROUTER_PROMPT
from ..state import ContentState


def _materials_summary(materials: dict | None) -> str:
    if not materials:
        return "无附带材料"
    parts = []
    for k, v in materials.items():
        preview = str(v)[:200] if v else "(空)"
        parts.append(f"- {k}: {preview}")
    return "\n".join(parts) or "无附带材料"


async def route_mode(state: ContentState, config: RunnableConfig) -> dict:
    """Classify user request into mode A/B/C/D."""
    cfg = Configuration.from_runnable_config(config)
    llm = cfg.get_model("planner")

    prompt = MODE_ROUTER_PROMPT.format(
        user_request=state.get("user_request", ""),
        materials_summary=_materials_summary(state.get("materials")),
    )
    response = await llm.ainvoke(prompt)
    mode = response.content.strip().upper()
    if mode not in ("A", "B", "C", "D"):
        mode = "B"

    return {
        "mode": mode,
        "current_stage": "mode_routed",
        "messages": [{"role": "system", "content": f"任务模式已识别为：模式 {mode}"}],
    }
