# 如何设计一个优秀的 Skill V2

优秀的 Skill，本质上是把某个领域的专家经验、工作流、工具使用方式和质量标准工程化沉淀，变成一套 AI agent 可以稳定执行、按需扩展、失败可控、结果可验证的能力包。

相比普通 Prompt，Skill 不是一次性的表达技巧，而是可复用的标准作业程序。它要让 Codex 在同类任务上少摸索、少犯错、少浪费上下文，并在关键时刻知道何时继续、何时追问、何时停止。

一个优秀 Skill 至少要回答七个问题：

1. 什么时候应该触发这个 Skill？
2. 这个 Skill 负责什么，不负责什么？
3. Codex 应该按什么流程执行？
4. 缺少信息时应该怎样向用户提问？
5. 失败、部分成功或高风险操作时如何处理？
6. 哪些资源、脚本、参考资料应按需加载？
7. 如何验证这个 Skill 的输出质量？

## 一、Skill 的核心定位

Skill 解决的是“怎么做更稳”的问题。

- Tool 解决“能不能做”：例如搜索网页、读取文件、调用 API、操作浏览器。
- Prompt 解决“这一次怎么表达”：适合临场、轻量、一次性任务。
- Skill 解决“同类任务以后怎么稳定做”：适合高频、复杂、有专家差距、有验证要求的任务。

好的 Skill 不是把所有知识塞进一个长文档，而是把最关键的执行策略、路由规则、边界条件和验证标准放在 Codex 能够及时使用的位置。

## 二、Skill 的标准结构

一个标准 Skill 通常是一个文件夹，至少包含一个 `SKILL.md` 文件：

```text
skill-name/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
├── references/
└── assets/
```

只有 `SKILL.md` 是必需的，其余目录按需添加。

### 1. `SKILL.md`

`SKILL.md` 是 Skill 的入口，由 YAML frontmatter 和 Markdown 正文组成：

```markdown
---
name: skill-name
description: Clear description of what this skill does and when to use it.
---

# Skill Title

Instructions for Codex...
```

frontmatter 中只应包含必要字段：

- `name`：Skill 的唯一标识，使用小写字母、数字和连字符。
- `description`：Codex 判断是否触发 Skill 的主要依据。

`description` 必须同时说明：

- 能做什么。
- 何时使用。
- 适用的文件、工具、任务或业务场景。
- 关键排除场景。

不要把“什么时候使用这个 Skill”只写在正文里，因为正文只有在 Skill 已经触发后才会被读取。

### 2. `agents/openai.yaml`

推荐添加，用于 UI 展示 Skill 信息。

常见字段：

- `display_name`：用户可读名称。
- `short_description`：一句话说明。
- `default_prompt`：用户可直接使用的默认请求。

这些字段应和 `SKILL.md` 保持一致。更新 Skill 后，要检查 UI 元数据是否已经过期。

### 3. `scripts/`

用于存放可执行脚本。适合以下场景：

- 操作需要确定性和可重复性。
- 每次让 Codex 手写代码容易出错。
- 任务涉及格式转换、批处理、渲染、校验、迁移、打包等机械流程。

脚本必须经过代表性测试。进入 Skill 的脚本应被视为长期可复用组件，而不是临时草稿。

### 4. `references/`

用于存放按需读取的详细资料。

适合放置：

- API 文档。
- 数据库 schema。
- 公司政策。
- 领域知识。
- 复杂流程说明。
- 不同平台、框架、供应商的专门指南。

`SKILL.md` 应当只保留路由规则和核心流程，详细内容放入 `references/`。每个引用文件都应在 `SKILL.md` 中被明确提到，并说明何时读取。

### 5. `assets/`

用于存放产出中会使用的资源，而不是给 Codex 阅读的资料。

例如：

- 模板文件。
- Logo。
- 字体。
- 图片。
- 示例项目。
- 可复制的工程骨架。

## 三、什么任务适合做成 Skill

并非所有任务都值得封装为 Skill。适合做成 Skill 的任务通常有以下特征：

- 高频重复：经常发生，值得维护一套固定流程。
- 专家差距大：熟手和新手产出差异明显。
- 流程复杂：需要多步判断，单次 Prompt 难以稳定完成。
- 输入输出清晰：能描述需要什么材料、交付什么结果。
- 风险较高：出错会造成返工、数据问题、格式损坏或业务风险。
- 需要验证：不能只生成结果，还要检查结果是否正确。
- 需要工具协同：需要脚本、API、浏览器、文档渲染或文件处理。

不适合做成 Skill 的任务：

- 一次性闲聊。
- 没有稳定流程的开放式探索。
- 过于宽泛的“帮我提高效率”。
- Codex 默认能力已经足够、且没有额外约束的简单任务。

## 四、设计 Skill 的七步流程

### 第一步：收集真实任务

先找 3 到 5 个真实案例，覆盖成功、失败、信息不足、边界情况。

不要只问专家“你的方法论是什么”，而要追问具体动作：

- 你拿到材料先看哪里？
- 什么信号会让你停下来追问？
- 哪些错误是新人经常犯的？
- 遇到例外情况你怎么处理？
- 做完后你怎么验收？

目标是提炼可执行流程，而不是写经验散文。

### 第二步：用 IPO 模型定义任务

像设计函数一样设计 Skill。

输入 Input：

- 用户必须提供什么？
- Codex 可以主动读取什么？
- 哪些信息缺失时不能开始？
- 哪些假设可以默认，哪些必须确认？

处理 Process：

- 标准执行顺序是什么？
- 哪些地方需要分支判断？
- 哪些步骤必须严格执行？
- 哪些步骤允许自由发挥？

输出 Output：

- 最终交付物是什么？
- 输出格式是什么？
- 文件保存在哪里？
- 是否需要报告、日志、摘要或验证结果？

边界 Boundary：

- 哪些情况不属于这个 Skill？
- 哪些情况必须暂停并询问用户？
- 哪些情况应该交给另一个 Skill 或工具？

### 第三步：设计信息搜集协议

优秀 Skill 不能只规定“做什么”，还要规定“信息不够时怎么问”。

提问策略应区分三类场景。

一次性追问：

- 适合缺少多个独立信息。
- 适合用户容易一次性补齐的配置项。
- 适合减少往返轮次。

示例：

```text
Before starting, ask for: target environment, input file path, desired output format, and whether existing files may be overwritten.
```

逐步澄清：

- 适合需求本身还模糊。
- 适合用户可能不知道专业选项。
- 适合需要先根据第一轮回答决定后续问题。

示例：

```text
If the user's goal is ambiguous, ask one clarifying question first. After the answer, choose the workflow branch.
```

选项式提问：

- 尽量提供 2 到 4 个明确选项。
- 每个选项说明影响。
- 避免让用户面对完全开放的问题。

示例：

```text
Ask the user to choose: "strict format preservation", "content-only conversion", or "visual redesign".
```

关键假设确认：

- 覆盖、删除、迁移、发布、生产环境操作前必须确认。
- 高成本或不可逆操作前必须复述即将执行的动作。

示例：

```text
Before overwriting files, restate the target paths and ask for explicit confirmation.
```

### 第四步：规划资源和渐进式披露

渐进式披露的目标是让 Codex 只加载当前任务真正需要的信息。

推荐三层结构：

1. 元数据：`name` 和 `description`，始终在上下文中。
2. `SKILL.md` 正文：触发后加载，只放核心流程和路由。
3. 资源文件：按需读取或执行。

`SKILL.md` 应尽量短，建议控制在 500 行以内。能放进 `references/` 的细节，不要塞进正文。特别大的引用文件应有目录或摘要。

资源路由要写成强指令，而不是弱建议。

弱路由：

```markdown
For AWS details, see `references/aws.md`.
```

强路由：

```markdown
If the user mentions AWS deployment, load `references/aws.md` before choosing commands.
```

对于大引用文件，在 `SKILL.md` 中加入短摘要，帮助 Codex 判断是否需要读取：

```markdown
- `references/aws.md`: AWS deploy paths, IAM assumptions, rollback rules, and CloudWatch verification.
```

避免深层引用。所有关键 reference 最好都从 `SKILL.md` 直接链接，不要让 Codex 需要层层寻找。

### 第五步：设置自由度

根据任务风险决定 Skill 的约束强度。

高自由度：

- 适合文案、头脑风暴、方案比较。
- 给原则和启发式规则即可。

中自由度：

- 适合有推荐流程但允许调整的任务。
- 可提供伪代码、参数表、分支规则。

低自由度：

- 适合文件格式脆弱、生产系统、批量迁移、合规流程。
- 应提供脚本、固定命令、校验步骤、回滚策略。

原则：越脆弱、越高风险、越需要一致性，就越应该降低自由度。

### 第六步：设计失败处理和回退机制

复杂任务中，失败和部分成功是常态。优秀 Skill 必须定义状态、检查点和升级条件。

建议在 Skill 中区分四种状态：

- Not started：尚未执行，会先检查输入和权限。
- In progress：正在执行，应记录关键中间状态。
- Partial success：部分完成，必须说明完成了什么、未完成什么。
- Failed safely：失败但保留现场，不掩盖错误，不继续猜测。

长链条任务应设计检查点：

- 每完成一个阶段，确认产物或状态。
- 对批量操作记录已处理项和未处理项。
- 对文件修改保留可比较的 diff 或输出路径。
- 对迁移、发布、覆盖类任务说明回退方式。

幂等性设计：

- 脚本重复运行不应造成重复写入、重复发布或重复删除。
- 如果无法保证幂等，必须在 Skill 中写明运行前检查和人工确认条件。

升级条件：

- 遇到 references 未覆盖的例外。
- 置信度不足。
- 输入和用户目标冲突。
- 验证失败且无法定位原因。
- 继续执行可能造成数据丢失、覆盖、发布或权限风险。

这些情况应暂停并询问用户，而不是自行猜测。

### 第七步：设计验证和评测

Skill 不应只规定如何产出，还要规定如何证明产出可靠。

单次任务验证：

- 运行测试。
- 执行校验脚本。
- 渲染并目视检查。
- 比较 schema 或格式。
- 检查命令退出码。
- 检查目标文件是否存在。
- 报告验证命令和结果。

Skill 开发期评测：

- 建议维护一个开发用 eval suite。
- eval suite 可以放在 Skill 包外部，避免污染正式 Skill。
- 选择 10 到 20 个典型请求，覆盖正常、缺参、边界、失败场景。

可量化指标：

- 任务成功率。
- 首轮正确率。
- 关键步骤遗漏率。
- 平均交互轮次。
- 验证通过率。
- 失败后是否正确暂停或升级。

对于确定性强的 Skill，可以维护 golden checklist：

- 必须执行的步骤。
- 必须读取的资源。
- 必须生成的文件。
- 必须报告的验证结果。
- 不允许发生的行为。

## 五、优秀 Skill 的核心特征

### 1. 触发精准

`description` 应清楚说明能力、对象、场景和排除条件。

不推荐：

```yaml
description: Helps with documents.
```

推荐：

```yaml
description: Create, edit, inspect, render, and verify professional .docx documents, including formatting, comments, tracked changes, templates, and visual QA. Use when Codex needs to work with Word documents or Google Docs-targeted document artifacts. Do not use for PDFs or live Google Docs editing.
```

### 2. 职责单一

每个 Skill 最好只做一类事情。职责越清晰，触发越稳定，维护越容易。

如果一个 Skill 必须覆盖多个分支，应让 `SKILL.md` 做路由，把分支细节拆到 `references/`。

### 3. 工作流明确

优秀 Skill 应提供清晰的行动顺序：

```markdown
## Workflow

1. Inspect the request and inputs.
2. Identify the task branch.
3. Load the required reference.
4. Execute the smallest sufficient change.
5. Validate the output.
6. Report output path, validation result, and unresolved risks.
```

### 4. 输入输出明确

Skill 应像函数一样定义输入和输出。

- 输入：用户提供什么，Codex 自动读取什么，缺什么必须问。
- 输出：交付物、格式、路径、日志、验证结果。
- 验收：什么条件下可以宣称完成。

### 5. 交互策略明确

优秀 Skill 应告诉 Codex 怎样和用户协作：

- 何时一次性追问。
- 何时逐步澄清。
- 何时提供选项。
- 何时复述关键假设并等待确认。

### 6. 失败可控

Skill 应规定失败后的动作：

- 重试。
- 回滚。
- 保存中间产物。
- 报告部分成功。
- 暂停并询问用户。
- 交给更合适的 Skill 或工具。

### 7. 验证闭环完整

凡是会生成文件、修改代码、转换格式、查询数据、部署系统的 Skill，都应包含验证步骤。

验证不是附加项，而是完成条件的一部分。

### 8. 上下文经济

Skill 应尊重上下文窗口：

- `SKILL.md` 放核心流程和路由。
- 大段知识放 `references/`。
- 稳定操作放 `scripts/`。
- 输出素材放 `assets/`。
- 不创建 README、CHANGELOG、安装手册等无关文件。

### 9. 可组合但不混乱

复杂任务可能触发多个 Skill。优秀 Skill 应说明和其他 Skill 的边界。

可以在正文中写：

```markdown
If the task requires PDF rendering after document generation, use the PDF skill only for rendering and visual inspection. Keep this skill responsible for DOCX authoring decisions.
```

当多个 Skill 冲突时，Codex 应先识别主任务，再决定主 Skill；如果无法判断，应向用户确认。

### 10. 可评测、可迭代

优秀 Skill 应能被真实任务检验。每次失败都应反向更新：

- 触发描述。
- 工作流。
- 资源路由。
- 验证标准。
- 失败处理。
- 示例和评测用例。

## 六、多 Skill 协同与冲突仲裁

复杂任务经常需要多个 Skill 接力。设计 Skill 时应避免让它成为孤岛。

### 1. 明确主 Skill

当用户请求跨多个能力域时，先判断主目标。

示例：

- “把 DOCX 转成 PDF 并检查排版”：主 Skill 是文档处理，PDF Skill 用于渲染验证。
- “审查代码并生成变更说明”：主 Skill 是代码审查，文档生成只是输出格式。
- “生成数据报告并制作 PPT”：主 Skill 取决于用户更重视数据分析还是演示产物。

### 2. 声明边界

Skill 可以写明：

- 何时把子任务交给另一个 Skill。
- 自己只负责哪部分决策。
- 冲突时以哪个 Skill 为准。

### 3. 冲突检测

当两个 Skill 的指令冲突时，应按以下顺序处理：

1. 用户明确要求优先。
2. 安全和数据保护优先。
3. 主任务 Skill 优先。
4. 更具体的 Skill 优先。
5. 仍无法判断时询问用户。

## 七、资源设计原则

### 1. `SKILL.md` 只放必要内容

应放：

- 核心工作流。
- 资源路由。
- 关键约束。
- 交互策略。
- 失败处理。
- 验证要求。

不应放：

- 长篇背景。
- 大量示例。
- 全量 API 文档。
- 变更日志。
- 人类教程。

### 2. `references/` 放详细知识

适合拆分方式：

```text
references/
├── aws.md
├── gcp.md
├── azure.md
├── schema.md
└── edge-cases.md
```

每个 reference 应只覆盖一个主题。超过 100 行的 reference 建议在开头加入目录。

### 3. `scripts/` 放确定性操作

适合脚本化的任务：

- 文件转换。
- 批处理。
- 结构校验。
- 渲染检查。
- API 调用封装。
- 重复生成固定格式产物。

脚本应提供：

- 参数说明。
- 清晰错误信息。
- 非零退出码。
- 可重复运行策略。

### 4. `assets/` 放输出素材

适合放：

- 模板。
- 图片。
- 字体。
- 示例工程。
- 可复制的 boilerplate。

这些资源一般不需要被完整读入上下文。

## 八、优秀 `SKILL.md` 模板

```markdown
---
name: example-skill
description: Do X, Y, and Z for [domain/tool/file type]. Use when Codex needs to [specific task], [specific task], or [specific task]. Do not use for [excluded scenario].
---

# Example Skill

## Workflow

1. Inspect the user request and available inputs.
2. Identify the task branch and risk level.
3. If required information is missing, follow the clarification protocol.
4. Load only the reference files required by the selected branch.
5. Use bundled scripts for deterministic or fragile operations.
6. Validate the result before reporting completion.
7. Report outputs, validation results, assumptions, and unresolved risks.

## Clarification Protocol

- Ask one question at a time when the user's goal is ambiguous.
- Ask a grouped checklist when several independent configuration values are missing.
- Prefer concrete options over open-ended questions.
- Before destructive or irreversible actions, restate the target action and wait for confirmation.

## Resource Routing

- If task A is requested, load `references/a.md`.
- If task B is requested, load `references/b.md`.
- If deterministic conversion is required, run `scripts/convert.py`.
- If an output template is required, use `assets/templates/`.

## Failure Handling

- If validation fails, inspect the error, fix the issue, and rerun validation.
- If the operation partially succeeds, report completed and incomplete items separately.
- If continuing may cause data loss or production impact, pause and ask the user.
- Preserve intermediate artifacts when they help diagnosis.

## Validation

Before completion, confirm:

- The output exists.
- Required commands or scripts exited successfully.
- Format, schema, or visual checks passed when relevant.
- Any assumptions or skipped steps are reported.
```

## 九、常见反模式

### 1. `description` 太泛

“Helps with documents” 这种描述无法稳定触发。应写清楚任务、对象、场景和排除条件。

### 2. 把正文写成百科

Skill 不是知识库全文。`SKILL.md` 应是路由和操作手册，详细知识放到 `references/`。

### 3. 只写成功路径

真实任务经常缺信息、失败或部分成功。Skill 必须包含失败处理和升级条件。

### 4. 缺少交互策略

只写“缺信息时询问用户”不够。应说明什么时候问、怎么问、问几个问题、是否提供选项。

### 5. 没有验证闭环

没有验证步骤的 Skill 容易让 Codex 过早宣布完成。验证应是完成条件。

### 6. 脚本没有测试

脚本进入 Skill 后会被反复使用。至少应通过代表性输入测试，并输出清晰错误信息。

### 7. 多 Skill 边界不清

如果 Skill 不说明边界，复杂任务中容易出现多个 Skill 抢主导、指令冲突、上下文浪费。

### 8. 上下文浪费

把长篇说明、重复示例、全量文档都放进 `SKILL.md`，会降低 Codex 处理真实任务的空间。

## 十、优秀 Skill 检查清单

设计完成后，用下面的清单自查：

- `SKILL.md` 是否存在？
- frontmatter 是否只包含 `name` 和 `description`？
- `name` 是否短小、合法、和文件夹名一致？
- `description` 是否明确说明能力、触发场景和排除场景？
- 正文是否以工作流为主？
- 是否定义输入、处理、输出和边界？
- 是否包含信息搜集和澄清协议？
- 是否包含高风险操作确认规则？
- 是否使用渐进式披露？
- 大段资料是否移动到 `references/`？
- 是否说明何时读取哪个 reference？
- 稳定重复操作是否做成 `scripts/`？
- 脚本是否经过代表性测试？
- 输出资源是否放在 `assets/`？
- 是否包含失败、部分成功和升级处理？
- 是否包含验证步骤和完成标准？
- 是否说明多 Skill 协同时的边界？
- 是否避免 README、CHANGELOG、安装手册等无关文件？
- 是否避免重复内容？
- 是否面向 Codex 编写，而不是面向人类教程？
- 是否有真实任务或 eval suite 进行验证？

## 十一、判断一个 Skill 是否优秀的标准

一个优秀 Skill 应该让 Codex 在同类任务上表现出：

- 触发更准：知道什么时候用，什么时候不用。
- 行动更稳：按明确流程执行，而不是临场猜测。
- 交互更少但更有效：缺信息时问得具体、及时、低负担。
- 失败更可控：部分成功、失败、回退、升级都有规则。
- 上下文更省：只加载当前任务需要的信息。
- 输出更可靠：验证是完成条件的一部分。
- 组合更清晰：知道自己和其他 Skill 的边界。
- 迭代更容易：有评测用例和质量指标支撑改进。

最终标准很简单：

如果没有这个 Skill，Codex 需要重新摸索；有了这个 Skill，Codex 可以稳定、快速、可验证、可回退地完成同类任务。这就是一个优秀 Skill。
