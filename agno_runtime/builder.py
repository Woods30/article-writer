from __future__ import annotations

import os
from typing import Any

from agno.agent import Agent
from agno.team import Team, TeamMode

from .manifests import AgentManifest, TeamManifest
from .registry import RegistryLoader
from .tools import BUILTIN_TOOL_REGISTRY


class AgnoTeamBuilder:
    """Build Agno Agent and Team instances from registry manifests."""

    def __init__(
        self,
        registry_loader: RegistryLoader,
        model_override: str | None = None,
        telemetry: bool = False,
    ):
        self.registry_loader = registry_loader
        self.model_override = model_override
        self.telemetry = telemetry

    def build_agent(self, team_id: str, agent_id: str) -> Agent:
        manifest = self.registry_loader.load_agent_manifest(team_id, agent_id)
        instructions = self.registry_loader.load_agent_instruction_parts(manifest)
        model = self._resolve_model(manifest.model)
        tools = self._resolve_tools(manifest.tools)
        return Agent(
            id=f"{team_id}:{manifest.id}",
            name=manifest.name,
            role=manifest.role,
            description=manifest.description,
            model=model,
            markdown=manifest.markdown,
            instructions=instructions,
            tools=tools if tools else None,
            metadata={
                "team_id": team_id,
                "agent_id": manifest.id,
                "declared_tools": manifest.tools,
                **manifest.metadata,
            },
            telemetry=self.telemetry,
        )

    def build_team(self, team_id: str) -> Team:
        team_manifest = self.registry_loader.load_team_manifest(team_id)
        member_ids = team_manifest.members or self.registry_loader.list_agent_ids(team_id)
        members = [self.build_agent(team_id, agent_id) for agent_id in member_ids]
        mode = self._resolve_mode(team_manifest.mode)
        team_model = self._resolve_model(team_manifest.model)
        team_instructions = self.registry_loader.load_team_instructions(team_manifest)
        return Team(
            id=team_manifest.id,
            name=team_manifest.name,
            description=team_manifest.description,
            members=members,
            mode=mode,
            model=team_model,
            markdown=team_manifest.markdown,
            instructions=team_instructions,
            metadata={
                "public_entry_agent": team_manifest.public_entry_agent,
                **team_manifest.metadata,
            },
            telemetry=self.telemetry,
        )

    def summarize_team(self, team_id: str) -> dict[str, Any]:
        team_manifest = self.registry_loader.load_team_manifest(team_id)
        member_ids = team_manifest.members or self.registry_loader.list_agent_ids(team_id)
        agents: list[dict[str, Any]] = []
        for agent_id in member_ids:
            agent = self.registry_loader.load_agent_manifest(team_id, agent_id)
            agents.append(
                {
                    "id": agent.id,
                    "name": agent.name,
                    "role": agent.role,
                    "tools": agent.tools,
                    "model": self._resolve_model(agent.model),
                }
            )
        return {
            "team_id": team_manifest.id,
            "name": team_manifest.name,
            "mode": team_manifest.mode,
            "model": self._resolve_model(team_manifest.model),
            "public_entry_agent": team_manifest.public_entry_agent,
            "members": agents,
        }

    def _resolve_model(self, declared_model: str | None) -> str | None:
        return self.model_override or declared_model or os.getenv("AGNO_MODEL")

    @staticmethod
    def _resolve_mode(mode: str) -> TeamMode:
        normalized = (mode or "route").strip().lower()
        mapping = {
            "route": TeamMode.route,
            "coordinate": TeamMode.coordinate,
            "broadcast": TeamMode.broadcast,
            "tasks": TeamMode.tasks,
        }
        return mapping.get(normalized, TeamMode.route)

    @staticmethod
    def _resolve_tools(tool_names: list[str]) -> list[Any]:
        tools: list[Any] = []
        for tool_name in tool_names:
            tool = BUILTIN_TOOL_REGISTRY.get(tool_name)
            if tool is not None:
                tools.append(tool)
        return tools
