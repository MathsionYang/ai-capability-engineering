# AI 能力工程：从 Skill、MCP 到 Agent

> 构建可复用、可调用、可验证的 AI 执行系统。
> 让模型吸收不确定性、让系统约束不确定性

## 中文介绍

本仓库收录《AI 能力工程：从 Skill、MCP 到 Agent》的 Markdown 版本。

这本书从工程实践角度系统梳理 AI 能力建设的三层结构：**Skill、MCP 与 Agent**。Skill 用于沉淀专家经验和标准工作流，MCP 用于把外部工具、资源和提示词模板协议化暴露给 AI 系统，Agent 则负责理解目标、调度流程、调用工具、执行任务并验证结果。

本书适合正在开发 AI Agent、MCP Server、企业内部智能助手、AI 工具链，或希望将业务流程封装为可复用 AI 能力的开发者、产品经理和技术团队阅读。

## English Introduction

This repository contains the Markdown edition of *AI Capability Engineering: From Skill and MCP to Agent*.

The book explains a practical engineering framework for building reliable AI capabilities through three layers: **Skill, MCP, and Agent**. Skills capture expert workflows and reusable operating procedures. MCP standardizes how tools, resources, and prompts are exposed to AI systems. Agents orchestrate goals, load skills, call MCP tools, execute tasks, and verify outcomes.

It is written for developers, product teams, and technical leaders building AI agents, MCP servers, internal AI assistants, AI toolchains, or reusable business workflows powered by large language models.

## Repository Structure

```text
.
├── cn/
│   ├── AI能力工程：从Skill、MCP到Agent.md
│   ├── Agent开发总结V.md
│   ├── MCP开发总结V3.md
│   └── 优秀Skill设计指南V2.md
└── en/
    └── .gitkeep
```

## Main Book

- [《AI 能力工程：从 Skill、MCP 到 Agent》](cn/AI能力工程：从Skill、MCP到Agent.md)

## Source Notes

The main book is reorganized from three Chinese technical notes:

- [优秀Skill设计指南V2.md](cn/优秀Skill设计指南V2.md)
- [MCP开发总结V3.md](cn/MCP开发总结V3.md)
- [Agent开发总结V.md](cn/Agent开发总结V.md)

## Core Framework

```text
Skill: how to do the task
MCP: what capabilities can be called
Agent: who orchestrates and completes the task
```

Or in Chinese:

```text
Skill：怎么做
MCP：靠什么做
Agent：谁来调度并完成
```

## Suggested Topics

`ai-agent` `mcp` `model-context-protocol` `skill` `llm` `ai-engineering` `agent-engineering` `tool-calling`

