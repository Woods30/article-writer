#!/usr/bin/env python3
"""Validate content-creation-team bundle integrity."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"JSON 解析失败: {path}: {exc}") from exc


def expect_file(path: Path, errors: list[str]) -> None:
    if not path.exists() or not path.is_file():
        errors.append(f"缺少文件: {path}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    team_path = root / "team.json"
    expect_file(team_path, errors)
    if errors:
        print("\n".join(f"[ERROR] {e}" for e in errors))
        return 1

    team = load_json(team_path)
    agent_ids = set(team.get("agents", []))
    if not agent_ids:
        errors.append("team.json 未声明 agents")

    # Validate agent files and references.
    agent_dir = root / "agents"
    agent_files = list(agent_dir.glob("*.json"))
    seen_agents: set[str] = set()

    for path in agent_files:
        data = load_json(path)
        agent_id = data.get("id")
        if not agent_id:
            errors.append(f"agent 文件缺少 id: {path}")
            continue
        seen_agents.add(agent_id)

        prompt_file = data.get("prompt_file")
        if prompt_file:
            expect_file(root / prompt_file, errors)

        input_schema = data.get("input_schema")
        if input_schema:
            expect_file(root / input_schema, errors)

        output_schema = data.get("output_schema")
        if output_schema:
            expect_file(root / output_schema, errors)

    missing_agent_files = sorted(agent_ids - seen_agents)
    if missing_agent_files:
        errors.append(f"team.json 中声明但缺少定义文件的 agent: {missing_agent_files}")

    # Validate workflows.
    workflow_paths = team.get("workflows", [])
    for wf in workflow_paths:
        wf_path = root / wf
        expect_file(wf_path, errors)
        if not wf_path.exists():
            continue
        wf_data = load_json(wf_path)
        for step in wf_data.get("steps", []):
            agent = step.get("agent")
            if agent and agent not in agent_ids:
                errors.append(f"workflow 引用了未知 agent: {wf_path} -> {agent}")

    # Validate router.
    router_rel = team.get("workflow_router")
    if router_rel:
        router_path = root / router_rel
        expect_file(router_path, errors)
        if router_path.exists():
            router_data = load_json(router_path)
            for route in router_data.get("routes", []):
                wf_rel = route.get("workflow")
                if wf_rel:
                    expect_file(root / wf_rel, errors)

    if errors:
        print("\n".join(f"[ERROR] {e}" for e in errors))
        return 1

    print("[OK] bundle 校验通过")
    print(f"- root: {root}")
    print(f"- agents: {len(agent_files)}")
    print(f"- workflows: {len(workflow_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
