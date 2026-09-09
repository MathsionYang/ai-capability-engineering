# AI 能力工程：从 Skill、MCP 到 Agent

> 构建可复用、可调用、可验证的 AI 执行系统。
> 让模型吸收不确定性，让系统约束不确定性。

## 核心问题

本系列围绕一个核心问题展开：

> **如何把专家经验、外部工具和大模型推理能力，组合成稳定、可治理、可验证的 AI 系统？**

整套内容以 **Skill → MCP → Agent** 为主线：

| 层 | 回答的问题 |
| :--- | :--- |
| **Skill（方法层）** | 任务应该怎么稳定完成 |
| **MCP（能力层）** | 外部工具、资源和系统如何被 AI 稳定调用 |
| **Agent（执行层）** | 谁来理解目标、制定计划、调用工具、验证结果并持续调整 |

## 阶段 0 资产入口

- [知识地图与文章-能力-资产矩阵](assets/knowledge-map.md)：查看六层阅读顺序、文章依赖、已有资产、缺口和下一步动作。
- [采购 / 合同审批 Agent 案例线](assets/examples/procurement-agent/README.md)：业务主案例，覆盖权限、人工确认和多 Agent 协作。
- [代码修复 Agent 案例线](assets/examples/code-repair-agent/README.md)：技术验证案例，覆盖 Trace、Evals、Checkpoint 和失败恢复。
- [Trace Event 模板](assets/schemas/trace-event.md)、[Eval Case 模板](assets/schemas/eval-case.yaml)、[Checkpoint State 模板](assets/schemas/checkpoint-state.yaml)、[Permission Matrix 模板](assets/checklists/permission-matrix.md)：统一 Trace、评估、状态和权限字段。

## 六层阅读顺序

按下面的顺序阅读，可以从方法和能力基础逐步走到可运行、可协作、可治理的 Agent 系统：

1. **基础层**：Skill、MCP、模型效率与 Agent 第一性原理。
2. **执行层**：工程闭环、规划、任务拆解与记忆。
3. **可靠性层**：可观测性、验证、Evals、状态恢复与 Replay。
4. **协作层**：多 Agent 拓扑、A2A、任务交接与 Artifact。
5. **安全层**：权限、提示注入防护、人工确认与审计。
6. **生产治理层**：上下文、成本延迟、Owner、评估、发布与生命周期。

完整的文章-能力-资产关系见 [AI 能力工程知识地图与资产矩阵](assets/knowledge-map.md)。

两条固定案例线见 [采购 / 合同审批 Agent](assets/examples/procurement-agent/README.md) 和 [代码修复 Agent](assets/examples/code-repair-agent/README.md)。

## 文章索引（按知识链路）

### 总纲

- [AI 能力工程：从 Skill、MCP 到 Agent](总纲/AI能力工程：从Skill、MCP到Agent.md)

### Skill 方法层

- [Skill 设计方法论：从专家经验到可复用能力](基础层/Skill设计方法论：从专家经验到可复用能力.md)
- [从 Prompt 到 Skill：专家经验的标准化封装指南](基础层/从Prompt到Skill：专家经验的标准化封装指南.md)

### MCP 能力层

- [MCP 的第一性原理：从工具调用到能力协议](基础层/MCP的第一性原理：从工具调用到能力协议.md)

### 模型效率

- [模型量化与蒸馏：原理、取舍与可跑实例](基础层/模型量化与蒸馏：原理、取舍与可跑实例.md)

### Agent 基础

- [Agent 的第一性原理：从概念到范式演进](基础层/Agent的第一性原理：从概念到范式演进.md)
- [Agent 工程实践指南：从最小闭环到生产级系统](执行层/Agent工程实践指南：从最小闭环到生产级系统.md)

### 执行能力

- [Agent 规划范式进化论：从 CoT 到 Plan-and-Execute](执行层/Agent规划范式进化论：从CoT到Plan-and-Execute.md)
- [Agent 的任务拆解艺术：从目标到可执行子任务](执行层/Agent的任务拆解艺术：从目标到可执行子任务.md)
- [Agent 记忆系统设计：从上下文管理到长期经验复用](执行层/Agent记忆系统设计：从上下文管理到长期经验复用.md)

### 可靠性层

- [Agent 可观测性实战：从日志、Trace 到 Replay](可靠性层/Agent可观测性实战：从日志、Trace到Replay.md)
- [Agent 的可观测性实战：用 Tracing 看清你的 Agent“大脑”](可靠性层/Agent的可观测性实战：用Tracing看清你的Agent“大脑”.md)
- [Agent 状态管理与断点续传：Checkpointer 机制深度解析](可靠性层/Agent状态管理与断点续传：Checkpointer机制深度解析.md)
- [Agent 自我纠错与验证机制设计：从自信回答到可验证执行](可靠性层/Agent自我纠错与验证机制设计.md)
- [Agent 的自动化评估体系（Evals）：从单元测试到集成评测](可靠性层/Agent的自动化评估体系（Evals）：从单元测试到集成评测.md)

> 可观测性阅读顺序：先读[从日志、Trace 到 Replay](可靠性层/Agent可观测性实战：从日志、Trace到Replay.md)总论，再读[用 Tracing 看清你的 Agent“大脑”](可靠性层/Agent的可观测性实战：用Tracing看清你的Agent“大脑”.md)专题。

其中，《Agent 可观测性实战：从日志、Trace 到 Replay》是可观测性总论，定义执行证据链、Replay 与治理边界；《Agent 的可观测性实战：用 Tracing 看清你的 Agent“大脑”》是 Trace 专题，深入 Trace / Span / Event 埋点与排障。先读总论，再读专题。

### 协作编排

- [多 Agent 协作模式深度解析：层级、流水线与群组](协作层/多Agent协作模式深度解析：层级、流水线与群组.md)
- [从 MCP 到 A2A：解读 Agent 互联协议的未来](协作层/从MCP到A2A：解读Agent互联协议的未来.md)
  讲清 A2A 如何把多个 Agent 连成可发现、可委派、可回传的协作网络，重点放在 Agent Card、Task / Message、Artifact 以及与 MCP 的配合。

### 安全治理

- [Agent 安全护栏设计：权限控制、对抗鲁棒性与人工确认环](安全层/Agent安全护栏设计：权限控制、对抗鲁棒性与人工确认环.md)

### 生产治理层

- [生产治理层](生产治理层/index.md)

## 推荐阅读顺序

- **快速建立认知**：总纲 → Agent 第一性原理 → Agent 工程实践指南
- **开发 MCP Server**：总纲 → Skill 设计方法论 → MCP 第一性原理 → Agent 可观测性实战
- **模型压缩**：MCP 第一性原理 → 模型量化与蒸馏
- **生产级 Agent**：按知识链路 1 → 2 → … → 生产治理完整阅读


## 路线文档

- [路线文档](路线/index.md)

## 发布主页

- CSDN：[https://blog.csdn.net/sinat_28228747?type=blog](https://blog.csdn.net/sinat_28228747?type=blog)
- 掘金：[https://juejin.cn/user/3647513603343131/posts](https://juejin.cn/user/3647513603343131/posts)
## Stage 1 trusted execution loop

- [Agent trusted execution loop](可靠性层/Agent可信执行闭环：从Trace、Evals到可恢复执行.md)
- [Code repair Runner and Eval Set](assets/examples/code-repair-agent/README.md)
- [Validator decision](assets/checklists/validator-decision.md) and [regression report](assets/checklists/regression-report.md)
