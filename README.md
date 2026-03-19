# article-writer

基于 **LangGraph** 的多 Agent 内容创作团队（自媒体内容创作团队），支持微信公众号和小红书双平台内容生产。

参考架构：[open_deep_research](https://github.com/langchain-ai/open_deep_research)

---

## 项目结构

```
langgraph_content_team/     # LangGraph 实现（推荐）
├── __main__.py             # CLI 入口
├── configuration.py        # 配置中心
├── state.py                # 状态定义
├── prompts.py              # 全部 Agent 提示词
├── graph.py                # 主图定义（4 种模式）
└── nodes/                  # Agent 节点实现
    ├── route.py            # 模式路由
    ├── trend_analyst.py    # 趋势洞察师
    ├── topic_strategist.py # 选题策略师
    ├── researcher.py       # 深度研究员
    ├── writer.py           # 首席撰稿人
    ├── platform_adapter.py # 平台适配师
    ├── quality_auditor.py  # 质量审核官
    ├── illustrator.py      # 插画配图师
    ├── data_analyst.py     # 数据分析师
    └── deliverables.py     # 交付物汇总

agno_registry/              # Agno YAML 注册表（历史）
agno_runtime/               # Agno 运行时（历史）
openclaw_content_team/      # OpenClaw JSON 包（历史）
```

---

## 工作模式

| 模式 | 名称 | 流程 |
|------|------|------|
| **A** | 从研究报告启动 | 选题策略师 → 深度研究员 → 撰稿人 → 适配师 → 审核 → 配图 |
| **B** | 从零开始创作 | 趋势洞察 → 选题策略 → 深度研究 → 撰稿 → 适配 → 审核 → 配图 |
| **C** | 数据复盘 | 数据分析师 → 趋势洞察师 |
| **D** | 平台改写 | 平台适配师 → 质量审核 |

---

## 安装依赖

```bash
pip install -r requirements.txt
```

> 需要设置 OpenAI API Key：
>
> ```bash
> export OPENAI_API_KEY=你的key
> ```
>
> 如需自定义 OpenAI 网关：
>
> ```bash
> export OPENAI_BASE_URL=https://your-openai-gateway/v1
> ```

---

## 使用方式

### 1) 校验图结构

```bash
python3 -m langgraph_content_team validate
```

### 2) 查看图结构

```bash
python3 -m langgraph_content_team show-graph
```

### 3) 干跑（不调用模型）

```bash
python3 -m langgraph_content_team run \
  --input "帮我从选题开始创作一篇关于AI效率工具的文章" --dry-run
```

### 4) 模式 B — 从零开始创作

```bash
python3 -m langgraph_content_team run \
  --input "帮我从选题开始创作一篇关于AI效率工具的双平台文章"
```

### 5) 模式 A — 从研究报告启动

```bash
python3 -m langgraph_content_team run \
  --input "我有一份研究报告，请完整跑一遍" \
  --material research_report "这里是研究报告内容..."
```

### 6) 模式 C — 数据复盘

```bash
python3 -m langgraph_content_team run \
  --input "复盘上周发布的内容" \
  --material performance_data "阅读 5200, 转发 120..."
```

### 7) 模式 D — 平台改写

```bash
python3 -m langgraph_content_team run \
  --input "把这篇公众号文章改成小红书版本" \
  --material wechat_original_article "# 原文标题..."
```

### 8) 指定模型

```bash
python3 -m langgraph_content_team --model openai:gpt-4o run \
  --input "从选题开始创作一篇文章"
```

---

## 质量门禁

- 质量审核官对内容进行三维评分（内容价值 40 + 传播表现 30 + 合规风险 30）
- 总分 ≥ 70 且无硬性否决项才通过
- 未通过时自动修订，最多 2 轮，超过后上报人工

---

## 历史版本

- **Agno 运行时**：`agno_runtime/` + `agno_registry/`（详见 `agno_runtime/README.md`）
- **OpenClaw JSON 包**：`openclaw_content_team/`（详见 `openclaw_content_team/README.md`）
