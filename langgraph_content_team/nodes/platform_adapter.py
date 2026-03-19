"""Platform Adapter — adapts content for WeChat / Xiaohongshu."""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from ..configuration import Configuration
from ..prompts import (
    ADAPTER_REVISION_PROMPT,
    PLATFORM_ADAPTER_PROMPT,
    PLATFORM_ADAPTER_REWRITE_PROMPT,
)
from ..state import ContentState


async def platform_adapter(state: ContentState, config: RunnableConfig) -> dict:
    """Produce titles, tags, cover copy, and short version for platforms."""
    cfg = Configuration.from_runnable_config(config)
    llm = cfg.get_model("planner")

    mode = state.get("mode", "B")
    if mode == "D":
        wechat_article = state.get("materials", {}).get(
            "wechat_original_article", state.get("wechat_draft", "")
        )
        prompt = PLATFORM_ADAPTER_REWRITE_PROMPT.format(wechat_article=wechat_article)
    else:
        draft_content = ""
        if state.get("wechat_draft"):
            draft_content += f"## 公众号初稿\n{state['wechat_draft']}\n\n"
        if state.get("xiaohongshu_draft"):
            draft_content += f"## 小红书初稿\n{state['xiaohongshu_draft']}"
        prompt = PLATFORM_ADAPTER_PROMPT.format(input_context=draft_content)

    response = await llm.ainvoke(prompt)

    return {
        "platform_adaptation": response.content,
        "current_stage": "adaptation_done",
        "messages": [{"role": "assistant", "content": "[平台适配师] 平台适配方案已生成"}],
    }


async def adapter_revision(state: ContentState, config: RunnableConfig) -> dict:
    """Revise platform adaptation based on audit feedback."""
    cfg = Configuration.from_runnable_config(config)
    llm = cfg.get_model("planner")

    adapter_items = [
        item for item in state.get("revision_items", [])
        if item.get("owner", "").lower() == "adapter"
    ]
    if not adapter_items:
        return {}

    items_text = "\n".join(
        f"- [{item.get('issue', '')}] {item.get('action', '')}"
        for item in adapter_items
    )
    prompt = ADAPTER_REVISION_PROMPT.format(
        platform_adaptation=state.get("platform_adaptation", ""),
        revision_items=items_text,
    )
    response = await llm.ainvoke(prompt)

    return {
        "platform_adaptation": response.content,
        "messages": [{"role": "assistant", "content": "[平台适配师] 已根据审核反馈修订适配方案"}],
    }
