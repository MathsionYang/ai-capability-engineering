# AI 能力工程知识地图与资产矩阵

> 本文件是文章、能力与资产关系的唯一维护入口，用于阅读、导航和评审。

## 使用说明

- 阅读顺序：基础层 -> 执行层 -> 可靠性层 -> 协作层 -> 安全层 -> 生产治理层。
- `已有专题文章` 表示内容已存在，不重复列为待写选题；`需要新增的整合文章` 表示后续整合缺口。
- 下一步动作只使用：保留、补充、重构、抽取资产。

## 固定案例线

| 案例线 | 定位 | 覆盖能力 | 入口 |
| --- | --- | --- | --- |
| 采购 / 合同审批 Agent | 业务主案例 | 权限、人工确认、委派、多 Agent、A2A、Artifact、审计 | [案例说明](examples/procurement-agent/README.md) |
| 代码修复 Agent | 技术验证案例 | Trace、Replay、Evals、Checkpoint、Validator、成本、失败恢复 | [案例说明](examples/code-repair-agent/README.md) |

## 分层总览

| 层级 | 文章数 | 主要能力 |
| --- | ---: | --- |
| 基础层 | 6 | AI能力工程：从 Skill、MCP 到 Agent、Skill 设计方法论：从专家经验到可复用能力、从 Prompt 到 Skill：专家经验的标准化封装指南、MCP 的第一性原理：从工具调用到能力协议、模型量化与蒸馏：原理、取舍与可跑实例、Agent 的第一性原理：从概念到范式演进 |
| 执行层 | 4 | Agent 工程实践指南：从最小闭环到生产级系统、Agent 规划范式进化论：从 CoT 到 Plan-and-Execute、Agent 的任务拆解艺术：从目标到可执行子任务、Agent 记忆系统设计：从上下文管理到长期经验复用 |
| 可靠性层 | 6 | Agent 可观测性实战：从日志、Trace 到 Replay、Agent 的可观测性实战：用 Tracing 看清你的 Agent“大脑”、Agent 的自动化评估体系（Evals）：从单元测试到集成评测、Agent 状态管理与断点续传：Checkpointer 机制深度解析、Agent 自我纠错与验证机制设计：从自信回答到可验证执行、Agent 可信执行闭环：从 Trace、Evals 到可恢复执行 |
| 协作层 | 3 | 多 Agent 协作模式深度解析：层级、流水线与群组、从 MCP 到 A2A：解读 Agent 互联协议的未来、Agent 任务交接协议：从 Agent Card 到 Artifact |
| 安全层 | 1 | Agent 安全护栏设计：权限控制、对抗鲁棒性与人工确认环 |
| 生产治理层 | 3 | Context Engineering：从记忆与 RAG 到可审计上下文、Agent 成本与延迟优化：模型路由、缓存、并行与预算控制、从个人 Agent 到企业能力平台：目录、Owner、评估、审计与生命周期 |

## 文章-能力-资产矩阵

| 状态 | 文章 / 提案 | 层级 | 依赖文章 | 已有案例 | 已有代码 | 已有清单 | 已有模板 | 待补缺口 | 下一步动作 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 已有专题文章 | [AI能力工程：从 Skill、MCP 到 Agent](../articles/AI能力工程：从Skill、MCP到Agent.md) | 基础层 | Skill设计方法论：从专家经验到可复用能力.md<br>MCP的第一性原理：从工具调用到能力协议.md<br>Agent工程实践指南：从最小闭环到生产级系统.md | 代码安全审查系统<br>合同与招标审查 Agent<br>财报分析 Agent<br>生产级质检 MCP Server | Skill、MCP、Agent 的流程和伪代码示例<br>Python/MCP Server 示例片段<br>C++ 与 MCP 边界示例<br>无统一可运行示例仓库 | Skill 设计检查清单<br>MCP Server 上线检查清单<br>Agent 设计检查清单<br>发布前检查清单 | 工具 schema 模板<br>结构化错误返回模板<br>权限矩阵模板<br>人类确认与审批模板<br>测试用例设计模板<br>优秀 SKILL.md 模板 | 章节内容较完整，但还没有独立的可运行参考仓库<br>需要将附录模板集中抽取到统一 assets 目录<br>需要补一张基础层到生产治理层的知识地图 | 抽取资产 |
| 已有专题文章 | [Skill 设计方法论：从专家经验到可复用能力](../articles/Skill设计方法论：从专家经验到可复用能力.md) | 基础层 | AI能力工程：从Skill、MCP到Agent.md | 高频重复任务识别<br>代码审查、质检和文档类 Skill 设计场景 | SKILL.md 和 YAML frontmatter 示例<br>agents/openai.yaml 结构示例<br>主要是目录结构和配置片段，没有独立脚本仓库 | 优秀 Skill 检查清单 | SKILL.md 结构模板<br>agents/openai.yaml 结构<br>scripts、references、assets 目录模板<br>Skill 生命周期设计步骤 | 文件名与 H1 标题不完全一致，需要统一命名<br>需要补一个从真实任务采集到 Skill 发布的完整可运行示例<br>需要把 Skill 评估样例与后续 Evals 统一 | 重构 |
| 已有专题文章 | [从 Prompt 到 Skill：专家经验的标准化封装指南](../articles/从Prompt到Skill：专家经验的标准化封装指南.md) | 基础层 | Skill设计方法论：从专家经验到可复用能力.md | 财报分析 Prompt 到 Skill 的完整迁移案例 | Prompt 到 Skill 的流程图和结构化配置示例<br>Skill 目录、资源和输出模板片段<br>无独立可运行项目 | Skill 生命周期检查清单 | 任务识别表<br>专家工作流抽取表<br>risk-language.md 示例<br>Skill 输出模板和 assets 目录示例 | 需要补充与统一主案例的连接，避免长期停留在财报案例<br>需要增加脚本、参考资料和测试样例的实际目录<br>需要将 Skill 版本、评估和发布流程接入生产治理 | 抽取资产 |
| 已有专题文章 | [MCP 的第一性原理：从工具调用到能力协议](../articles/MCP的第一性原理：从工具调用到能力协议.md) | 基础层 | AI能力工程：从Skill、MCP到Agent.md<br>Skill设计方法论：从专家经验到可复用能力.md | Hello MCP Server<br>Tool、Resource、Prompt 的组合<br>生产级质检 MCP Server<br>代码审查和外部工具调用 | hello_server.py FastMCP 示例<br>Tool、Resource、Prompt 注册示例<br>Host 配置、错误处理、日志、健康检查和测试示例 | MCP Server 上线检查清单<br>安全配置清单<br>测试与运维检查项 | Tool schema 示例<br>结构化错误返回示例<br>Host 配置模板<br>Resource URI 模板<br>Prompt 模板 | 文件名与 H1 标题不完全一致，需要统一命名<br>需要把最小 Server、契约测试和安全配置整理成独立示例目录<br>需要补 MCP 与 Agent Trace、权限矩阵、A2A 的统一字段映射 | 重构 |
| 已有专题文章 | [模型量化与蒸馏：原理、取舍与可跑实例](../articles/模型量化与蒸馏：原理、取舍与可跑实例.md) | 基础层 | AI能力工程：从Skill、MCP到Agent.md | 量化与蒸馏的最小实验 | distill_quant_demo.py 可运行最小实验 | — | 量化与蒸馏选型对比表<br>实验参数和结果对比表 | 与 Agent 模型路由、成本和延迟的关系还没有接入主线<br>需要补模型选择、质量退化、硬件环境和部署成本的可复现实验<br>属于支撑主题，暂不应抢占 Agent 可靠性主线的写作资源 | 保留 |
| 已有专题文章 | [Agent 的第一性原理：从概念到范式演进](../articles/Agent的第一性原理：从概念到范式演进.md) | 基础层 | AI能力工程：从Skill、MCP到Agent.md | SaaS 用户流失分析<br>代码测试和工具调用场景 | 目标闭环、Agent 等级和架构流程图<br>伪代码和概念性结构示例<br>无独立可运行项目 | — | — | 缺少从第一性结构到统一执行模型的字段映射<br>缺少可运行的最小 Agent 示例和验收标准<br>可以补充一张与 Skill、MCP、可靠性层的关系图 | 保留 |
| 已有专题文章 | [Agent 工程实践指南：从最小闭环到生产级系统](../articles/Agent工程实践指南：从最小闭环到生产级系统.md) | 执行层 | Agent的第一性原理：从概念到范式演进.md<br>MCP的第一性原理：从工具调用到能力协议.md<br>Skill设计方法论：从专家经验到可复用能力.md | 周末旅行规划 Agent<br>客服 Agent<br>代码测试<br>财报分析 Agent | 最小 Agent 闭环和工具调用代码片段<br>工具定义、权限判断和生产架构伪代码<br>无统一可运行参考项目 | Agent 设计检查清单<br>常见坑与避坑清单<br>工具清单 | 工具定义模板<br>权限矩阵模板<br>Agent 设计要素表 | 文件名与 H1 标题不一致，需要改成系列统一标题<br>内容覆盖面较宽，需要与总纲明确分工<br>需要补一套从开发、评估、灰度到回滚的最小参考实现 | 重构 |
| 已有专题文章 | [Agent 规划范式进化论：从 CoT 到 Plan-and-Execute](../articles/Agent规划范式进化论：从CoT到Plan-and-Execute.md) | 执行层 | Agent的第一性原理：从概念到范式演进.md<br>Agent工程实践指南：从最小闭环到生产级系统.md | SaaS 用户流失分析<br>登录接口 500 错误修复<br>代码修改、补测试和验证 | CoT、ReAct、Plan-and-Execute 流程图<br>Planner/Executor 结构和伪代码<br>无独立可运行项目 | — | 计划步骤结构示例<br>Planner/Executor 分工表 | 需要把计划输出接入统一 Task、Trace 和 Checkpoint Schema<br>需要补计划质量的 Eval Case 和计划偏离检测示例<br>需要明确短任务、长任务和多 Agent 委派的选择标准 | 抽取资产 |
| 已有专题文章 | [Agent 的任务拆解艺术：从目标到可执行子任务](../articles/Agent的任务拆解艺术：从目标到可执行子任务.md) | 执行层 | Agent规划范式进化论：从CoT到Plan-and-Execute.md<br>MCP的第一性原理：从工具调用到能力协议.md | 代码问题定位与修复<br>复杂目标到子任务的拆解 | Python Task 结构示例<br>结构化子任务 JSON 示例<br>Prompt 驱动的任务拆解示例 | — | 可交付子任务模板<br>任务依赖图和输入输出字段<br>Python Task 类结构 | 任务 Schema 还没有与 Checkpoint、Handoff 和 Artifact 统一<br>需要补拆解结果进入 Evals 的完整样例<br>需要增加任务取消、重试、超时和人工升级的处理规则 | 抽取资产 |
| 已有专题文章 | [Agent 记忆系统设计：从上下文管理到长期经验复用](../articles/Agent记忆系统设计：从上下文管理到长期经验复用.md) | 执行层 | Agent工程实践指南：从最小闭环到生产级系统.md<br>Agent的任务拆解艺术：从目标到可执行子任务.md | 代码修复 Agent<br>用户偏好和跨会话长期经验 | 记忆写入、读取、评分和升级代码片段<br>记忆记录 JSON 示例<br>无独立可运行记忆服务 | 记忆系统设计检查清单 | 记忆记录字段示例<br>写入与读取策略表<br>重要性、置信度和过期策略示例 | 文件名与 H1 标题不一致，需要统一命名<br>需要把记忆与 RAG、权限过滤、引用和有效期纳入 Context Engineering<br>缺少记忆质量、召回质量和错误注入的 Eval Case | 补充 |
| 已有专题文章 | [Agent 可观测性实战：从日志、Trace 到 Replay](../articles/Agent可观测性实战：从日志、Trace到Replay.md) | 可靠性层 | MCP的第一性原理：从工具调用到能力协议.md<br>Agent工程实践指南：从最小闭环到生产级系统.md<br>Agent的记忆系统设计：从上下文管理到长期经验复用.md | 用户流失原因分析<br>Agent 任务失败定位和 Replay | 结构化 Agent 事件和 JSONL 示例<br>SQL/DuckDB Trace 查询示例<br>成本、失败和漂移分析示例 | Agent 可观测性设计检查清单 | Goal/Plan/Tool Call/Observation/Validation/Cost 事件字段<br>Trace 结构化事件模型<br>Replay 元数据和失败归因字段 | 需要与 Tracing 专题明确总论和专题分工<br>需要发布一个可直接复用的 Trace Schema 文件<br>需要把 Trace 与 Evals、Checkpoint、权限和 Handoff 字段统一 | 抽取资产 |
| 已有专题文章 | [Agent 的可观测性实战：用 Tracing 看清你的 Agent“大脑”](../articles/Agent的可观测性实战：用Tracing看清你的Agent“大脑”.md) | 可靠性层 | Agent可观测性实战：从日志、Trace到Replay.md<br>MCP的第一性原理：从工具调用到能力协议.md | 代码修复 Agent 提交 PR<br>Agent 到 MCP 的 Trace 传递 | Trace/Span/Event 埋点示例<br>JSONL 导入 DuckDB 的分析示例<br>OpenTelemetry/GenAI 属性映射示例 | Tracing 落地检查清单 | Trace、Span、Event 三层模型<br>OpenTelemetry 属性映射表<br>Agent 到 MCP 的上下文传递字段 | 需要将专题字段合并到可观测性总论的 canonical Schema<br>需要补生产环境采样、脱敏、保留周期和成本控制配置<br>需要增加与 Eval Case 的轨迹评分示例 | 抽取资产 |
| 已有专题文章 | [Agent 的自动化评估体系（Evals）：从单元测试到集成评测](../articles/Agent的自动化评估体系（Evals）：从单元测试到集成评测.md) | 可靠性层 | Agent可观测性实战：从日志、Trace到Replay.md<br>Agent自我纠错与验证机制设计.md<br>MCP的第一性原理：从工具调用到能力协议.md | 客服退款 Agent<br>正常、缺参、边界、工具失败、高风险、攻击和回归样本 | Eval Case、Runner 和评分器代码片段<br>规则测试、轨迹评测和集成评测示例<br>JSON 评估结果和报告示例 | Evals 设计检查清单 | Eval Case 结构<br>测试金字塔分层表<br>Rubric/评分器示例<br>回归报告和失败归因表 | 需要提供可直接运行的评测 Runner、Fixture 和示例数据集<br>需要补 CI 门禁和版本基线对比样例<br>需要将线上 Trace 自动回流为 Eval Case 的流程具体化 | 抽取资产 |
| 已有专题文章 | [Agent 状态管理与断点续传：Checkpointer 机制深度解析](../articles/Agent状态管理与断点续传：Checkpointer机制深度解析.md) | 可靠性层 | Agent工程实践指南：从最小闭环到生产级系统.md<br>Agent规划范式进化论：从CoT到Plan-and-Execute.md<br>Agent可观测性实战：从日志、Trace到Replay.md | 被中断的长任务<br>LangGraph Checkpoint 恢复流程 | 可运行的最小 Checkpointer/恢复示例<br>状态版本和恢复规则示例 | 断点续传检查清单 | Checkpoint 状态字段表<br>恢复规则表<br>幂等键和重复副作用防护示例 | 需要补持久化后端、状态迁移和版本兼容示例<br>需要加入工具超时、取消、重复提交和恢复失败的故障注入<br>需要与 Trace、Eval 和人工确认状态统一 | 抽取资产 |
| 已有专题文章 | [Agent 自我纠错与验证机制设计：从自信回答到可验证执行](../articles/Agent自我纠错与验证机制设计.md) | 可靠性层 | Agent可观测性实战：从日志、Trace到Replay.md<br>Agent的任务拆解艺术：从目标到可执行子任务.md<br>Agent的自动化评估体系（Evals）：从单元测试到集成评测.md | 用户流失原因分析<br>事实 Claim 与外部证据核查<br>结构校验和高风险输出降级 | Validator 最小实现<br>Claim/证据绑定和事实核查代码片段<br>Reflection 与失败分类伪代码 | 自我纠错设计检查清单 | Validator 结果结构<br>Claim/证据表<br>事实来源等级表<br>纠错决策表 | 需要将 Validator 失败统一写入 Trace 并转成 Eval Case<br>需要增加纠错循环次数、成本和停止条件<br>需要明确何时进入 Memory、Skill、权限规则或人工升级 | 抽取资产 |
| 已有专题文章 | [Agent 安全护栏设计：权限控制、对抗鲁棒性与人工确认环](../articles/Agent安全护栏设计：权限控制、对抗鲁棒性与人工确认环.md) | 安全层 | MCP的第一性原理：从工具调用到能力协议.md<br>Agent工程实践指南：从最小闭环到生产级系统.md<br>Agent可观测性实战：从日志、Trace到Replay.md | 供应商资料整理<br>网页提示注入<br>权限越界、敏感信息泄露和高风险工具调用 | 策略判断、工具权限和人工确认伪代码<br>输入、计划、工具、输出和人工层防护示例<br>无独立安全测试项目 | Agent 安全护栏落地清单 | 威胁分类表<br>最小权限和人工确认规则示例<br>安全审计字段示例 | 需要抽取正式的工具、数据、动作三级权限矩阵<br>需要补提示注入、越权、外发和不可逆动作的回归数据集<br>需要与 Agent Card、Handoff、Trace 和 Eval 统一安全上下文 | 抽取资产 |
| 已有专题文章 | [多 Agent 协作模式深度解析：层级、流水线与群组](../articles/多Agent协作模式深度解析：层级、流水线与群组.md) | 协作层 | Agent规划范式进化论：从CoT到Plan-and-Execute.md<br>Agent的任务拆解艺术：从目标到可执行子任务.md<br>Agent自我纠错与验证机制设计.md | 竞品分析与汇报<br>代码修复<br>新功能上线方案评审 | 层级、流水线和群组协作流程伪代码<br>角色分工和消息结构示例<br>无独立可运行多 Agent 项目 | — | 三种协作模式对比表<br>角色职责和任务交接示例<br>风险清单、依赖清单和回滚预案示例 | 需要补正式 Handoff、Task、Message、Artifact 契约<br>需要补父子任务 Trace、权限和预算传递<br>需要增加协作超时、结果冲突、重复交接和人工升级案例 | 抽取资产 |
| 已有专题文章 | [从 MCP 到 A2A：解读 Agent 互联协议的未来](../articles/从MCP到A2A：解读Agent互联协议的未来.md) | 协作层 | MCP的第一性原理：从工具调用到能力协议.md<br>多Agent协作模式深度解析：层级、流水线与群组.md<br>Agent安全护栏设计：权限控制、对抗鲁棒性与人工确认环.md | 采购 Agent 连接供应商、法务和财务 Agent<br>采购网络中的发现、委派、回传和收敛 | Agent 路由和任务对象伪代码<br>A2A Task/Message/Artifact 结构示例<br>无独立可运行 A2A 互操作项目 | — | Agent Card 字段表<br>Task/Message/Artifact 对象表<br>MCP 与 A2A 边界对比表 | 需要补 Agent Card、认证、超时、取消和任务生命周期的可运行示例<br>需要补跨 Agent Trace、权限和成本传递<br>需要增加协议契约测试和协作者不可用的失败测试 | 抽取资产 |
| 已建立的整合文章 | Agent 可信执行闭环：从 Trace、Evals 到可恢复执行 | 可靠性层 | Agent可观测性实战：从日志、Trace到Replay.md<br>Agent的可观测性实战：用Tracing看清你的Agent“大脑”.md<br>Agent的自动化评估体系（Evals）：从单元测试到集成评测.md<br>Agent状态管理与断点续传：Checkpointer机制深度解析.md<br>Agent自我纠错与验证机制设计.md | 代码修复 Agent、离线 Runner、30 条 Eval Case | `trace-event.md`、`eval-case.yaml`、`checkpoint-state.yaml`、Validator 决策表、回归报告、Runner 测试 | — | 已建立参考实现 | Goal、Plan、Tool Call、Observation、Validation、Checkpoint、Artifact、Trace、Evals、Replay 和失败恢复均有可运行产物；成本/延迟与高风险发布门禁可回归 | 保留并持续回归 |
| 需要新增的整合文章 | Agent 任务交接协议：从 Agent Card 到 Artifact（待新增） | 协作层 | 多Agent协作模式深度解析：层级、流水线与群组.md<br>从MCP到A2A：解读Agent互联协议的未来.md<br>Agent安全护栏设计：权限控制、对抗鲁棒性与人工确认环.md | — | — | — | — | 需要定义 Agent Card、Task、Message、Artifact 和 Handoff 的最小字段<br>需要用主管 Agent、合同分析 Agent、风险审查 Agent 展示交接过程<br>需要处理超时、结果冲突、重复提交、权限不足和人工澄清<br>需要继承父任务的 trace_id、安全上下文和预算边界 | 补充 |
| 需要新增的整合文章 | Context Engineering：从记忆与 RAG 到可审计上下文（待新增） | 生产治理层 | Agent记忆系统设计：从上下文管理到长期经验复用.md<br>Agent可观测性实战：从日志、Trace到Replay.md<br>Agent安全护栏设计：权限控制、对抗鲁棒性与人工确认环.md | — | — | — | — | 需要统一用户输入、短期状态、长期记忆、RAG、工具结果和 Artifact 等上下文来源<br>需要覆盖切分、召回、重排、压缩、引用和上下文预算<br>需要为关键结论绑定来源、时间、权限和有效期<br>需要评估召回质量、证据完整性、陈旧知识和提示注入风险 | 补充 |
| 需要新增的整合文章 | Agent 成本与延迟优化：模型路由、缓存、并行与预算控制（待新增） | 生产治理层 | Agent可观测性实战：从日志、Trace到Replay.md<br>Agent的可观测性实战：用Tracing看清你的Agent“大脑”.md<br>Agent工程实践指南：从最小闭环到生产级系统.md | — | — | — | — | 需要拆解模型 Token、工具调用、重试、长上下文和人工等待成本<br>需要覆盖模型路由、工具结果缓存、Prompt 缓存、并行、超时和降级<br>需要定义单任务 Token、工具次数、最大执行时间和预算上限<br>需要使用 P50/P95 延迟、单任务成本、缓存命中率和重复调用率验收 | 补充 |
| 需要新增的整合文章 | 从个人 Agent 到企业能力平台：目录、Owner、评估、审计与生命周期（待新增） | 生产治理层 | AI能力工程：从Skill、MCP到Agent.md<br>Agent工程实践指南：从最小闭环到生产级系统.md<br>Agent的自动化评估体系（Evals）：从单元测试到集成评测.md<br>Agent安全护栏设计：权限控制、对抗鲁棒性与人工确认环.md | — | — | — | — | 需要建立 Skill、MCP Server、Agent、工具和评估集的能力目录<br>需要定义 Owner、数据责任人、安全责任人和事故处理人<br>需要覆盖开发、测试、灰度、发布、回滚、废弃和下线生命周期<br>需要把 Evals、安全审查、成本预算和权限策略接入发布门禁<br>需要补多租户隔离、审计、SLO、成本核算和能力复用 | 补充 |

## 资产目录

- [Trace Event 模板](schemas/trace-event.md)：统一 `trace_id`、`task_id`、事件类型、错误和指标字段。
- [Eval Case 模板](schemas/eval-case.yaml)：固定 Golden Set、禁止动作、评分规则和 fixture。
- [Checkpoint State 模板](schemas/checkpoint-state.yaml)：统一游标、状态、幂等键、恢复和失败字段。
- [Permission Matrix 模板](checklists/permission-matrix.md)：统一工具、数据、动作和人工确认边界。
- [采购 / 合同审批 Agent](examples/procurement-agent/README.md)
- [代码修复 Agent](examples/code-repair-agent/README.md)

## 术语约定

| 术语 | 统一含义 |
| --- | --- |
| `trace_id` | 一次完整 Agent 执行链路的唯一标识，可跨 Agent、MCP 和工具调用传递。 |
| `task_id` | 可独立跟踪、重试、取消和验收的任务标识；子任务另设 `parent_task_id`。 |
| `checkpoint` | 恢复所需的结构化状态快照，不保存聊天历史或大文件原文。 |
| `artifact` | 可被验收、引用和审计的结构化交付物，不等同于过程消息。 |
| `validator` | 对格式、事实、测试、权限或风险边界执行检查并返回结果的组件。 |
| `human-in-the-loop` | 在高风险、不可逆或无法自动判定的节点由人工确认、澄清或接管。 |

## 阶段 0 完成记录

- [x] 已建立文章-能力-资产矩阵（本页为唯一维护版本）。
- [x] 已确定采购 / 合同审批 Agent 与代码修复 Agent 两条固定案例线。
- [x] 已创建 `assets/checklists/`、`assets/schemas/`、`assets/examples/` 目录及最小模板。
- [x] 已统一总论与专题文章的可观测性关系，并在入口页补充交叉链接。
## Stage 1 trusted execution loop assets

- [Agent trusted execution loop article](../articles/Agent可信执行闭环：从Trace、Evals到可恢复执行.md)
- [Code repair Runner](examples/code-repair-agent/runner.py): offline six-scenario execution with Trace, Checkpoint, and Artifact output.
- [30 Eval Cases](examples/code-repair-agent/eval_cases.yaml): exact 10/5/5/5/5 category distribution.
- [Batch Eval Runner](examples/code-repair-agent/run_evals.py): JSON and Markdown regression reports with release gates.
- [Validator decision](checklists/validator-decision.md) and [regression report](checklists/regression-report.md): shared failure attribution and recovery fields.
