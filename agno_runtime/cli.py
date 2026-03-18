from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .builder import AgnoTeamBuilder
from .registry import RegistryError, RegistryLoader
from .scaffold import scaffold_agent, scaffold_team


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Agno teams from filesystem registry.")
    parser.add_argument(
        "--registry-root",
        default="agno_registry",
        help="Registry 根目录，默认 agno_registry。",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="覆盖 team/agent 的模型配置，如 openai:gpt-4o-mini。",
    )
    parser.add_argument(
        "--telemetry",
        action="store_true",
        help="开启 Agno telemetry（默认关闭）。",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-teams", help="列出可用 team")

    p_agents = sub.add_parser("list-agents", help="列出 team 下 agent")
    p_agents.add_argument("--team", required=True, help="team id")

    sub.add_parser("validate", help="校验 registry 结构")

    p_scaffold_team = sub.add_parser("scaffold-team", help="创建 team 骨架")
    p_scaffold_team.add_argument("--team", required=True, help="team id")
    p_scaffold_team.add_argument("--name", required=True, help="team name")

    p_scaffold_agent = sub.add_parser("scaffold-agent", help="创建 agent 骨架")
    p_scaffold_agent.add_argument("--team", required=True, help="team id")
    p_scaffold_agent.add_argument("--agent", required=True, help="agent id")
    p_scaffold_agent.add_argument("--name", required=True, help="agent name")
    p_scaffold_agent.add_argument("--role", default="member", help="agent role")

    p_run_team = sub.add_parser("run-team", help="运行指定 team")
    p_run_team.add_argument("--team", required=True, help="team id")
    p_run_team.add_argument("--input", required=True, help="用户输入")
    p_run_team.add_argument("--session-id", default=None, help="可选 session id")
    p_run_team.add_argument("--user-id", default=None, help="可选 user id")
    p_run_team.add_argument(
        "--dry-run",
        action="store_true",
        help="仅输出构建信息，不调用模型。",
    )

    p_run_agent = sub.add_parser("run-agent", help="运行指定 agent")
    p_run_agent.add_argument("--team", required=True, help="team id")
    p_run_agent.add_argument("--agent", required=True, help="agent id")
    p_run_agent.add_argument("--input", required=True, help="用户输入")
    p_run_agent.add_argument("--session-id", default=None, help="可选 session id")
    p_run_agent.add_argument("--user-id", default=None, help="可选 user id")
    p_run_agent.add_argument(
        "--dry-run",
        action="store_true",
        help="仅输出构建信息，不调用模型。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    registry_root = Path(args.registry_root).resolve()
    loader = RegistryLoader(registry_root)
    builder = AgnoTeamBuilder(
        registry_loader=loader,
        model_override=args.model,
        telemetry=args.telemetry,
    )

    try:
        if args.command == "list-teams":
            return _cmd_list_teams(loader)
        if args.command == "list-agents":
            return _cmd_list_agents(loader, args.team)
        if args.command == "validate":
            return _cmd_validate(loader)
        if args.command == "scaffold-team":
            return _cmd_scaffold_team(registry_root, args.team, args.name)
        if args.command == "scaffold-agent":
            return _cmd_scaffold_agent(registry_root, args.team, args.agent, args.name, args.role)
        if args.command == "run-team":
            return _cmd_run_team(builder, args)
        if args.command == "run-agent":
            return _cmd_run_agent(builder, args)
    except RegistryError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    except ImportError as exc:
        print(f"[ERROR] 模型依赖缺失: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] 执行失败: {exc}", file=sys.stderr)
        return 1

    print(f"[ERROR] 未知命令: {args.command}", file=sys.stderr)
    return 1


def _cmd_list_teams(loader: RegistryLoader) -> int:
    team_ids = loader.list_team_ids()
    print(json.dumps({"teams": team_ids}, ensure_ascii=False, indent=2))
    return 0


def _cmd_list_agents(loader: RegistryLoader, team_id: str) -> int:
    agents = loader.list_agent_ids(team_id)
    print(json.dumps({"team": team_id, "agents": agents}, ensure_ascii=False, indent=2))
    return 0


def _cmd_validate(loader: RegistryLoader) -> int:
    errors = loader.validate()
    if errors:
        for err in errors:
            print(f"[ERROR] {err}")
        return 1
    print("[OK] agno registry 校验通过")
    return 0


def _cmd_run_team(builder: AgnoTeamBuilder, args: argparse.Namespace) -> int:
    if args.dry_run:
        summary = builder.summarize_team(args.team)
        print(json.dumps({"dry_run": True, "team_summary": summary}, ensure_ascii=False, indent=2))
        return 0

    team = builder.build_team(args.team)
    _ensure_model_for_run(summary=builder.summarize_team(args.team))
    response = team.run(
        args.input,
        session_id=args.session_id,
        user_id=args.user_id,
    )
    print(_extract_content(response))
    return 0


def _cmd_scaffold_team(registry_root: Path, team_id: str, team_name: str) -> int:
    created = scaffold_team(registry_root=registry_root, team_id=team_id, team_name=team_name)
    print(f"[OK] team scaffold created: {created}")
    return 0


def _cmd_scaffold_agent(
    registry_root: Path, team_id: str, agent_id: str, agent_name: str, role: str
) -> int:
    created = scaffold_agent(
        registry_root=registry_root,
        team_id=team_id,
        agent_id=agent_id,
        agent_name=agent_name,
        role=role,
    )
    print(f"[OK] agent scaffold created: {created}")
    return 0


def _cmd_run_agent(builder: AgnoTeamBuilder, args: argparse.Namespace) -> int:
    if args.dry_run:
        agent = builder.registry_loader.load_agent_manifest(args.team, args.agent)
        summary: dict[str, Any] = {
            "id": agent.id,
            "name": agent.name,
            "role": agent.role,
            "model": builder._resolve_model(agent.model),
            "tools": agent.tools,
        }
        print(json.dumps({"dry_run": True, "agent_summary": summary}, ensure_ascii=False, indent=2))
        return 0

    agent = builder.build_agent(args.team, args.agent)
    model = builder._resolve_model(builder.registry_loader.load_agent_manifest(args.team, args.agent).model)
    if not model:
        raise RuntimeError("运行 agent 前请提供模型（--model 或环境变量 AGNO_MODEL）。")
    response = agent.run(
        args.input,
        session_id=args.session_id,
        user_id=args.user_id,
    )
    print(_extract_content(response))
    return 0


def _ensure_model_for_run(summary: dict[str, Any]) -> None:
    if summary.get("model"):
        return
    for member in summary.get("members", []):
        if member.get("model"):
            return
    raise RuntimeError("运行 team 前请提供模型（--model 或环境变量 AGNO_MODEL）。")


def _extract_content(response: Any) -> str:
    content = getattr(response, "content", None)
    if content is None:
        return str(response)
    if isinstance(content, str):
        return content
    try:
        return json.dumps(content, ensure_ascii=False, indent=2)
    except TypeError:
        return str(content)


if __name__ == "__main__":
    raise SystemExit(main())
