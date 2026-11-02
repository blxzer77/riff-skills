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

历史上已用 Pi 对两个试点做过 with-skill / without-skill benchmark：

- `writing-tests`：with-skill pass rate `1.00`，baseline `0.62`。
- `writing-adrs`：with-skill pass rate `0.94`，baseline `0.85`。

这些结果只作为历史方向性证据，不与当前 cometix/deepseek-flash 结果直接比较。详细数据、解释和限制见 `docs/EVALUATION_RESULTS.md`。

## 评测系统的已知事实

- 当前只用本机 `cometix` 运行评测，模型固定为 `deepseek-flash`；不做 Pi、Codex、Nyan 或跨 agent/model 对比。
- `cometix` 通过 Claude Code-compatible adapter 接入；评测时使用独立的 bwrap 包装，避免 agent 离开 sandbox 读取本机其他项目。
- `run_evals.py` 使用独立 sandbox，并对 agent 终态 API 错误做重试；每次 attempt 保留，成本统计包含所有 attempt。
- timeout、429/rate-limit、API error、invalid grading 和未加载 skill 的 with-run 不进入 treatment effect；它们分别记录在 `timing.json`/`benchmark.json`。
- grader 使用稳定 assertion ID，并读取 treated/baseline 元数据；无法可靠关联证据时 grading 标为 invalid。
- aggregate 只对同一 eval 的有效 with/baseline 配对结果计算 delta，并保留 requested/completed/retry/untreated/error 计数。
- tokens 只能在同一 agent/model 内比较；某些 agent 会把 cache read 算入 token 统计。

## 第二阶段状态

- 已按官方规范和最佳实践完成内容审查，并修正无条件规则、评测断言、review fixture 和测试 references。
- 已提交 treatment-aware harness：`ef6c8c5`。它区分 routing、treated body effect、baseline 和 infrastructure failure。
- treatment-aware 结果显示：`designing-apis`、`writing-adrs`、`writing-tests`、`authoring-skills`、`reviewing-code`、`building-llm-applications`、`designing-modules`、`reviewing-designs` 在关键 case 上有增益；`selecting-technologies` 正文增益尚未测出（见下）。
- 评测模型：`deepseek-flash`。2026-11-02 它一度触发月度上限，当天临时用 `claude-haiku-5-5` 跑了一批；同日 deepseek 短暂恢复，随后最小请求又返回 HTTP 500 `empty response content`。两个模型的结果不可直接比较；`docs/EVALUATION_RESULTS.md` 每节注明模型。恢复前不要启动新 eval。
- sandbox 包装脚本 `~/.cache/riff-skills/bin/cometix-sandboxed` 在登录用户变更后丢失过一次，已重建：只允许在 `~/.cache/riff-skills/runs/*/work` 和 grader 用的 `/tmp/riff-complete-*/work` 下运行。缺失时先重建再跑评测，不要裸跑 cometix。
- `designing-modules` 改用非 Anthropic 一手资料（Anthropic 没有模块边界方面的指导；来源见其 `references/sources.md`）。增益只集中在一个行为：边界只体现在代码约定、未写成文档时，通过公开 API 访问而不是越界 import internal（deepseek 上 baseline 6 次中 5 次越界，with-skill 6/6 正确）。haiku 上 trigger 18/20，0 误触发。
- `reviewing-designs` 按 Anthropic 审查设计重写，换成 4 个 fixture case（prompt 不点题）。haiku 上 0.98 vs 0.83：两边都能找出隐藏缺陷，差别在“健全设计给 approve”（with-skill 5/6，baseline 0/6）。成本约 +585k token/次。trigger 18/20。
- `selecting-technologies` 在 haiku 上：5 个 case baseline 全过（haiku 训练截止晚于这些事实）；case 6（仓库已固定一个 2026-09 弃用的模型）baseline 3/3 沿用，能区分，但 description 的排除条款让 skill 不被加载，正文效果未测。trigger 19/20，description 不改。
- trigger harness：agent 调用提问工具后在非交互模式下会被中止，这类运行现在计入路由结果，不再当作错误排除。
- trigger eval 现在支持 `fixture`：需要输入才能工作的 skill（审查代码、审查设计、写 ADR）必须在有真实输入的 sandbox 里测路由。`reviewing-code` 加 fixture 后为 20/20；空仓库下的 12/20 和更早的 16/20 都是环境造成的。
- `reviewing-code` 已按 Anthropic / Claude Code 官方审查设计重写（来源和 SHA 见 `skills/reviewing-code/references/sources.md`），eval 改为“真缺陷 + 官方 false-positive 诱饵”的配对 case 和机械检查；两轮独立复测均为约 0.85 vs 0.65。之前的“无增益”结论来自评测风格偏好的坏断言，已作废。
- `building-llm-applications` 已按 Anthropic 官方材料重写（building effective agents、writing tools、contextual retrieval、evals、injection 等，见其 `references/sources.md`）；eval 改为只提需求的 fixture case，由脚本运行产出的代码判定。两轮复测 1.00 vs 0.78 / 0.75，成本基本持平。旧的 4 个 case 在 prompt 里直接写了答案，已删除。
- 这些结论仍是每个 case 三次运行的方向性证据，不能泛化为 skill 的全部能力；详细结果和成本见 `docs/EVALUATION_RESULTS.md`。
- 不再根据旧的、未区分 treatment 的 benchmark 删除 skill；先换成真正能区分 baseline 的 case，再做移除决定。

## 下一步顺序

1. 在家拉取后先运行校验：

   ```bash
   git pull --ff-only origin main
   python3 scripts/validate.py --strict
   ```

2. 阅读本文件和 `docs/EVALUATION_RESULTS.md`，再阅读 `skills/evaluating-skills/SKILL.md`。
3. 其余 skill 按 `reviewing-code` 的方法重做：先找 Anthropic / Claude Code 团队对应的官方材料并钉住版本，再对照重写正文；eval 用“必须做到 + 不能做的诱饵”配对 case，判定优先机械检查，check 先做 good / near-miss / empty 三态校验。
4. `writing-tests`、`writing-adrs` 的 description 已在 deepseek 上用完整查询集对比过（当前 16/20、17/20，0 误触发；更 pushy 的候选各带来 1 个误触发、validation 无提升），保留当前版本。剩下的漏触发都是 agent 自己能直接做完的任务（重构、flaky 测试、加第二个 LLM provider 等），不要再靠加强 description 解决；需要每次都生效的项目用 `assets/agents-snippet.md`。
5. `selecting-technologies` 已有第 7 个 case：选择更便宜的 triage 模型时，报告仓库里已固定模型的退役状态。deepseek baseline 三次都没报告，旧 skill 三次都报告；当前正文改动为 2/3，仍不稳定。deepseek 恢复后重跑当前正文，若仍不能稳定超过 baseline，再把这条规则移入 `assets/agents-snippet.md`，并评估合并或移除该 skill。
6. 修复前记录的 trigger 结果都可能失真（空 sandbox、`ls` 误判为加载、提问运行被排除），以 2026-11-02 haiku 重测为准。
7. 改 skill 正文后用 `--baseline old_skill` 对比上一版；没有证明增量的改动如实标注，不要把方差当成效果。
8. 如果新 fixture 仍无法产生稳定 skill-only 增益（同时考虑成本和严重风险），将 skill 标记为候选移除或合并，而不是继续加规则。
9. 评测新 skill 前先跑静态检查，并确保 fixture、机械断言和 output eval 能区分 with/without；遇到 timeout 或 rate limit 时排除运行，不修改 skill。
10. 如果安装到个人项目，优先复制对应的 `assets/agents-snippet.md` 到项目自己的 agent instruction file；skill 只在加载时生效，不能单独保证每次都触发。
11. 不做 Pi、Codex、Nyan 或跨 agent/model 对比；如果以后改变评测政策，再单独更新本文件和评测结果说明。

## 不要做的事

- 不要提交 `.workspace/`、agent session、缓存、密钥或全局配置。
- 未明确要求不要 commit/push 之外的远程操作，例如创建 PR、发布 marketplace release。
- 不要把某个 agent 的专用配置、工具名、环境变量或字段写进通用 skill。
- 不要为了让 benchmark 变好而删除困难 eval；先检查 assertion 是否合理、agent 是否 rate limited、fixture 是否可执行。
- 不要把上游 SDFrame 的未核实事实当作项目事实。
