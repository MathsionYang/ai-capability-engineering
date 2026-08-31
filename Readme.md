# AI 能力工程：从 Skill、MCP 到 Agent

> 构建可复用、可调用、可验证的 AI 执行系统。  
> 让模型吸收不确定性，让系统约束不确定性。

## 项目定位

本目录收录一组围绕 **AI 能力工程** 展开的中文技术文章，核心问题是：

```text
如何把专家经验、外部工具和大模型推理能力组合成稳定、可治理、可验证的 AI 系统？
```

整套内容以 **Skill -> MCP -> Agent** 为主线展开：

- **Skill**：方法层，回答“任务应该怎么稳定完成”。
- **MCP**：能力层，回答“外部工具、资源和系统如何被 AI 稳定调用”。
- **Agent**：执行层，回答“谁来理解目标、制定计划、调用工具、验证结果并持续调整”。

## 发布主页

- CSDN 主页：[https://blog.csdn.net/sinat_28228747?type=blog](https://blog.csdn.net/sinat_28228747?type=blog)
- 掘金主页：[https://juejin.cn/user/3647513603343131/posts](https://juejin.cn/user/3647513603343131/posts)

## 文章之间的关系

这组文章不是孤立主题，而是一套从概念到生产治理的知识链路。

```text
AI 能力工程总纲
  -> Skill：沉淀可复用方法
       -> 方法论：定义优秀 Skill 的结构、边界和验证标准
       -> 实战迁移：把高频 Prompt 封装成可复用 Skill
  -> MCP：封装可调用能力
  -> Agent：组织目标、计划、工具、状态和验证
       -> 第一性原理：理解 Agent 是什么
       -> 工程实践：从最小闭环到生产系统
       -> 规划范式：决定怎么拆路径
       -> 任务拆解：把目标变成可执行子任务
       -> 记忆系统：让经验跨任务复用
       -> 可观测性：让执行过程可追踪、可回放、可治理
            -> Tracing 专项：看清 Thought / Action / Observation 的现场决策链
       -> 自我纠错：让结果可校验、事实可核查、经验可沉淀
```

也可以按工程分层理解：

| 层级 | 解决的问题 | 对应文章 |
| :--- | :--- | :--- |
| 总纲层 | 建立 Skill、MCP、Agent 的整体框架 | 《AI 能力工程：从 Skill、MCP 到 Agent》 |
| 方法层 | 把专家经验、流程和验证标准沉淀为可复用能力 | 《Skill 设计方法论》《从 Prompt 到 Skill》 |
| 能力层 | 把工具、资源、协议、部署、安全和运维标准化 | 《MCP 的第一性原理》 |
| Agent 基础层 | 讲清 Agent 的定义、边界、等级和核心闭环 | 《Agent 的第一性原理》《Agent 工程实践指南》 |
| 执行增强层 | 讲清规划、拆解、记忆这些核心执行能力 | 《Agent 规划范式进化论》《Agent 的任务拆解艺术》《Agent 记忆系统设计》 |
| 生产治理层 | 讲清日志、Trace、Replay、验证、纠错和成本治理 | 《Agent 可观测性实战》《Agent 的可观测性实战：用 Tracing 看清你的 Agent“大脑”》《Agent 自我纠错与验证机制设计》 |

## 推荐阅读顺序

如果是第一次阅读，建议按下面顺序走：

1. [《AI 能力工程：从 Skill、MCP 到 Agent》](cn/AI能力工程：从Skill、MCP到Agent.md)  
   先建立总框架，理解 Skill、MCP、Agent 分别处在哪一层。

2. [《Agent 的第一性原理：从概念到范式演进》](cn/Agent的第一性原理：从概念到范式演进.md)  
   再理解 Agent 的底层定义、目标闭环、能力等级和边界，避免把 Agent 简化成“模型加工具”。

3. [《Agent 工程实践指南：从最小闭环到生产级系统》](cn/Agent工程实践指南：从最小闭环到生产级系统.md)  
   从实践角度看一个 Agent 如何从目标、上下文、计划、工具、执行、验证走向可用系统。

4. [《Skill 设计方法论：从专家经验到可复用能力》](cn/Skill设计方法论：从专家经验到可复用能力.md)  
   学会把高频、复杂、有专家差距的任务沉淀成稳定流程和质量标准。

5. [《从 Prompt 到 Skill：专家经验的标准化封装指南》](cn/从Prompt到Skill：专家经验的标准化封装指南.md)  
   用一个完整案例理解如何从高频 Prompt 出发，逐步封装成带工作流、资源、脚本、测试和迭代机制的 Skill。

6. [《MCP 的第一性原理：从工具调用到能力协议》](cn/MCP的第一性原理：从工具调用到能力协议.md)  
   理解工具调用如何从简单函数封装，升级为带 schema、权限、错误处理、测试和运维的能力协议。

7. [《Agent 规划范式进化论：从 CoT 到 Plan-and-Execute》](cn/Agent规划范式进化论：从CoT到Plan-and-Execute.md)  
   学习 Agent 如何从内部推理走向外部行动，再走向可管理的任务计划。

8. [《Agent 的任务拆解艺术：从目标到可执行子任务》](cn/Agent的任务拆解艺术：从目标到可执行子任务.md)  
   深入理解如何把模糊目标拆成有输入、有输出、有依赖、有验证标准的子任务。

9. [《Agent 记忆系统设计：从上下文管理到长期经验复用》](cn/Agent记忆系统设计：从上下文管理到长期经验复用.md)  
   学习什么时候记、记什么、什么时候查、查出来怎么用，以及如何处理记忆冲突和过期。

10. [《Agent 可观测性实战：从日志、Trace 到 Replay》](cn/Agent可观测性实战：从日志、Trace到Replay.md)  
   最后进入生产治理，理解一次 Agent 任务如何被记录、追踪、验证、回放和成本管控。

11. [《Agent 自我纠错与验证机制设计：从自信回答到可验证执行》](cn/Agent自我纠错与验证机制设计.md)  
   进一步理解 Validator、事实核查和 Reflection 如何让 Agent 从“看起来完成”走向“能够证明自己做对”。

如果只想快速建立认知，可以读 1、2、3。  
如果要开发 MCP Server，可以重点读 1、4、6、10。  
如果要做生产级 Agent，可以按 1 到 11 顺序完整阅读。

## 专项实战补充

- [《Agent 的可观测性实战：用 Tracing 看清你的 Agent“大脑”》](cn/Agent的可观测性实战：用Tracing看清你的Agent“大脑”.md)
  作为《Agent 可观测性实战：从日志、Trace 到 Replay》的专项实战补充，聚焦 Thought / Action / Observation 链路埋点、`trace_id` 跨 Agent / MCP / Tool 贯穿、Langfuse / Phoenix 接入映射、DuckDB 轻量查询和失败 Trace 回流 Evals。

## 文档逐篇摘要

### [AI 能力工程：从 Skill、MCP 到 Agent](https://blog.csdn.net/sinat_28228747/article/details/164061172?spm=1001.2014.3001.5501)

这是整个系列的总纲型文档，系统解释 AI 能力工程为什么不能只靠 Prompt，而要通过 Skill、MCP、Agent 三层协作来构建稳定执行系统。文章覆盖方法层、能力层、执行层，以及从 Demo 到生产平台的完整路径，适合作为全系列入口和知识地图。

### [Agent 的第一性原理：从概念到范式演进](https://blog.csdn.net/sinat_28228747/article/details/164114906?spm=1001.2014.3001.5501)

这篇文章从第一性原理重新定义 Agent，强调 Agent 不是“会调用工具的大模型”，而是在目标约束下持续感知、规划、行动、反馈和验证的闭环系统。它梳理了 Agent 从符号系统、强化学习、工作流到 LLM Agent 的演进，并解释 Agent、ChatGPT、RPA、Workflow 的边界。

### [Agent 工程实践指南：从最小闭环到生产级系统](https://blog.csdn.net/sinat_28228747/article/details/164014253?spm=1001.2014.3001.5501)

这是一份面向落地的 Agent 开发指南，重点讲如何从一个最小闭环开始构建 Agent：明确目标、定义输入输出、设置权限、设计工具、处理失败、建立验收标准。它适合初学者和项目团队用来把 Agent 从概念变成可运行、可评估、可逐步生产化的系统。

### [Skill 设计方法论：从专家经验到可复用能力](https://blog.csdn.net/sinat_28228747/article/details/163827530?spm=1001.2014.3001.5501)

这篇文章讲 Skill 如何把专家经验、工作流、工具使用方式和质量标准沉淀为可复用能力包。它覆盖 Skill 的触发条件、标准结构、资源组织、七步设计流程、多 Skill 协同、失败处理和验证闭环，是理解“怎么做”这一方法层的核心文章。

### [从 Prompt 到 Skill：专家经验的标准化封装指南](https://blog.csdn.net/sinat_28228747/article/details/164209755?spm=1011.2415.3001.5331)

这篇文章是《Skill 设计方法论》的实战姊妹篇，重点回答一个更具体的问题：团队已有的高频 Prompt 如何升级为可复用 Skill。文章用财报分析案例贯穿，从任务识别、专家流程抽取、IPO-B 定义、Skill 包结构、`SKILL.md` 编写、测试样本到失败迭代，展示 Prompt 如何变成标准化工程资产。

### [MCP 的第一性原理：从工具调用到能力协议](https://blog.csdn.net/sinat_28228747/article/details/163638431?spm=1001.2014.3001.5501)

这篇文章系统讲解 MCP 如何把外部工具、资源和提示模板协议化，让 AI Host 能以稳定、可治理的方式调用外部能力。内容覆盖 MCP 基础概念、Server 开发、Tools/Resources/Prompts、传输方式、schema、错误处理、安全、测试、部署、可观测性、版本管理和生态集成，是能力层的核心长文。

### [Agent 规划范式进化论：从 CoT 到 Plan-and-Execute](https://blog.csdn.net/sinat_28228747/article/details/164120351?spm=1001.2014.3001.5501)

这篇文章解释 Agent 为什么需要规划，并对比 CoT、ReAct、Plan-and-Execute 三种典型范式。它说明 CoT 解决“怎么想”，ReAct 解决“怎么边想边做”，Plan-and-Execute 解决“怎么围绕目标组织长期行动”，适合理解 Agent 的决策和执行路径如何逐步工程化。

### [Agent 的任务拆解艺术：从目标到可执行子任务](https://blog.csdn.net/sinat_28228747/article/details/164139285?spm=1001.2014.3001.5501)

这篇文章聚焦“目标如何变成可执行任务”，强调好的任务拆解不是把目标切碎，而是把目标转化为可执行、可观察、可验证、可恢复的工作单元。文章讲解层级分解、依赖图、输入输出分解、工具映射、验证导向拆解，并给出常见错误和评估方法。

### [Agent 记忆系统设计：从上下文管理到长期经验复用](https://blog.csdn.net/sinat_28228747/article/details/164092820?spm=1001.2014.3001.5501)

这篇文章讲 Agent 记忆系统的设计方法，区分短期记忆、长期记忆、中间层摘要和缓存，并重点回答什么时候写入、什么时候检索、检索后如何注入上下文。它还讨论记忆冲突、过期、隐私、评估指标和最小可用架构，是理解 Agent 如何跨会话复用经验的重要文章。

### [Agent 可观测性实战：从日志、Trace 到 Replay](https://blog.csdn.net/sinat_28228747/article/details/164148491)

这篇文章面向生产级 Agent 的可观测性建设，讲清一次任务的 Goal、Plan、Step、Tool Call、Observation、Interpretation、Validation、Output、Cost 如何形成证据链。文章给出结构化事件、Trace、Replay、指标阈值、存储开销估算和埋点代码，帮助定位目标误解、工具错误、观察误读、验证缺失和成本失控等问题。

### [Agent 自我纠错与验证机制设计：从自信回答到可验证执行](https://blog.csdn.net/sinat_28228747/article/details/164206199?spm=1001.2014.3001.5501)

这篇文章讨论如何让 Agent 具备工程化的“自我怀疑”能力。文章从业务分析场景切入，讲解 Validator 步骤校验、事实核查证据绑定、Reflection 经验沉淀，以及失败后的重试、重规划、降级和人工确认机制，帮助 Agent 从流畅回答走向可验证执行。



## Repository Structure

```text
.
├── Readme.md
├── cn/
    ├── AI能力工程：从Skill、MCP到Agent.md
    ├── Agent的第一性原理：从概念到范式演进.md
    ├── Agent工程实践指南：从最小闭环到生产级系统.md
    ├── Skill设计方法论：从专家经验到可复用能力.md
    ├── 从Prompt到Skill：专家经验的标准化封装指南.md
    ├── MCP的第一性原理：从工具调用到能力协议.md
    ├── Agent规划范式进化论：从CoT到Plan-and-Execute.md
    ├── Agent的任务拆解艺术：从目标到可执行子任务.md
    ├── Agent记忆系统设计：从上下文管理到长期经验复用.md
    ├── Agent可观测性实战：从日志、Trace到Replay.md
    ├── Agent自我纠错与验证机制设计.md
    
```
