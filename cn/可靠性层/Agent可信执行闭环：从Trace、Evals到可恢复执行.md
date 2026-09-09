# Agent 可信执行闭环：从 Trace、Evals 到可恢复执行

## 目标与边界

本章把可靠性层已有的 Trace、Evals、Checkpoint 和 Validator 主题串成一条可运行的执行闭环。唯一参考实现是离线的代码修复 Agent，输入、工具和结果都来自固定 fixture；阶段 1 不扩展到多 Agent Handoff、A2A、Context Engineering 或企业平台治理。

## 统一执行模型

一次任务按 `Goal -> Plan -> Tool Call -> Observation -> Validation -> Checkpoint -> Artifact` 推进。`Trace -> Span -> Event` 是唯一事件层级，事件至少包含 `trace_id`、`event_id`、`task_id`、`timestamp`、`event_type`、`name` 和 `status`。事件通过 `parent_event_id` 建立父子关系，`artifact://` 引用和 SHA-256 hash 用来保存大对象，日志中不写入密钥、令牌和个人数据。

参考契约：

- [代码修复 Agent 案例 README](../assets/examples/code-repair-agent/README.md)
- [Trace Event Schema](../assets/schemas/trace-event.md)
- [Checkpoint State Schema](../assets/schemas/checkpoint-state.yaml)
- [Eval Case Schema](../assets/schemas/eval-case.yaml)
- [Validator 决策表](../assets/checklists/validator-decision.md)
- [Regression Report 模板](../assets/checklists/regression-report.md)

## 可运行案例

代码修复 Agent 只读 `assets/examples/code-repair-agent/fixtures/repo_v1`，固定提供 `search_repo`、`run_tests`、`apply_patch` 和 `git_diff` 四个工具。它不会访问网络，也不会修改真实仓库；补丁、测试报告、Trace 和 Checkpoint 都写入运行目录。

```text
cd cn/assets/examples/code-repair-agent
python run_demo.py --scenario success --out ./artifacts
python run_demo.py --scenario tool-timeout --out ./artifacts
python run_demo.py --scenario validation-failed --out ./artifacts
python run_demo.py --scenario permission-denied --out ./artifacts
python run_demo.py --scenario duplicate-replay --out ./artifacts
```

成功运行会产生 `trace.jsonl`、`checkpoint.yaml`、`test-report.json` 和 `patch.diff`。阻断路径额外产生 `failure.json`；每个 Artifact 返回 URI、路径和 hash，便于审计与 Replay。

## Trace 与 Observation

Goal 和 Plan 说明任务意图及执行步骤；Tool Call 记录工具名、幂等键和边界；Observation 只保留可复现的结果引用；Validation 绑定测试退出码和证据；Checkpoint 在副作用前保存游标。最终 `final_output` 事件引用结果 Artifact，因此可以从一个 `trace_id` 找到完整执行链。

与已有专题的分工如下：

- [Agent 可观测性实战：从日志、Trace 到 Replay](Agent可观测性实战：从日志、Trace到Replay.md) 负责事件检索和 Replay 思路。
- [Agent 的可观测性实战：用 Tracing 看清你的 Agent“大脑”](Agent的可观测性实战：用Tracing看清你的Agent“大脑”.md) 负责 Span 与工具观测细节。
- [Agent 的自动化评估体系（Evals）](Agent的自动化评估体系（Evals）：从单元测试到集成评测.md) 负责评估分层与证据要求。
- [Agent 状态管理与断点续传](Agent状态管理与断点续传：Checkpointer机制深度解析.md) 负责游标、状态和幂等恢复。
- [Agent 自我纠错与验证机制](Agent自我纠错与验证机制设计.md) 负责 Validator 和失败归因。

## 四类失败恢复

### 输入不完整

缺少目标文件或测试命令时，任务进入 `input-required`，只写 Checkpoint 和失败 Artifact，不调用 `apply_patch`。补齐输入后从 `input_received` 游标继续，原 Trace 保持不变。

### 工具超时

工具事件标记 `failed` 并记录 `DEADLINE_EXCEEDED`。Runner 从最近 Checkpoint 进入 `retrying`，使用同一幂等键重试一次；再次失败后进入 `failed`，不产生补丁副作用，故障分类为 `tool_timeout`。

### 验证失败

补丁已经生成但测试退出码非零时，保留 `patch.diff`、`test-report.json` 和 `failure.json`，任务进入 `failed`，故障分类为 `validation_failed`。Validator 不能把缺失证据解释成成功，后续应回流对应 Eval Case。

### 权限拒绝与重复执行

越权路径、测试文件修改、外部命令或网络边界触发 `permission_denied`，立即阻断并等待人工处理。重复幂等键只读取已有结果；`duplicate-replay` 会复用原 Artifact，第二次调用的 `side_effect_count` 为零。

## Evals 与发布门禁

固定样本集包含 30 条 Eval Case：`normal` 10 条、`input_incomplete` 5 条、`tool_failure` 5 条、`high_risk` 5 条、`historical_regression` 5 条。批量执行复用同一个 `run_scenario` 入口：

```text
python run_evals.py --cases eval_cases.yaml --out ./eval-output
```

Runner 输出 `regression-report.json` 和 `regression-report.md`。报告同时记录分类计数、通过率、失败归因、Trace/Checkpoint 路径和副作用计数。高风险样本必须阻断或转人工；整体成功率相对基线下降超过 5 个百分点，或成本/延迟回归达到 20%，发布门禁为 `blocked`。

## 复用清单

1. 新任务先复用 `trace-event.md` 的 canonical 字段，再定义业务字段。
2. 副作用前写 `checkpoint.yaml`，恢复时依据幂等键跳过已成功步骤。
3. 每条 Eval Case 固定输入、工具 fixture、期望状态、禁止动作和 required evidence。
4. Validator 决策必须能回指 Trace 事件和最终 Artifact，并填写失败分类。
5. 发布前运行 30 条 Golden Set，审阅 `regression-report.md`，高风险路径不得静默放行。

## 验收结果

本章的命令、文件路径和字段均对应代码修复 Agent 的实际接口。先运行单场景 Trace，再运行批量 Evals，最后结合 Checkpoint 做 Replay；这样可以回答“任务做了什么、失败在哪一步、从哪里恢复、修复后是否回归”。
