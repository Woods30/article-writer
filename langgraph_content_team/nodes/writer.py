"""Lead Writer — produces dual-platform drafts."""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from ..configuration import Configuration
from ..prompts import LEAD_WRITER_PROMPT, WRITER_REVISION_PROMPT
from ..state import ContentState


async def lead_writer(state: ContentState, config: RunnableConfig) -> dict:
    """Write WeChat long-form + Xiaohongshu note from brief + research."""
    cfg = Configuration.from_runnable_config(config)
    llm = cfg.get_model("writer")

    prompt = LEAD_WRITER_PROMPT.format(
        creative_brief=state.get("creative_brief", ""),
        research_pack=state.get("research_pack", ""),
    )
    response = await llm.ainvoke(prompt)

    content = response.content
    wechat_draft = content
    xiaohongshu_draft = ""

    sep_markers = ["## 小红书笔记", "## 小红书", "# 小红书笔记", "# 小红书"]
    for marker in sep_markers:
        if marker in content:
            idx = content.index(marker)
            wechat_draft = content[:idx].strip()
            xiaohongshu_draft = content[idx:].strip()
            break

    return {
        "wechat_draft": wechat_draft,
        "xiaohongshu_draft": xiaohongshu_draft,
        "current_stage": "drafts_done",
        "messages": [{"role": "assistant", "content": "[首席撰稿人] 双平台初稿已完成，等待用户确认"}],
    }


async def writer_revision(state: ContentState, config: RunnableConfig) -> dict:
    """Revise drafts based on audit feedback."""
    cfg = Configuration.from_runnable_config(config)
    llm = cfg.get_model("writer")

    writer_items = [
        item for item in state.get("revision_items", [])
        if item.get("owner", "").lower() == "writer"
    ]
    if not writer_items:
        return {}

    items_text = "\n".join(
        f"- [{item.get('issue', '')}] {item.get('action', '')}"
        for item in writer_items
    )
    prompt = WRITER_REVISION_PROMPT.format(
        wechat_draft=state.get("wechat_draft", ""),
        xiaohongshu_draft=state.get("xiaohongshu_draft", ""),
        revision_items=items_text,
    )
    response = await llm.ainvoke(prompt)
    content = response.content
    wechat_draft = content
    xiaohongshu_draft = state.get("xiaohongshu_draft", "")

    sep_markers = ["## 小红书笔记", "## 小红书", "# 小红书笔记", "# 小红书"]
    for marker in sep_markers:
        if marker in content:
            idx = content.index(marker)
            wechat_draft = content[:idx].strip()
            xiaohongshu_draft = content[idx:].strip()
            break

    return {
        "wechat_draft": wechat_draft,
        "xiaohongshu_draft": xiaohongshu_draft,
        "messages": [{"role": "assistant", "content": "[首席撰稿人] 已根据审核反馈修订稿件"}],
    }
