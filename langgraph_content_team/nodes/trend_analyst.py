"""Trend Insight Analyst — discovers content opportunities."""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from ..configuration import Configuration
from ..prompts import TREND_ANALYST_PROMPT
from ..state import ContentState


async def trend_analyst(state: ContentState, config: RunnableConfig) -> dict:
    """Scan trends and produce candidate topic material report."""
    cfg = Configuration.from_runnable_config(config)
    llm = cfg.get_model("researcher")

    user_request = state.get("user_request", "")
    insight_memo = state.get("insight_memo", "")

    if insight_memo:
        input_context = f"洞察备忘录（来自数据复盘）：\n{insight_memo}"
    elif user_request:
        input_context = f"用户请求：{user_request}"
    else:
        input_context = "主动扫描模式，请根据当前热点生成候选选题。"

    prompt = TREND_ANALYST_PROMPT.format(input_context=input_context)
    response = await llm.ainvoke(prompt)

    return {
        "topic_material_report": response.content,
        "current_stage": "trend_analysis_done",
        "messages": [{"role": "assistant", "content": "[趋势洞察师] 选题素材报告已生成"}],
    }
