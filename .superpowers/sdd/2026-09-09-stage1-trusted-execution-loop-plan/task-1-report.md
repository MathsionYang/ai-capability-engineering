# Task 1 Report

## Changed files

- `cn/assets/schemas/trace-event.md`: defined Trace -> Span -> Event hierarchy, ordered events, event and failure types, references, and redaction rules with a parseable example.
- `cn/assets/schemas/checkpoint-state.yaml`: added a machine-readable schema and resumable example covering status, cursor, idempotency, state, failure, and owner.
- `cn/assets/schemas/eval-case.yaml`: added the single-case schema and example covering categories, evidence, artifacts, rubric, forbidden actions, and fixtures.
- `cn/assets/checklists/validator-decision.md`: added decisions for incomplete input, tool timeout, validation failure, permission denial, and duplicate execution.
- `cn/assets/checklists/regression-report.md`: added baseline comparison, failure attribution, cost/latency gates, and Eval feedback fields.
- `tests/test_stage1_schemas.py`: added five unittest contract checks.
- `tests/__init__.py`: made the test directory importable by the required unittest module command.

## Verification

Command: `python -m unittest tests.test_stage1_schemas -v`

Initial run failed as intended because the Stage 0 schemas had no `schema` wrapper/hierarchy contracts and the new checklists did not exist. Final output: `Ran 5 tests in 0.010s`, `OK`, exit code `0`.

## Concerns

- The repository has pre-existing uncommitted Stage 0 edits; they were preserved and excluded from this commit.
- The schemas are documentation-level contracts; runtime JSON Schema validation is left to the Runner tasks.

## Review Fixes (2026-09-09)

- Added canonical trace required fields, `human_confirmation`/`waiting` values, optional sequence guidance, `parent_event_id`, and artifact URI/hash integrity rules.
- Replaced checkpoint statuses with the unified submitted/working/validating/retrying/input-required/waiting-confirmation/completed/failed/cancelled taxonomy.
- Replaced Eval categories with normal/input_incomplete/tool_failure/high_risk/historical_regression and made artifact examples explicit `{ref, hash}` objects.
- Strengthened `tests/test_stage1_schemas.py` to assert these normative contracts.

Verification command: `python -m unittest tests.test_stage1_schemas -v`

Output: `Ran 5 tests in 0.011s`, `OK`, exit code `0`.

Concern unchanged: these remain documentation-level schemas; runtime validation is owned by later Runner tasks.
