#!/usr/bin/env python3
"""Install content-creation-team bundle into an existing OpenClaw workspace."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install content-creation-team into OpenClaw."
    )
    parser.add_argument(
        "--openclaw-home",
        required=True,
        help="OpenClaw 根目录路径。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="目标目录已存在时强制覆盖。",
    )
    parser.add_argument(
        "--target-dir",
        default="teams",
        help="团队安装目录（相对于 openclaw-home，默认 teams）。",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def register_team(openclaw_home: Path, team_install_path: Path, team_meta: dict[str, Any]) -> None:
    index_path = openclaw_home / "teams" / "index.json"
    if index_path.exists():
        index_data = load_json(index_path)
    else:
        index_data = {"teams": []}

    if "teams" not in index_data or not isinstance(index_data["teams"], list):
        index_data["teams"] = []

    relative_path = str(team_install_path.relative_to(openclaw_home))
    team_id = team_meta["team_id"]
    existing = [item for item in index_data["teams"] if item.get("team_id") == team_id]

    if existing:
        existing[0].update(
            {
                "name": team_meta["name"],
                "path": relative_path,
                "public_agent_id": team_meta["public_agent_id"],
                "version": team_meta["version"],
            }
        )
    else:
        index_data["teams"].append(
            {
                "team_id": team_id,
                "name": team_meta["name"],
                "path": relative_path,
                "public_agent_id": team_meta["public_agent_id"],
                "version": team_meta["version"],
            }
        )

    save_json(index_path, index_data)


def copy_bundle(source_root: Path, target_root: Path, force: bool) -> None:
    if target_root.exists():
        if not force:
            raise FileExistsError(
                f"目标目录已存在: {target_root}。如需覆盖，请加 --force。"
            )
        shutil.rmtree(target_root)

    shutil.copytree(
        source_root,
        target_root,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )


def main() -> int:
    args = parse_args()
    openclaw_home = Path(args.openclaw_home).expanduser().resolve()
    if not openclaw_home.exists():
        print(f"[ERROR] openclaw-home 不存在: {openclaw_home}", file=sys.stderr)
        return 1

    source_root = Path(__file__).resolve().parents[1]
    team_meta = load_json(source_root / "team.json")

    install_base = openclaw_home / args.target_dir
    install_base.mkdir(parents=True, exist_ok=True)
    target_root = install_base / team_meta["team_id"]

    copy_bundle(source_root, target_root, args.force)
    register_team(openclaw_home, target_root, team_meta)

    print("[OK] 团队安装完成")
    print(f"- openclaw-home: {openclaw_home}")
    print(f"- install-path:  {target_root}")
    print(f"- public-agent:  {team_meta['public_agent_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
