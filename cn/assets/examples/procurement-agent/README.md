# 采购 / 合同审批 Agent 案例线

## 定位

这是本系列的业务主案例，用于贯穿权限、人工确认、任务委派、多 Agent、A2A 和 Artifact。案例中的采购单、合同文本和供应商资料均使用脱敏或固定 fixture，不能直接连接真实审批系统。

## 用户目标

根据采购需求和合同证据，生成可复核的条款摘要与风险报告，并在需要时发起人工审批；Agent 不直接替代审批人。

## 最小流程

```text
用户提交采购需求
  -> 主管 Agent 拆解合同审查任务
  -> 合同分析 Agent 提取付款、交付和违约条款
  -> 风险审查 Agent 复核风险并生成风险报告
  -> 主管 Agent 汇总证据
  -> 高风险动作转人工审批
  -> 生成可审计 Artifact
```

## 输入

采购目的、预算上限、供应商标识、合同文本引用，以及可选的审批规则版本。

## 工具

| 项目 | 固定定义 |
| --- | --- |
| 协作 Agent | `procurement-supervisor`、`contract-reviewer`、`risk-reviewer` |
| 工具 | 合同读取、条款抽取、风险规则检查、审批提交（默认关闭） |
| 权限边界 | 读取当前采购单；写入审查报告；提交审批必须人工确认 |
| 追踪字段 | `context_id`、`task_id`、`parent_task_id`、`trace_id`、`artifact_id` |

## 状态

`submitted` -> `working` -> `input-required`（资料不足时）或 `awaiting-human-confirmation`（高风险动作前） -> `completed` / `failed` / `cancelled`。

## 风险动作

- 提交采购审批、发送合同或触发付款等不可逆动作默认关闭。
- 预算、供应商身份、权限范围或高风险条款未通过校验时，必须阻止动作并转人工。
- 所有阻止、确认和审批结果都写入审计记录，并关联 `trace_id` 与 Artifact。

## 最终 Artifact

- `contract-summary-v1`：关键条款及证据引用。
- `risk-report-v1`：风险等级、触发规则、证据和建议动作。
- `approval-request-v1`：待人工确认的审批请求，不代表已提交。

最终交付是包含证据引用、风险结论、审批状态和审计关联的 Artifact 包；`approval-request-v1` 只有在人工确认后才能进入真实审批系统。

## 必测失败路径

1. 合同文本缺失或供应商标识不完整：状态为 `input-required`，不得调用审批工具。
2. 风险审查 Agent 超时或不可用：主管 Agent 保留原任务状态，按 Handoff 契约重试或升级人工。
3. 发现高风险付款或越权请求：记录 `permission_denied`，阻止不可逆动作并要求人工确认。

## 阶段 0 使用方式

阶段 0 只固定案例边界和字段，不要求连接真实系统。阶段 2 再补充 Agent Card、Handoff、Task、Message 和 Artifact 的可运行演示。

## 复用指导

新文章优先复用本案例的角色、状态、权限边界和 Artifact 名称；讲协作时沿用三类 Agent，讲安全时沿用人工确认门，讲评估时使用缺参、超时和越权三条失败路径。新增字段先更新本页，再同步到统一模板。
