# AI 能力工程：从 Skill、MCP 到 Agent

> 构建可复用、可调用、可验证的 AI 执行系统。

中文资料统一入口。文章原稿集中在 [`articles/`](articles/)，层级归属和阶段交付状态见 [文章目录说明](articles/README.md)。

## 先看这里

- [文章目录说明](articles/README.md)：解释基础层、执行层、可靠性层、协作层、安全层和生产治理层的边界，并标记各阶段交付物。
- [知识地图与文章-能力-资产矩阵](assets/knowledge-map.md)：查看文章依赖、案例、模板、缺口和下一步动作。
- [路线文档](路线/index.md)：查看实施路线、执行 Checklist、写作规划和发布资料。
- [生产治理层说明](生产治理层说明.md)：查看生产治理阶段的当前缺口和后续方向。

## 统一资产

- [采购 / 合同审批 Agent](assets/examples/procurement-agent/README.md)：业务主案例，覆盖权限、人工确认和多 Agent 协作。
- [代码修复 Agent](assets/examples/code-repair-agent/README.md)：技术验证案例，覆盖 Trace、Evals、Checkpoint 和失败恢复。
- [Trace Event Schema](assets/schemas/trace-event.md)
- [Eval Case Schema](assets/schemas/eval-case.yaml)
- [Checkpoint State Schema](assets/schemas/checkpoint-state.yaml)
- [Permission Matrix](assets/checklists/permission-matrix.md)

## 阅读链路

1. **总纲**： [AI 能力工程：从 Skill、MCP 到 Agent](articles/AI能力工程：从Skill、MCP到Agent.md)
2. **基础层**： [Skill 设计方法论](articles/Skill设计方法论：从专家经验到可复用能力.md) -> [从 Prompt 到 Skill](articles/从Prompt到Skill：专家经验的标准化封装指南.md) -> [MCP 第一性原理](articles/MCP的第一性原理：从工具调用到能力协议.md) -> [Agent 第一性原理](articles/Agent的第一性原理：从概念到范式演进.md)
3. **执行层**： [Agent 工程实践指南](articles/Agent工程实践指南：从最小闭环到生产级系统.md) -> [规划范式进化论](articles/Agent规划范式进化论：从CoT到Plan-and-Execute.md) -> [任务拆解艺术](articles/Agent的任务拆解艺术：从目标到可执行子任务.md) -> [记忆系统设计](articles/Agent记忆系统设计：从上下文管理到长期经验复用.md)
4. **可靠性层**： [可观测性总论](articles/Agent可观测性实战：从日志、Trace到Replay.md) -> [Tracing 专题](articles/Agent的可观测性实战：用Tracing看清你的Agent“大脑”.md) -> [自动化评估体系](articles/Agent的自动化评估体系（Evals）：从单元测试到集成评测.md) -> [状态管理与断点续传](articles/Agent状态管理与断点续传：Checkpointer机制深度解析.md) -> [自我纠错与验证](articles/Agent自我纠错与验证机制设计.md) -> [可信执行闭环](articles/Agent可信执行闭环：从Trace、Evals到可恢复执行.md)
5. **协作层**： [多 Agent 协作模式](articles/多Agent协作模式深度解析：层级、流水线与群组.md) -> [从 MCP 到 A2A](articles/从MCP到A2A：解读Agent互联协议的未来.md)
6. **安全层**： [Agent 安全护栏设计](articles/Agent安全护栏设计：权限控制、对抗鲁棒性与人工确认环.md)
7. **生产治理层**： [生产治理层说明](生产治理层说明.md)

## 阶段状态

| 阶段 | 目标 | 状态 | 主要入口 |
| :--- | :--- | :--- | :--- |
| 阶段 0 | 体系收口与资产盘点 | 已交付 | [知识地图](assets/knowledge-map.md) |
| 阶段 1 | 可信执行闭环 | 已交付 | [可信执行闭环](articles/Agent可信执行闭环：从Trace、Evals到可恢复执行.md) |
| 阶段 2 | 多 Agent 交接协议 | 未开始 | [执行 Checklist](路线/后续执行Checklist：AI能力工程路线落地清单.md) |
| 阶段 3 | 生产治理与平台化 | 未开始 | [生产治理层说明](生产治理层说明.md) |

完整的文章归属和交付物清单见 [文章目录说明](articles/README.md)，详细执行项见 [后续执行 Checklist](路线/后续执行Checklist：AI能力工程路线落地清单.md)。
