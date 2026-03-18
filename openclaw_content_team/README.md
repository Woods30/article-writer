# OpenClaw Multi-Agent：自媒体内容创作团队

这是一个可安装到 OpenClaw 的多代理团队包。  
对外只暴露一个 Agent（`team_orchestrator`），内部由多个 SubAgent 协作完成内容创作。

## 1. 目录结构

```text
openclaw_content_team/
├── team.json
├── agents/
├── workflows/
├── prompts/
├── schemas/
├── templates/
├── examples/
├── installer/
└── scripts/
```

## 2. 角色清单

- 团队协调者（Orchestrator，公开入口）
- 趋势洞察师
- 选题策略师
- 深度研究员
- 首席撰稿人
- 平台适配师
- 质量审核官
- 插画配图师
- 数据分析师

## 3. 支持流程

- 模式 A：研究报告 -> 策略 -> 研究 -> 撰稿 -> 适配 -> 审核 -> 配图
- 模式 B：趋势洞察 -> 策略 -> 研究 -> 撰稿 -> 适配 -> 审核 -> 配图
- 模式 C：发布数据 -> 复盘 -> 趋势回传
- 模式 D：公众号原文 -> 平台改写 -> 审核

## 4. 安装到现有 OpenClaw

> 假设你的 OpenClaw 根目录是 `/path/to/openclaw`

```bash
python openclaw_content_team/scripts/validate_bundle.py
python openclaw_content_team/installer/install_to_openclaw.py \
  --openclaw-home /path/to/openclaw \
  --force
```

安装后将：
1. 复制团队包到 `<openclaw-home>/teams/content-creation-team`
2. 更新 `<openclaw-home>/teams/index.json` 注册条目

## 5. 任务输入示例

见 `examples/mode_inputs.json`。

## 6. 人工介入节点

1. 选题确认（topic_strategist）
2. 初稿确认（lead_writer）
3. 发布确认（quality_auditor）

## 7. 审核门禁

- 通过：总分 >= 70 且无硬性否决项
- 退回：总分 < 70 或存在硬性否决项
- 修改上限：2 轮，超限后升级人工
