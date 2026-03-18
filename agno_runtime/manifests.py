from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AgentManifest:
    id: str
    name: str
    role: str
    description: str
    team_id: str
    base_dir: Path
    tools: list[str] = field(default_factory=list)
    model: str | None = None
    markdown: bool = True
    instructions_file: str = "AGENT.md"
    soul_file: str = "SOUL.md"
    skills_dir: str = "skills"
    memory_dir: str = "memory"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TeamManifest:
    id: str
    name: str
    description: str
    base_dir: Path
    mode: str = "route"
    public_entry_agent: str | None = None
    members: list[str] = field(default_factory=list)
    instructions_file: str = "TEAM.md"
    model: str | None = None
    markdown: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
