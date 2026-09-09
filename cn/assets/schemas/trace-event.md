# Trace Event Schema

The canonical hierarchy is `Trace -> Span -> Event`. Events within a span are ordered by optional `sequence` metadata; `parent_event_id` links a child event to its parent.

Required identity fields are `trace_id`, `event_id`, `task_id`, `timestamp`, `event_type`, `name`, and `status`; `span_id` and `sequence` are required for span ordering. `event_type` is one of `goal`, `plan`, `tool_call`, `observation`, `validation`, `checkpoint`, `final_output`, or `human_confirmation`; status is `started`, `succeeded`, `failed`, `skipped`, or `waiting`. The `failure_class` field uses `incomplete_input`, `tool_timeout`, `validation_failed`, `permission_denied`, `duplicate_execution`, or `internal_error`.

Redact secrets, tokens, credentials, personal data, and sensitive tool payloads before persistence; the `redact` rule applies before storage. Store large values by `input_ref` or `output_ref`.

```yaml
trace:
  trace_id: tr_20260909_001
  task_id: fix-issue-42
  spans:
    - span_id: sp_001
      events:
        - {trace_id: tr_20260909_001, event_id: ev_001, parent_event_id: null, task_id: fix-issue-42, sequence: 1, event_type: goal, name: receive_goal, status: succeeded, timestamp: 2026-09-09T10:15:00+08:00}
        - {trace_id: tr_20260909_001, event_id: ev_002, parent_event_id: ev_001, task_id: fix-issue-42, sequence: 2, event_type: human_confirmation, name: confirm_patch, status: waiting, timestamp: 2026-09-09T10:15:01+08:00}
```
