# agno_runtime

`agno_runtime` 用于从文件系统注册表加载 Team/Agent 定义，并使用 Agno 执行。

## 模块说明

- `registry.py`：扫描与加载 `agno_registry/` 中的 manifest
- `builder.py`：将 manifest 转换为 `agno.agent.Agent` / `agno.team.Team`
- `cli.py`：提供 list / validate / run / scaffold 命令
- `tools.py`：内置工具注册（read/write/edit/now_utc）

## 设计目标

1. 可扩展：新增 team/agent 不改代码，仅增量新增目录和文件。
2. 可组合：可以运行整队（run-team）或单角色（run-agent）。
3. 可迁移：同时兼容 OpenClaw 风格的 `AGENT.md` / `SOUL.md` / `skills` / `memory` 组织方式。
