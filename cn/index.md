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

## 文章索引（按知识链路）

### 总纲

- [AI 能力工程：从 Skill、MCP 到 Agent](AI能力工程：从Skill、MCP到Agent.md)

### Skill 方法层

- [Skill 设计方法论：从专家经验到可复用能力](Skill设计方法论：从专家经验到可复用能力.md)
- [从 Prompt 到 Skill：专家经验的标准化封装指南](从Prompt到Skill：专家经验的标准化封装指南.md)

### MCP 能力层

- [MCP 的第一性原理：从工具调用到能力协议](MCP的第一性原理：从工具调用到能力协议.md)

### 模型效率

- [模型量化与蒸馏：原理、取舍与可跑实例](模型量化与蒸馏：原理、取舍与可跑实例.md)

### Agent 基础

- [Agent 的第一性原理：从概念到范式演进](Agent的第一性原理：从概念到范式演进.md)
- [Agent 工程实践指南：从最小闭环到生产级系统](Agent工程实践指南：从最小闭环到生产级系统.md)

### 执行能力

- [Agent 规划范式进化论：从 CoT 到 Plan-and-Execute](Agent规划范式进化论：从CoT到Plan-and-Execute.md)
- [Agent 的任务拆解艺术：从目标到可执行子任务](Agent的任务拆解艺术：从目标到可执行子任务.md)
- [Agent 记忆系统设计：从上下文管理到长期经验复用](Agent记忆系统设计：从上下文管理到长期经验复用.md)

### 协作编排

- [多 Agent 协作模式深度解析：层级、流水线与群组](多Agent协作模式深度解析：层级、流水线与群组.md)

### 安全治理

- [Agent 安全护栏设计：权限控制、对抗鲁棒性与人工确认环](Agent安全护栏设计：权限控制、对抗鲁棒性与人工确认环.md)

### 生产治理

- [Agent 可观测性实战：从日志、Trace 到 Replay](Agent可观测性实战：从日志、Trace到Replay.md)
- [Agent 的可观测性实战：用 Tracing 看清你的 Agent“大脑”](Agent的可观测性实战：用Tracing看清你的Agent“大脑”.md)
- [Agent 状态管理与断点续传：Checkpointer 机制深度解析](Agent状态管理与断点续传：Checkpointer机制深度解析.md)
- [Agent 自我纠错与验证机制设计：从自信回答到可验证执行](Agent自我纠错与验证机制设计.md)
- [Agent 的自动化评估体系（Evals）：从单元测试到集成评测](Agent的自动化评估体系（Evals）：从单元测试到集成评测.md)

## 推荐阅读顺序

- **快速建立认知**：总纲 → Agent 第一性原理 → Agent 工程实践指南
- **开发 MCP Server**：总纲 → Skill 设计方法论 → MCP 第一性原理 → Agent 可观测性实战
- **模型压缩**：MCP 第一性原理 → 模型量化与蒸馏
- **生产级 Agent**：按知识链路 1 → 2 → … → 生产治理完整阅读

## 发布主页

- CSDN：[https://blog.csdn.net/sinat_28228747?type=blog](https://blog.csdn.net/sinat_28228747?type=blog)
- 掘金：[https://juejin.cn/user/3647513603343131/posts](https://juejin.cn/user/3647513603343131/posts)
