"""Deep Researcher — fact-checks and structures research materials."""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from ..configuration import Configuration
from ..prompts import DEEP_RESEARCHER_PROMPT
from ..state import ContentState


async def deep_researcher(state: ContentState, config: RunnableConfig) -> dict:
    """Produce structured research pack (modules A–E) from creative brief."""
    cfg = Configuration.from_runnable_config(config)
    llm = cfg.get_model("researcher")

    prompt = DEEP_RESEARCHER_PROMPT.format(
        creative_brief=state.get("creative_brief", ""),
    )
    response = await llm.ainvoke(prompt)

    return {
        "research_pack": response.content,
        "current_stage": "research_done",
        "messages": [{"role": "assistant", "content": "[深度研究员] 研究素材包 (A-E) 已生成"}],
    }
