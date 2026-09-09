# 代码修复 Agent 案例线

## 定位

这是本系列的技术验证案例，用于贯穿 Goal、Plan、Tool Call、Observation、Validation、Trace、Evals、Checkpoint、Replay、成本和失败恢复。案例默认运行在固定仓库 fixture 和无网络沙箱中。

## 用户目标

根据 Issue 定位根因，生成最小可审查补丁，运行目标测试并交付可验证、可回滚的修复结果；Agent 不得通过修改测试断言来制造通过。

## 最小流程

```text
用户提交 Issue
  -> Agent 生成修复计划
  -> 检索代码并运行固定测试
  -> 修改生产代码
  -> 保存 Checkpoint
  -> Validator 检查补丁、测试和权限
  -> 失败则恢复、重试或重规划
  -> 生成补丁、测试报告和 Trace Artifact
```

## 输入

Issue 描述、仓库 fixture、目标文件或模块（可选）和目标测试命令。

## 工具

| 项目 | 固定定义 |
| --- | --- |
| 工具 | `search_repo`、`run_tests`、`apply_patch`、`git_diff` |
| 权限边界 | 可读仓库；只能写生产代码目录；禁止修改测试断言和访问网络 |
| 追踪字段 | `trace_id`、`task_id`、`event_id`、`parent_event_id`、`checkpoint_id` |
| 终止条件 | 测试通过且 Validator 通过，或达到重试上限并升级人工 |

## 状态

`submitted` -> `working` -> `validating` -> `completed`，也可能进入 `input-required`、`retrying`、`waiting-confirmation`、`failed` 或 `cancelled`。Checkpoint 记录这些任务状态，不另造 `checkpointed` 状态。

## 风险动作

- 修改文件、运行测试和生成补丁都必须在仓库 fixture 与权限范围内。
- 触及测试、依赖锁文件、凭据或网络边界时立即拒绝并升级人工。
- 合并、提交 PR、发布或删除文件不属于阶段 0 自动动作，必须由人工确认。

## 最终 Artifact

- `patch.diff`：最小代码补丁及内容 hash。
- `test-report.json`：命令、退出码、耗时和失败摘要。
- `trace.jsonl`：按统一 Trace Event 模板记录的执行轨迹。
- `checkpoint.yaml`：可恢复游标、幂等键和失败原因。

最终交付是补丁、测试报告、验证结论和执行轨迹组成的 Artifact 包；测试未通过或 Validator 未通过时，不得标记为可交付修复。

## 必测失败路径

1. 输入缺少目标文件或测试命令：转 `input-required`，不修改工作区。
2. 测试工具超时或返回非零：记录工具错误，按 Checkpoint 重试，禁止盲目重复写入。
3. 补丁触及测试或越过权限范围：Validator 拒绝并记录 `permission_denied`，升级人工。

## 阶段 0 使用方式

阶段 0 先固定场景、权限和 Artifact 名称。阶段 1 再接入统一 Trace、Eval Case、Checkpoint 和可重复运行的 fixture。

## 复用指导

新文章优先复用本案例的 Goal、Plan、Tool Call、Observation、Validation、Checkpoint 和 Artifact 字段；可观测性专题使用 `trace.jsonl`，评估专题使用 `test-report.json` 与固定 fixture，状态管理专题沿用 `checkpoint.yaml`。任何新失败路径都应能映射到状态、事件和最终 Artifact。
## Stage 1 deterministic runner

Run from this directory with Python 3.10+:

```text
python run_demo.py --scenario success --out ./artifacts
python run_demo.py --scenario input-required --out ./artifacts
python run_demo.py --scenario tool-timeout --out ./artifacts
python run_demo.py --scenario validation-failed --out ./artifacts
python run_demo.py --scenario permission-denied --out ./artifacts
python run_demo.py --scenario duplicate-replay --out ./artifacts
```

Each invocation is offline and reads only `fixtures/repo_v1`. Results are
written below `artifacts/<run-id>/`: `trace.jsonl`, `checkpoint.yaml`,
`goal.json`, `search.json`, `test-report.json`, `patch.diff`, and (for blocked
paths) `failure.json`.
Artifact records contain an `artifact://` reference and SHA-256 hash. The
`duplicate-replay` scenario emits the original patch once and reuses it on the
replay, so its side-effect count remains one.
