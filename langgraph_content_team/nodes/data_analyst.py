"""Data Analyst — post-publication retrospective."""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from ..configuration import Configuration
from ..prompts import DATA_ANALYST_PROMPT
from ..state import ContentState


async def data_analyst(state: ContentState, config: RunnableConfig) -> dict:
    """Analyse publication performance data and produce retrospective + insights."""
    cfg = Configuration.from_runnable_config(config)
    llm = cfg.get_model("planner")

    materials = state.get("materials", {})
    performance_data = materials.get("performance_data", "")
    if not performance_data:
        performance_data = state.get("user_request", "")

    prompt = DATA_ANALYST_PROMPT.format(performance_data=performance_data)
    response = await llm.ainvoke(prompt)

    content = response.content
    insight_memo = content
    memo_markers = ["## 洞察备忘录", "# 洞察备忘录"]
    for marker in memo_markers:
        if marker in content:
            idx = content.index(marker)
            insight_memo = content[idx:]
            break

    return {
        "retrospective_report": content,
        "insight_memo": insight_memo,
        "current_stage": "data_analysis_done",
        "messages": [{"role": "assistant", "content": "[数据分析师] 复盘报告与洞察备忘录已生成"}],
    }
