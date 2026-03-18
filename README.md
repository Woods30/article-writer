# article-writer

本仓库现在包含两种形态：

1. **OpenClaw JSON 团队包**（历史版本）
   - 路径：`openclaw_content_team/`
2. **Agno 可运行 Team Registry（推荐）**
   - 运行时：`agno_runtime/`
   - 注册表：`agno_registry/`

---

## 使用 Agno 运行多 Team / 多 Agent

### 1) 安装依赖

```bash
python3 -m pip install -r requirements-agno.txt
```

> 如果你用 OpenAI 模型，还需要：
>
> ```bash
> python3 -m pip install openai
> export OPENAI_API_KEY=你的key
> ```

### 云环境自动预装（Cursor Cloud Agent）

仓库已新增：
- `.cursor/environment.json`
- `.cursor/install.sh`
- `requirements-agno-providers-optional.txt`

新机器启动时会自动执行：
1. `pip install -r requirements-agno.txt`
2. `pip install -r requirements-agno-providers-optional.txt`（当前包含 `openai`）
3. `python3 -m agno_runtime --registry-root agno_registry validate`

### 2) 校验 registry

```bash
python3 -m agno_runtime --registry-root agno_registry validate
```

### 3) 列出可用 team / agent

```bash
python3 -m agno_runtime --registry-root agno_registry list-teams
python3 -m agno_runtime --registry-root agno_registry list-agents --team content-creation-team
```

### 4) 干跑（不调用模型）

```bash
python3 -m agno_runtime --registry-root agno_registry --model openai:gpt-4o-mini \
  run-team --team content-creation-team --input "帮我从选题开始创作一篇文章" --dry-run
```

### 5) 真正执行 team

```bash
python3 -m agno_runtime --registry-root agno_registry --model openai:gpt-4o-mini \
  run-team --team content-creation-team --input "帮我从选题开始创作一篇关于AI效率工具的双平台文章"
```

### 6) 按需执行单个 agent

```bash
python3 -m agno_runtime --registry-root agno_registry --model openai:gpt-4o-mini \
  run-agent --team content-creation-team --agent platform_adapter --input "把这篇公众号文章改写成小红书版本"
```

---

## 后续扩展：新增 team 或 agent

### 新增 team 骨架

```bash
python3 -m agno_runtime --registry-root agno_registry scaffold-team --team growth-team --name "增长团队"
```

### 新增 agent 骨架

```bash
python3 -m agno_runtime --registry-root agno_registry scaffold-agent \
  --team growth-team --agent experiment_designer --name "实验设计师" --role strategist
```

创建后填充以下文件即可被自动发现并执行：
- `team.yaml` / `TEAM.md`
- `agent.yaml` / `AGENT.md` / `SOUL.md`
- `skills/*.md` / `memory/*.md`

---

## OpenClaw JSON 包（可选）

- 文档：`openclaw_content_team/README.md`
- 校验：`python3 openclaw_content_team/scripts/validate_bundle.py`
- 安装：`python3 openclaw_content_team/installer/install_to_openclaw.py --openclaw-home <你的OpenClaw目录> --force`
