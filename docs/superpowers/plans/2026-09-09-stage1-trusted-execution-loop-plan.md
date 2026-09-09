# 阶段 1：可信执行闭环实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Trace、Evals、Checkpoint、Validator 和固定 fixture 串成可运行、可回放、可回归的代码修复 Agent 闭环。

**Architecture:** 以无网络的代码修复 Agent 为唯一参考实现。Runner 使用确定性工具 fixture，按统一事件模型写 JSONL Trace，按状态游标写 Checkpoint，并把补丁、测试报告和失败说明写成 Artifact；Eval Runner 使用同一入口批量运行 30 条 YAML Case 并产出基线对比报告。

**Tech Stack:** Python 3.10+、标准库 `argparse`/`json`/`pathlib`/`hashlib`/`unittest`，已有 MkDocs + Material 配置，评估数据使用 PyYAML（仓库构建依赖已提供）。

**Spec:** `docs/superpowers/specs/2026-09-09-stage1-trusted-execution-loop-design.md`

## Global Constraints

- 参考实现只读本地 fixture，禁止网络访问和真实仓库副作用。
- Trace 必须包含 `trace_id`、`event_id`、`task_id`、`timestamp`、`event_type`、`name`、`status`；大对象只保存 `artifact://` 引用和 hash。
- 事件类型固定为 `goal`、`plan`、`tool_call`、`observation`、`validation`、`checkpoint`、`human_confirmation`、`final_output`；事件状态固定为 `started`、`succeeded`、`failed`、`skipped`、`waiting`。
- 任务状态至少覆盖 `submitted`、`working`、`validating`、`retrying`、`input-required`、`waiting-confirmation`、`completed`、`failed`、`cancelled`。
- Eval Case 固定分为 10 条正常、5 条缺参、5 条工具失败/超时、5 条高风险/权限不足、5 条历史回归，共 30 条。
- 高风险样本必须阻止或转人工；基线成功率下降超过 5 个百分点，或成本/延迟回归达到 20%，报告必须阻止发布。
- 阶段 1 不实现多 Agent Handoff、A2A、Context Engineering 或企业平台治理。

---

### Task 1: 升级统一 Schema 与验证决策资产

**Files:**
- Modify: `cn/assets/schemas/trace-event.md`
- Modify: `cn/assets/schemas/checkpoint-state.yaml`
- Modify: `cn/assets/schemas/eval-case.yaml`
- Create: `cn/assets/checklists/validator-decision.md`
- Create: `cn/assets/checklists/regression-report.md`
- Test: `tests/test_stage1_schemas.py`

**Interfaces:**
- `trace-event.md` 定义 `Trace -> Span -> Event` 层级、事件顺序、失败分类和脱敏规则，供 Task 2 Runner 和 Task 4 文章引用。
- `checkpoint-state.yaml` 的最小结构提供 `task_id`、`status`、`cursor`、`resume_policy.idempotency_key`、`state`、`failure` 和 `owner` 字段，供 Task 2 读取/写入。
- `eval-case.yaml` 的单条结构提供 `case_id`、`category`、`scenario`、`input`、`expected`、`forbidden_actions`、`required_evidence`、`artifacts`、`rubric` 和 `fixtures` 字段，供 Task 3 批量数据复用。

- [ ] **Step 1: 写 schema 失败测试**：`tests/test_stage1_schemas.py` 读取三个 YAML/示例文件，断言必需字段、事件类型、任务状态和失败分类集合存在；当前新增字段不存在时测试必须失败。
- [ ] **Step 2: 运行失败测试**：运行 `python -m unittest tests.test_stage1_schemas -v`，确认失败原因是 schema 字段尚未补齐。
- [ ] **Step 3: 升级 Trace、Checkpoint、Eval 模板**：补齐 canonical 字段、层级关系、状态转换、失败分类、幂等恢复、fixture 和评分字段；保留一个可解析的最小示例。
- [ ] **Step 4: 编写 Validator 决策表和回归报告模板**：覆盖输入不完整、工具超时、验证失败、权限拒绝、重复执行五类路径，并列出观测信号、处理策略、恢复点和是否回流 Eval。
- [ ] **Step 5: 运行通过测试**：再次运行 `python -m unittest tests.test_stage1_schemas -v`，预期所有断言通过。
- [ ] **Step 6: 提交**：提交消息为 `docs: define stage 1 execution schemas`。

### Task 2: 实现确定性代码修复 Runner

**Files:**
- Create: `cn/assets/examples/code-repair-agent/runner.py`
- Create: `cn/assets/examples/code-repair-agent/run_demo.py`
- Create: `cn/assets/examples/code-repair-agent/fixtures/repo_v1/README.md`
- Create: `cn/assets/examples/code-repair-agent/tests/test_runner.py`
- Modify: `cn/assets/examples/code-repair-agent/README.md`

**Interfaces:**
- `run_scenario(scenario: str, output_dir: pathlib.Path) -> dict`：运行一个固定场景，返回 `run_id`、`status`、`failure_class`、`artifacts`、`trace_path`、`checkpoint_path` 和 `side_effect_count`。
- 支持场景名 `success`、`input-required`、`tool-timeout`、`validation-failed`、`permission-denied`、`duplicate-replay`。
- `TraceWriter.emit(event_type: str, name: str, status: str, **fields) -> dict`：写入单行 JSONL，并自动补齐 `trace_id`、`event_id`、`task_id`、时间戳和父事件关系。
- `CheckpointStore.save(state: dict) -> pathlib.Path` / `CheckpointStore.load() -> dict`：使用 YAML 文件保存和恢复游标，按幂等键避免重复副作用。

- [ ] **Step 1: 写 Runner 失败测试**：在 `tests/test_runner.py` 先覆盖成功路径、缺参阻断、工具超时重试、验证失败、权限拒绝、Checkpoint 恢复和重复执行；测试断言输出文件、事件顺序、终态和 `side_effect_count`。
- [ ] **Step 2: 运行失败测试**：运行 `python -m unittest discover -s cn/assets/examples/code-repair-agent/tests -v`，确认实现尚不存在导致失败。
- [ ] **Step 3: 实现最小确定性工具和状态机**：只使用 `fixtures/repo_v1`，实现 `search_repo`、`run_tests`、`apply_patch`、`git_diff` 的固定返回；每个阶段写 Trace Event，验证前保存 Checkpoint，失败按场景进入对应状态。
- [ ] **Step 4: 实现 CLI 和 Artifact 输出**：支持 `python run_demo.py --scenario <name> --out <dir>`，写出 `trace.jsonl`、`checkpoint.yaml`、`test-report.json`、`patch.diff` 或失败说明；不访问网络。
- [ ] **Step 5: 更新案例 README**：补充运行命令、场景结果、Trace/Checkpoint/Artifact 路径和四类失败恢复规则。
- [ ] **Step 6: 运行通过测试**：再次运行 Runner 测试，并连续运行 `success` 两次，确认事件结构和副作用计数稳定。
- [ ] **Step 7: 提交**：提交消息为 `feat: add deterministic code repair runner`。

### Task 3: 建立 30 条 Eval Case 与批量 Runner

**Files:**
- Create: `cn/assets/examples/code-repair-agent/eval_cases.yaml`
- Create: `cn/assets/examples/code-repair-agent/run_evals.py`
- Create: `cn/assets/examples/code-repair-agent/tests/test_evals.py`
- Create: `cn/assets/examples/code-repair-agent/fixtures/tools.yaml`
- Modify: `cn/assets/schemas/eval-case.yaml`

**Interfaces:**
- `eval_cases.yaml` 是 YAML 列表，每条 Case 的 `scenario` 映射 Task 2 的场景名；`category` 精确取 `normal`、`input_incomplete`、`tool_failure`、`high_risk`、`historical_regression`。
- `run_evals.py` 提供 `run_cases(cases_path: pathlib.Path, output_dir: pathlib.Path, baseline_success_rate: float = 1.0) -> dict`，返回分类计数、通过率、失败分类、门禁结论和逐 Case 结果。
- CLI：`python run_evals.py --cases eval_cases.yaml --out report.json`。

- [ ] **Step 1: 写 Eval 失败测试**：断言数据总数为 30、分类计数为 10/5/5/5/5，每条含必需字段；断言固定 fixture 可解析，未实现数据时测试失败。
- [ ] **Step 2: 运行失败测试**：运行 `python -m unittest discover -s cn/assets/examples/code-repair-agent/tests -v`，确认缺少数据或 Runner 时失败。
- [ ] **Step 3: 编写 30 条 Case**：正常 10 条覆盖修复成功、测试通过和幂等；缺参 5 条覆盖目标文件/命令/Issue 缺失；工具失败 5 条覆盖超时、非零退出和空结果；高风险 5 条覆盖修改测试、越权路径、凭据和网络；历史回归 5 条覆盖已知重复搜索、未验证输出、错误文件修改、重复副作用和成本超预算。
- [ ] **Step 4: 实现批量 Runner 和门禁**：调用 `run_scenario`，校验必需证据和禁止动作；高风险全部阻止/转人工，比较基线成功率和成本/延迟回归并输出 `regression-report.md` 对应字段。
- [ ] **Step 5: 运行通过测试**：运行 Eval 测试，确认 30 条分类、报告结构和重复运行结果稳定。
- [ ] **Step 6: 提交**：提交消息为 `test: add code repair golden set`。

### Task 4: 编写可信执行闭环整合文章

**Files:**
- Create: `cn/可靠性层/Agent可信执行闭环：从Trace、Evals到可恢复执行.md`
- Modify: `cn/assets/examples/code-repair-agent/README.md`
- Modify: `cn/assets/knowledge-map.md`

**Interfaces:**
- 文章必须引用五篇已有可靠性文章、代码修复案例 README、四个 schema/checklist 资产和 30 条 Eval Case。
- 文章中的字段名、场景名、状态名和 CLI 命令必须与 Task 1-3 实际接口一致。

- [ ] **Step 1: 写文章验收测试**：用脚本读取文章，断言包含 Goal、Plan、Tool Call、Observation、Validation、Checkpoint、Artifact、Trace、Evals、Replay、失败恢复和发布门禁关键词，并命中五篇内部链接。
- [ ] **Step 2: 运行失败测试**：运行 `python -m unittest tests.test_integrated_article -v`，确认文章尚不存在导致失败。
- [ ] **Step 3: 编写整合文章**：按场景、执行模型、Trace、Evals、Checkpoint、Validator、失败恢复、发布门禁、运行结果和复用清单组织；展示成功与四类失败的实际输出，不重复展开专题原理。
- [ ] **Step 4: 更新知识地图**：将整合文章状态改为已建立参考实现，补充 Runner、Eval Set、Validator 决策表和回归报告资产。
- [ ] **Step 5: 运行通过测试**：运行文章测试、相对链接检查和 MkDocs 构建。
- [ ] **Step 6: 提交**：提交消息为 `docs: add trusted execution loop article`。

### Task 5: 更新入口、Checklist 并执行整体验收

**Files:**
- Modify: `cn/index.md`
- Modify: `Readme.md`
- Modify: `mkdocs.yml`
- Modify: `cn/路线/后续执行Checklist：AI能力工程路线落地清单.md`
- Create: `tests/test_stage1_acceptance.py`

**Interfaces:**
- 中文入口和根 README 链接整合文章、代码 Runner、Eval Set、Validator 决策表和回归报告。
- MkDocs nav 保持基础 -> 执行 -> 可靠性 -> 协作 -> 安全 -> 生产治理的顺序，阶段 1 资产可在导航中访问。

- [ ] **Step 1: 写阶段 1 验收测试**：断言五个阶段 1 小节均有 `[x]`、整合文章和所有资产存在、30 条 Case 分类正确、入口链接可解析。
- [ ] **Step 2: 运行失败测试**：运行 `python -m unittest tests.test_stage1_acceptance -v`，确认 Checklist 尚未勾选时失败。
- [ ] **Step 3: 更新导航和 README**：加入可信执行闭环、Runner、Eval Set 和决策资产；在整合文章与五篇专题之间补充双向关系链接。
- [ ] **Step 4: 标记阶段 1 Checklist**：勾选 1.1、1.2、1.3、1.4 的全部项目，验收描述写明实际命令和产物路径；不勾选阶段 2/3。
- [ ] **Step 5: 运行整体验收**：执行 `python -m unittest discover -s tests -v`、`python -m unittest discover -s cn/assets/examples/code-repair-agent/tests -v`、YAML/JSONL 校验、Markdown 相对链接检查、`git diff --check` 和 `python -m mkdocs build --strict --clean`。
- [ ] **Step 6: 提交**：提交消息为 `docs: close stage 1 trusted execution loop`。
