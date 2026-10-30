# riff-skills 项目交接

> 交接日期：2026-10-30
> 当前分支：`main`
> 用途：个人项目，不属于公司/BayDeer 工程规范仓库。

## 目标

riff-skills 是一个面向多种 coding agent 的、厂商中立的 Agent Skills 仓库。目标不是收集尽可能多的知识，而是把个人项目中 agent 容易遗漏、容易拍脑袋、容易过度设计的工程行为，沉淀成可触发、可执行、可评测的 skills。

目标 agent：

- Nyan
- Claude Code
- Codex
- Pi

Skill 必须遵循 [Agent Skills specification](https://agentskills.io/specification)，只使用规范 frontmatter，不依赖某一家厂商的工具名、环境变量或 slash command。

## 已确认的需求

- 技术选型要稳定、可靠，同时能识别真正有价值的新技术；不能因为流行或模型记忆就选型。
- 模块拆分必须适配项目结构、体量、团队和部署方式；规模化需要模块化，但不能提前微服务化或过度设计。
- API 需要可维护、可演进、兼容性清晰。
- 重大技术决策要主动形成 ADR，而不是只在对话里解释。
- 测试是核心交付物：修 bug 先写失败回归测试；改行为默认补测试；不能为了绿色测试偷偷改变生产语义。
- 代码审查和设计审查要项目感知、证据驱动、控制误报。
- AI 应用是重点：RAG、工具调用、Agent workflow、评测、成本、延迟、安全和回滚。
- 同时需要知识型 skill（相关任务自动加载）和任务型 skill（明确调用后按流程产出）。
- 原则是贵精不贵多，范围可以覆盖广，但每个 skill 都必须有明确行为价值。

## 当前 Skills

| Skill | 作用 |
|---|---|
| `authoring-skills` | 创建、拆分、压缩、规范化 Agent Skill |
| `evaluating-skills` | 静态审查、触发评测、输出 benchmark、版本比较 |
| `selecting-technologies` | 按项目约束和当前证据做技术选型 |
| `designing-modules` | 按项目规模设计模块边界，避免过早分布式化 |
| `designing-apis` | 设计可维护、可演进的 API 契约 |
| `writing-tests` | 回归测试、行为测试、flaky test、mutation 思维 |
| `writing-adrs` | 主动识别重大决策并写 ADR |
| `reviewing-code` | 正确性、测试、静默失败、安全、简化等代码审查 |
| `reviewing-designs` | 架构、ADR、RFC、模块/API 方案审查 |
| `building-llm-applications` | RAG、工具、workflow、eval、成本和生产安全 |

每个 skill 都有：

- `SKILL.md`
- 按需加载的 `references/`
- 可复制到项目 `AGENTS.md` 的 `assets/agents-snippet.md`
- `evals/evals.json`
- `evals/trigger-queries.json`

## 目录与校验

```text
.claude-plugin/marketplace.json   # 可选的 Claude Code marketplace 入口
skills/<name>/                     # 每个 skill 一个目录
scripts/validate.py                # 仓库级校验
sources/sdframe.yaml               # 上游素材到 skill 的裁剪映射
template/SKILL.md                  # 最小模板
docs/PROJECT_HANDOFF.md            # 本文件
docs/EVALUATION_RESULTS.md         # 已完成评测和限制
```

每次改动后建议执行：

```bash
python3 scripts/validate.py --strict
python3 -m py_compile scripts/*.py skills/*/scripts/*.py skills/*/evals/checks/*.py
```

CI 位于 `.github/workflows/validate.yml`，同时调用：

- `skills-ref==0.1.1` 的 Python API
- `scripts/validate.py`
- Python compile check

`.workspace/` 是评测工作区，已经加入 `.gitignore`，不要提交。它里面有 skill snapshot、sandbox、transcript 和 benchmark 中间文件。

## SDFrame 裁剪

素材来源：`Caldis/frameworks`，固定 commit：

```text
e519d0dd4d16be63b956fd35ab52fd6644840328
```

映射已经验证：

- 上游条目：317
- 已映射：317
- 重复：0
- 遗漏：0
- 未知 slug：0

`sources/sdframe.yaml` 是裁剪决策，不是自动生成内容。上游内容只作为素材；skill 正文应以一手资料重新核实，不能直接复制未验证的案例、采用者名单或时间线。

## 评测状态

已用 Pi 对两个试点做过 with-skill / without-skill benchmark：

- `writing-tests`：with-skill pass rate `1.00`，baseline `0.62`。
- `writing-adrs`：with-skill pass rate `0.94`，baseline `0.85`。

详细数据、解释和限制见 `docs/EVALUATION_RESULTS.md`。

重要：当前结果是方向性证据，不是统计学结论。每个 eval 只运行了两次，且使用 Pi 的默认模型配置；不同 agent/model 需要重新测量。

## 评测系统的已知事实

- Pi adapter：已验证。
- Claude Code-compatible adapter：已用本机 `cometix` 验证。
- Codex adapter：按官方 CLI 文档实现，本机没有 Codex CLI，尚未实跑。
- `run_evals.py` 使用独立 sandbox，并对 agent 终态 API 错误做重试。
- 429/rate-limit 运行不会再被当成 skill 质量失败；错误运行写入 `timing.json` 的 `error` 并从 benchmark 排除。
- grader 会读取工具调用日志，因此可以验证“先看到测试失败，再改生产代码”这类过程断言。
- tokens 只能在同一 agent/model 内比较；某些 agent 会把 cache read 算入 token 统计。

## 下一步顺序

1. 在家拉取后先运行校验：

   ```bash
   git pull --ff-only origin main
   python3 scripts/validate.py --strict
   ```

2. 阅读本文件和 `docs/EVALUATION_RESULTS.md`，再阅读 `skills/evaluating-skills/SKILL.md`。
3. 重新运行两个试点的 trigger eval，降低并发，避免模型端 rate limit：

   ```bash
   python3 skills/evaluating-skills/scripts/run_triggers.py \
     --skill skills/writing-tests --agent pi --set all --runs 3 --jobs 1
   python3 skills/evaluating-skills/scripts/run_triggers.py \
     --skill skills/writing-adrs --agent pi --set all --runs 3 --jobs 1
   ```

4. 调整 description 前先看 train/validation 结果，不要根据 validation 过拟合。
5. 对 `designing-modules`、`designing-apis`、`reviewing-code`、`selecting-technologies`、`reviewing-designs`、`building-llm-applications` 逐个跑静态检查和至少一轮 Pi benchmark。
6. 如果安装到个人项目，优先复制对应的 `assets/agents-snippet.md` 到项目自己的 `AGENTS.md`；skill 只在加载时生效，不能单独保证每次都触发。
7. Codex 可用后验证 `codex` adapter；如果事件格式不同，修改 `skills/evaluating-skills/scripts/agents.py` 和 `references/agents.md`，不要把 Codex 专用字段扩散进通用 skill 正文。

## 不要做的事

- 不要提交 `.workspace/`、agent session、缓存、密钥或全局配置。
- 未明确要求不要 commit/push 之外的远程操作，例如创建 PR、发布 marketplace release。
- 不要把 `CLAUDE.md`、Codex 配置或某个 agent 的专用字段写进通用 skill。
- 不要为了让 benchmark 变好而删除困难 eval；先检查 assertion 是否合理、agent 是否 rate limited、fixture 是否可执行。
- 不要把上游 SDFrame 的未核实事实当作项目事实。
