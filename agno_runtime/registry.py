from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .manifests import AgentManifest, TeamManifest


class RegistryError(RuntimeError):
    """Raised when registry content is missing or invalid."""


class RegistryLoader:
    """Load teams and agents from a filesystem registry."""

    def __init__(self, registry_root: Path):
        self.registry_root = registry_root.resolve()
        self.teams_root = self.registry_root / "teams"

    def list_team_ids(self) -> list[str]:
        if not self.teams_root.exists():
            return []
        result: list[str] = []
        for path in sorted(self.teams_root.iterdir()):
            if (path / "team.yaml").exists():
                result.append(path.name)
        return result

    def load_team_manifest(self, team_id: str) -> TeamManifest:
        team_dir = self.teams_root / team_id
        team_file = team_dir / "team.yaml"
        if not team_file.exists():
            raise RegistryError(f"未找到 team manifest: {team_file}")
        data = _read_yaml(team_file)
        try:
            return TeamManifest(
                id=data["id"],
                name=data["name"],
                description=data.get("description", ""),
                base_dir=team_dir,
                mode=data.get("mode", "route"),
                public_entry_agent=data.get("public_entry_agent"),
                members=list(data.get("members", [])),
                instructions_file=data.get("instructions_file", "TEAM.md"),
                model=data.get("model"),
                markdown=bool(data.get("markdown", True)),
                metadata=dict(data.get("metadata", {})),
            )
        except KeyError as exc:
            raise RegistryError(f"team.yaml 缺少必填字段: {exc}") from exc

    def list_agent_ids(self, team_id: str) -> list[str]:
        team_dir = self.teams_root / team_id
        agents_dir = team_dir / "agents"
        if not agents_dir.exists():
            return []
        result: list[str] = []
        for path in sorted(agents_dir.iterdir()):
            if (path / "agent.yaml").exists():
                result.append(path.name)
        return result

    def load_agent_manifest(self, team_id: str, agent_id: str) -> AgentManifest:
        team_dir = self.teams_root / team_id
        agent_dir = team_dir / "agents" / agent_id
        agent_file = agent_dir / "agent.yaml"
        if not agent_file.exists():
            raise RegistryError(f"未找到 agent manifest: {agent_file}")
        data = _read_yaml(agent_file)
        try:
            return AgentManifest(
                id=data["id"],
                name=data["name"],
                role=data.get("role", "member"),
                description=data.get("description", ""),
                team_id=team_id,
                base_dir=agent_dir,
                tools=list(data.get("tools", [])),
                model=data.get("model"),
                markdown=bool(data.get("markdown", True)),
                instructions_file=data.get("instructions_file", "AGENT.md"),
                soul_file=data.get("soul_file", "SOUL.md"),
                skills_dir=data.get("skills_dir", "skills"),
                memory_dir=data.get("memory_dir", "memory"),
                metadata=dict(data.get("metadata", {})),
            )
        except KeyError as exc:
            raise RegistryError(f"agent.yaml 缺少必填字段: {exc}") from exc

    def load_agent_instruction_parts(self, manifest: AgentManifest) -> list[str]:
        parts: list[str] = []
        agent_md = manifest.base_dir / manifest.instructions_file
        soul_md = manifest.base_dir / manifest.soul_file
        parts.extend(_read_existing_files([agent_md, soul_md]))

        skills_dir = manifest.base_dir / manifest.skills_dir
        if skills_dir.exists():
            skill_files = sorted(skills_dir.glob("*.md"))
            for skill_file in skill_files:
                text = skill_file.read_text(encoding="utf-8").strip()
                if text:
                    parts.append(f"[Skill:{skill_file.stem}]\n{text}")

        memory_dir = manifest.base_dir / manifest.memory_dir
        if memory_dir.exists():
            memory_files = sorted(memory_dir.glob("*.md"))
            for memory_file in memory_files:
                text = memory_file.read_text(encoding="utf-8").strip()
                if text:
                    parts.append(f"[Memory:{memory_file.stem}]\n{text}")
        return parts

    def load_team_instructions(self, team_manifest: TeamManifest) -> str | None:
        team_file = team_manifest.base_dir / team_manifest.instructions_file
        if team_file.exists():
            text = team_file.read_text(encoding="utf-8").strip()
            return text or None
        return None

    def validate(self) -> list[str]:
        errors: list[str] = []
        for team_id in self.list_team_ids():
            try:
                team = self.load_team_manifest(team_id)
            except RegistryError as exc:
                errors.append(str(exc))
                continue

            agent_ids = self.list_agent_ids(team_id)
            missing_members = sorted(set(team.members) - set(agent_ids))
            if missing_members:
                errors.append(
                    f"team={team_id} 缺少 members agent 定义: {', '.join(missing_members)}"
                )

            if team.public_entry_agent and team.public_entry_agent not in agent_ids:
                errors.append(
                    f"team={team_id} public_entry_agent 未定义: {team.public_entry_agent}"
                )

            for agent_id in agent_ids:
                try:
                    agent = self.load_agent_manifest(team_id, agent_id)
                except RegistryError as exc:
                    errors.append(str(exc))
                    continue

                required_files = [
                    agent.base_dir / agent.instructions_file,
                    agent.base_dir / agent.soul_file,
                ]
                for required in required_files:
                    if not required.exists():
                        errors.append(f"team={team_id} agent={agent_id} 缺少文件: {required}")
        return errors


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content) or {}
        if not isinstance(data, dict):
            raise RegistryError(f"YAML 顶层必须为对象: {path}")
        return data
    except RegistryError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise RegistryError(f"YAML 读取失败: {path}: {exc}") from exc


def _read_existing_files(paths: list[Path]) -> list[str]:
    result: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").strip()
        if text:
            result.append(text)
    return result
