"""Topic Strategist — produces Creative Brief from materials."""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from ..configuration import Configuration
from ..prompts import TOPIC_STRATEGIST_PROMPT
from ..state import ContentState


async def topic_strategist(state: ContentState, config: RunnableConfig) -> dict:
    """Generate a Creative Brief from topic material or research report."""
    cfg = Configuration.from_runnable_config(config)
    llm = cfg.get_model("planner")

    mode = state.get("mode", "B")
    if mode == "A":
        materials = state.get("materials", {})
        report = materials.get("research_report", "")
        input_context = f"研究报告（模式 A）：\n{report}"
    else:
        input_context = f"选题素材报告（模式 B）：\n{state.get('topic_material_report', '')}"

    user_request = state.get("user_request", "")
    if user_request:
        input_context += f"\n\n用户原始请求：{user_request}"

    prompt = TOPIC_STRATEGIST_PROMPT.format(input_context=input_context)
    response = await llm.ainvoke(prompt)

    return {
        "creative_brief": response.content,
        "current_stage": "creative_brief_done",
        "messages": [{"role": "assistant", "content": "[选题策略师] Creative Brief 已生成，等待用户确认选题方向"}],
    }
