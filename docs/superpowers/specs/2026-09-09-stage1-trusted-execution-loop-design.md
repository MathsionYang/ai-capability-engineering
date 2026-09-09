# 阶段 1：可信执行闭环设计规格

## 目标

把现有可观测性、Evals、Checkpointer 和自我纠错文章串成一条可以演示、回放和回归的代码修复 Agent 执行链。阶段 1 的交付物必须能够回答：任务做了什么、失败在哪一步、从哪里恢复、修复后是否退化。

## 范围

本阶段覆盖：

1. 统一 `Trace -> Span -> Event` 事件层级和 canonical 字段。
2. 统一任务状态、Checkpoint、幂等键、恢复和失败分类。
3. 新增《Agent 可信执行闭环：从 Trace、Evals 到可恢复执行》整合文章。
4. 在固定仓库 fixture 和无网络环境中提供最小代码修复 Agent 参考实现。
5. 提供 30 条固定 Eval Case：10 条正常、5 条缺参、5 条工具失败/超时、5 条高风险/权限不足、5 条历史回归。
6. 将阶段 1 资产加入 README、中文入口、MkDocs 导航和路线 Checklist。

不在本阶段实现多 Agent Handoff、A2A、Context Engineering、成本平台或企业能力目录；这些属于阶段 2/3。

## 设计决策

### 统一执行模型

参考案例只处理一个代码修复任务，执行步骤固定为：

```text
Goal
  -> Plan
  -> Tool Call
  -> Observation
  -> Validation
  -> Checkpoint
  -> Artifact
```

每个事件至少包含 `trace_id`、`event_id`、`task_id`、`timestamp`、`event_type`、`name` 和 `status`。事件通过 `parent_event_id` 组成 Span 内层级；`trace_id` 贯穿 Agent、工具和验证步骤。大对象使用 `artifact://` 引用并保留 hash，不直接写入事件。

事件类型固定为 `goal`、`plan`、`tool_call`、`observation`、`validation`、`checkpoint`、`human_confirmation` 和 `final_output`。状态固定为 `started`、`succeeded`、`failed`、`skipped` 和 `waiting`。

### 状态与恢复

参考实现使用以下任务状态：

```text
submitted -> working -> validating -> completed
                     |           |
                     v           v
                  retrying     failed
                     |           |
                     +--> working
```

`input-required`、`waiting-confirmation` 和 `cancelled` 是可从任一步骤进入的终态或暂停态。Checkpoint 保存 `task_id`、状态、游标、已完成步骤、输入/输出 Artifact、side effects、幂等键、重试次数和失败原因。恢复必须依据幂等键跳过已经成功的副作用步骤。

### 失败分类与恢复策略

| 分类 | 观测信号 | 处理策略 | 是否回归样本 |
| --- | --- | --- | --- |
| 输入不完整 | 缺少目标文件或测试命令 | `input-required`，不修改工作区 | 是 |
| 工具超时/异常 | 工具事件 `failed`，含错误码和耗时 | 从最近 Checkpoint 重试，达到上限后升级 | 是 |
| 验证失败 | 测试非零或 Validator 拒绝 | 保存失败 Artifact，重规划或人工接管 | 是 |
| 权限/风险 | 越权路径、测试被修改、网络调用 | `permission_denied`，立即阻止 | 是 |
| 重复执行 | 幂等键冲突或重复副作用 | 返回已有结果，不重复写入 | 是 |

### Evals 与发布门禁

每条 Eval Case 使用固定输入、固定工具 fixture、期望状态路径、禁止动作、必需证据、最终 Artifact 和 rubric。评估器输出通过/失败、失败分类、Trace 引用和版本信息。初始门禁为：高风险样本全部阻止或转人工；关键工具和最终验证可追踪；总体成功率较基线下降不得超过 5 个百分点；成本或延迟回归达到 20% 时阻止发布并记录原因。

## 文件与接口

| 文件 | 职责 |
| --- | --- |
| `cn/assets/schemas/trace-event.md` | canonical Trace/Span/Event 字段、事件类型、最小示例和脱敏约束 |
| `cn/assets/schemas/checkpoint-state.yaml` | 状态、游标、幂等、恢复和失败字段 |
| `cn/assets/schemas/eval-case.yaml` | 单条 Eval Case 字段和最小示例 |
| `cn/assets/checklists/validator-decision.md` | Validator 触发、失败分类、重试/重规划/人工升级决策 |
| `cn/assets/checklists/regression-report.md` | 基线对比、失败归因、成本/延迟门禁记录 |
| `cn/assets/examples/code-repair-agent/` | 固定 fixture、确定性工具、Runner 和输出 Artifact |
| `cn/assets/examples/code-repair-agent/eval_cases.yaml` | 30 条固定评估样本 |
| `cn/可靠性层/Agent可信执行闭环：从Trace、Evals到可恢复执行.md` | 跨文章整合说明和运行结果 |

参考实现的命令接口为：

```text
python run_demo.py --scenario success
python run_demo.py --scenario tool-timeout
python run_demo.py --scenario validation-failed
python run_demo.py --scenario permission-denied
python run_evals.py --cases eval_cases.yaml --out report.json
```

每次运行写出 `artifacts/<run_id>/trace.jsonl`、`checkpoint.yaml`、`test-report.json`、`patch.diff` 或失败说明；Runner 不访问网络，并且工具返回来自本地 fixture。

## 验收标准

1. 整合文章引用五篇已有专题、两个固定案例和四个阶段 0 模板。
2. 成功和四类失败场景都能生成可解析 JSONL Trace，并能按 `trace_id` 找到对应事件。
3. 中断后可以从明确的 Checkpoint 游标恢复，已完成步骤不会产生重复副作用。
4. 30 条 Eval Case 数量和分类准确，Runner 可重复执行并输出统一报告。
5. 高风险样本不会静默放行，权限失败含 `permission_denied` 证据。
6. 新旧版本可使用同一批 Case 比较成功率、失败分类、成本和延迟。
7. 文章、案例、模板、Eval 数据和导航之间的相对链接全部有效，MkDocs 严格构建成功。

## 验证策略

- 对 YAML 模板和 Eval 数据执行解析与分类计数校验。
- 对 Runner 编写测试，覆盖成功、输入缺失、工具超时、验证失败、权限拒绝、Checkpoint 恢复和幂等重复执行。
- 对每个场景检查 Trace 事件顺序、状态终点和 Artifact 文件。
- 使用相同 fixture 连续运行两次，确认结果、事件类型和失败分类稳定。
- 执行 Markdown 相对链接检查、`git diff --check` 和 `python -m mkdocs build --strict --clean`。
