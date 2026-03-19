from __future__ import annotations

from pathlib import Path


def scaffold_team(registry_root: Path, team_id: str, team_name: str) -> Path:
    team_dir = registry_root / "teams" / team_id
    if team_dir.exists():
        raise FileExistsError(f"team 已存在: {team_dir}")

    (team_dir / "agents").mkdir(parents=True, exist_ok=False)

    team_yaml = f"""id: {team_id}
name: {team_name}
description: TODO
mode: route
public_entry_agent: orchestrator
instructions_file: TEAM.md
model: null
markdown: true
members:
  - orchestrator
"""
    (team_dir / "team.yaml").write_text(team_yaml, encoding="utf-8")
    (team_dir / "TEAM.md").write_text(
        "# Team Mission\n请描述团队目标、路由策略、门禁规则。\n",
        encoding="utf-8",
    )
    scaffold_agent(
        registry_root=registry_root,
        team_id=team_id,
        agent_id="orchestrator",
        agent_name="Orchestrator",
        role="orchestrator",
    )
    return team_dir


def scaffold_agent(
    registry_root: Path,
    team_id: str,
    agent_id: str,
    agent_name: str,
    role: str = "member",
) -> Path:
    agent_dir = registry_root / "teams" / team_id / "agents" / agent_id
    if agent_dir.exists():
        raise FileExistsError(f"agent 已存在: {agent_dir}")

    (agent_dir / "skills").mkdir(parents=True, exist_ok=False)
    (agent_dir / "memory").mkdir(parents=True, exist_ok=False)

    agent_yaml = f"""id: {agent_id}
name: {agent_name}
role: {role}
description: TODO
instructions_file: AGENT.md
soul_file: SOUL.md
skills_dir: skills
memory_dir: memory
tools: []
model: null
markdown: true
"""
    (agent_dir / "agent.yaml").write_text(agent_yaml, encoding="utf-8")
    (agent_dir / "AGENT.md").write_text(
        "# AGENT\n请描述该角色职责、输入输出和约束。\n",
        encoding="utf-8",
    )
    (agent_dir / "SOUL.md").write_text(
        "# SOUL\n请描述该角色的风格、价值观和边界。\n",
        encoding="utf-8",
    )
    (agent_dir / "skills" / "default.md").write_text(
        "# Skill: default\n补充可复用策略。\n",
        encoding="utf-8",
    )
    (agent_dir / "memory" / "default.md").write_text(
        "记录长期记忆与偏好。\n",
        encoding="utf-8",
    )
    return agent_dir
