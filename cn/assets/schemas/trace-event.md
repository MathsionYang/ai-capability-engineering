# Trace Event Schema

The canonical hierarchy is `Trace -> Span -> Event`. Events within a span are ordered by `sequence`.

Required identity fields are `trace_id`, `span_id`, `event_id`, `task_id`, `timestamp`, and `sequence`. `event_type` is one of `goal`, `plan`, `tool_call`, `observation`, `validation`, `checkpoint`, or `final_output`; status is `started`, `succeeded`, `failed`, or `skipped`. The `failure_class` field uses `incomplete_input`, `tool_timeout`, `validation_failed`, `permission_denied`, `duplicate_execution`, or `internal_error`.

Redact secrets, tokens, credentials, personal data, and sensitive tool payloads before persistence; the `redact` rule applies before storage. Store large values by `input_ref` or `output_ref`.

```yaml
trace:
  trace_id: tr_20260909_001
  task_id: fix-issue-42
  spans:
    - span_id: sp_001
      events:
        - {event_id: ev_001, sequence: 1, event_type: goal, status: succeeded, timestamp: 2026-09-09T10:15:00+08:00}
```
