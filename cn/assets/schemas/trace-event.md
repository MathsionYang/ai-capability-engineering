# Trace Event Schema

The canonical hierarchy is `Trace -> Span -> Event`. Each event carries its parent `span_id`; events within a span are ordered by required `sequence` metadata, while `parent_event_id` links nested events.

Required identity fields are `trace_id`, `span_id`, `event_id`, `task_id`, `timestamp`, `event_type`, `name`, and `status`; `sequence` is required for deterministic event ordering and `parent_event_id` links nested events. `event_type` is one of `goal`, `plan`, `tool_call`, `observation`, `validation`, `checkpoint`, `artifact`, `final_output`, or `human_confirmation`; status is `started`, `succeeded`, `failed`, `skipped`, or `waiting`. The `failure_class` field uses `incomplete_input`, `tool_timeout`, `validation_failed`, `permission_denied`, `duplicate_execution`, or `internal_error`.

Redact secrets, tokens, credentials, personal data, and sensitive tool payloads before persistence; the `redact` rule applies before storage. Store large values by an `artifact://` reference and retain its SHA-256 digest in `artifact_hash` (the `input_ref`/`output_ref` and corresponding hash fields are required whenever an event carries an artifact).

Artifact-bearing event contract:

| Reference field | Required digest | Verification |
| --- | --- | --- |
| `input_ref` | `input_hash` | The digest must match the referenced input bytes when the reference is locally readable. |
| `output_ref` | `output_hash` and `artifact_hash` | Both digests must match the persisted output bytes; the reference must resolve to a file. |

Every digest uses the form `sha256:<64 lowercase hexadecimal characters>`. A missing reference, missing digest, or mismatched digest is a contract failure and must block the Eval Case.

```yaml
trace:
  trace_id: tr_20260909_001
  task_id: fix-issue-42
  spans:
    - span_id: sp_001
      events:
        - {trace_id: tr_20260909_001, span_id: sp_001, event_id: ev_001, parent_event_id: null, task_id: fix-issue-42, sequence: 1, event_type: goal, name: receive_goal, status: succeeded, timestamp: 2026-09-09T10:15:00+08:00, output_ref: artifact://runs/tr_20260909_001/goal.json, output_hash: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, artifact_hash: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}
        - {trace_id: tr_20260909_001, span_id: sp_001, event_id: ev_002, parent_event_id: ev_001, task_id: fix-issue-42, sequence: 2, event_type: human_confirmation, name: confirm_patch, status: waiting, timestamp: 2026-09-09T10:15:01+08:00}
```
