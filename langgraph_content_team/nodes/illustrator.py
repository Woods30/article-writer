"""Illustrator — generates AI image prompts."""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from ..configuration import Configuration
from ..prompts import ILLUSTRATOR_PROMPT
from ..state import ContentState


async def illustrator(state: ContentState, config: RunnableConfig) -> dict:
    """Generate Midjourney + DALL·E prompts for the approved content."""
    cfg = Configuration.from_runnable_config(config)
    llm = cfg.get_model("writer")

    article_parts = []
    if state.get("wechat_draft"):
        article_parts.append(f"## 公众号文章\n{state['wechat_draft'][:2000]}")
    if state.get("xiaohongshu_draft"):
        article_parts.append(f"## 小红书笔记\n{state['xiaohongshu_draft'][:1500]}")
    if state.get("platform_adaptation"):
        article_parts.append(f"## 适配方案摘要\n{state['platform_adaptation'][:1000]}")

    prompt = ILLUSTRATOR_PROMPT.format(
        article_content="\n\n".join(article_parts) or "(无文章内容)",
    )
    response = await llm.ainvoke(prompt)

    return {
        "image_prompts": response.content,
        "current_stage": "illustration_done",
        "messages": [{"role": "assistant", "content": "[插画配图师] AI 生图提示词已生成"}],
    }
