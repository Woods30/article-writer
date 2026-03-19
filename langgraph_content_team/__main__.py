"""CLI entry point for the LangGraph content creation team."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Any

from .graph import build_graph, compile_graph
from .state import ContentState


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="langgraph_content_team",
        description="LangGraph 自媒体内容创作团队 — 多 Agent 协作系统",
    )
    p.add_argument(
        "--model",
        default="openai:gpt-4o-mini",
        help="覆盖所有角色的模型，如 openai:gpt-4o-mini（默认）。",
    )
    p.add_argument(
        "--openai-base-url",
        default=None,
        help="自定义 OpenAI Base URL。",
    )

    sub = p.add_subparsers(dest="command", required=True)

    # ── show-graph ──────────────────────────────────────────────
    sub.add_parser("show-graph", help="打印图结构（节点 + 边）")

    # ── validate ────────────────────────────────────────────────
    sub.add_parser("validate", help="校验图结构可编译")

    # ── run ──────────────────────────────────────────────────────
    p_run = sub.add_parser("run", help="运行内容创作流程")
    p_run.add_argument("--input", required=True, help="用户请求")
    p_run.add_argument(
        "--mode",
        choices=["A", "B", "C", "D"],
        default=None,
        help="强制指定模式（默认自动路由）",
    )
    p_run.add_argument(
        "--material",
        action="append",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="附带材料 --material research_report '报告内容'",
    )
    p_run.add_argument(
        "--dry-run",
        action="store_true",
        help="仅输出图结构和初始 state，不实际执行。",
    )

    return p


def _configurable(args: argparse.Namespace) -> dict[str, Any]:
    cfg: dict[str, Any] = {}
    if args.model:
        for role in ("planner_model", "writer_model", "researcher_model", "auditor_model"):
            cfg[role] = args.model
    if getattr(args, "openai_base_url", None):
        cfg["openai_base_url"] = args.openai_base_url
    return cfg


def cmd_show_graph() -> int:
    g = build_graph()
    compiled = g.compile()

    print("=== 图节点 ===")
    for node_name in compiled.get_graph().nodes:
        print(f"  • {node_name}")

    print("\n=== 图边 ===")
    for edge in compiled.get_graph().edges:
        print(f"  {edge[0]} → {edge[1]}")

    return 0


def cmd_validate() -> int:
    try:
        g = build_graph()
        compiled = g.compile()
        node_count = len(compiled.get_graph().nodes)
        edge_count = len(compiled.get_graph().edges)
        print(f"[OK] LangGraph 内容创作图编译成功 — {node_count} 个节点, {edge_count} 条边")
        return 0
    except Exception as exc:
        print(f"[ERROR] 图编译失败: {exc}", file=sys.stderr)
        return 1


def cmd_run(args: argparse.Namespace) -> int:
    materials: dict[str, Any] = {}
    if args.material:
        for k, v in args.material:
            materials[k] = v

    initial_state: ContentState = {
        "user_request": args.input,
        "materials": materials,
        "target_platforms": ["wechat", "xiaohongshu"],
        "constraints": [],
        "revision_count": 0,
        "messages": [],
    }
    if args.mode:
        initial_state["mode"] = args.mode

    configurable = _configurable(args)

    if args.dry_run:
        g = build_graph()
        compiled = g.compile()
        graph_info = compiled.get_graph()
        nodes = list(graph_info.nodes)
        edges = [(e[0], e[1]) for e in graph_info.edges]

        output = {
            "dry_run": True,
            "initial_state": {
                k: v for k, v in initial_state.items()
                if v is not None and v != [] and v != {}
            },
            "configurable": configurable,
            "graph": {
                "nodes": nodes,
                "edge_count": len(edges),
            },
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    graph = compile_graph()
    result = asyncio.run(
        graph.ainvoke(initial_state, config={"configurable": configurable})
    )

    print("\n" + "=" * 60)
    print("  内容创作完成")
    print("=" * 60)

    deliverables = result.get("final_deliverables", {})
    mode = deliverables.get("mode", "?")
    print(f"\n模式: {mode}")
    print(f"审核得分: {deliverables.get('audit_score', 'N/A')}")

    for key, value in deliverables.items():
        if key in ("mode", "audit_score"):
            continue
        if value:
            preview = str(value)[:300]
            print(f"\n--- {key} ---")
            print(preview)
            if len(str(value)) > 300:
                print(f"  ... (共 {len(str(value))} 字)")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "show-graph":
        return cmd_show_graph()
    if args.command == "validate":
        return cmd_validate()
    if args.command == "run":
        return cmd_run(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
