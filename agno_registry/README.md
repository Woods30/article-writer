# Agno Registry

这个目录用于存放可动态加载的 Team/Agent 定义。

## 目录约定

- `teams/<team_id>/team.yaml`
- `teams/<team_id>/TEAM.md`
- `teams/<team_id>/agents/<agent_id>/agent.yaml`
- `teams/<team_id>/agents/<agent_id>/AGENT.md`
- `teams/<team_id>/agents/<agent_id>/SOUL.md`
- `teams/<team_id>/agents/<agent_id>/skills/*.md`
- `teams/<team_id>/agents/<agent_id>/memory/*.md`

新增 team 或 agent 后，无需改代码，直接通过 CLI `list-teams` / `run-team` 使用。
