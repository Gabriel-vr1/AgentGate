# Final submission verification - 25 September 2026

Application snapshot: `eb1cae5`. This completion block changes documentation and
submission artifacts only. No backend, prompts, schema, fixture, API or dependency
changes were made. The existing three live runs remain valid; trace and source
hashes were checked again. No redundant cloud calls were made.

| Gate | Result |
| --- | --- |
| Full automated tests | 53 passed |
| Repository evaluations | 13/13: 10 labelled cases plus 3 demos |
| Local CLI and HTTP | Unsafe BLOCK; safe APPROVE; incomplete CONDITIONAL |
| HTTP routes | Root 200; unknown route 404; invalid origin 403; invalid scenario 422 |
| Modes | Local deterministic and Microsoft Foundry live remain selectable |
| Download handler | All three review/trace JSON payloads round-trip exactly in a DOM stub |
| Live evidence | Three live cases, nine first-attempt stage calls; saved trace/source hashes verified |
| Independent clone | README install, 53 tests, 13 evaluations, server startup and 3 HTTP reviews pass |
| Security | detect-secrets 1.5.0 scanned 10 reachable commit snapshots and current intended files; no actual credentials found |
| Scan triage | 98 historical and 24 current detections: verified hashes/commit IDs and a synthetic invalid-endpoint fixture only; no tracked .env/private-key files |
| Other checks | JavaScript syntax and pip dependency consistency pass |
| PDF | Five pages rendered and visually inspected |

The clone was created earlier in this submission sprint, updated to the final
application snapshot and reinstalled in its isolated Python 3.12 environment.
It is an independent checkout, not a newly recreated virtual environment in
this last documentation block.

Actual browser visual/click/download verification and a spoken rehearsal remain
owner actions. The DOM stub is not browser QA. No portal telemetry, formal
Foundry evaluation or persistent agent resources are claimed.

Detailed machine-readable record: [final checks](evidence/final-submission-checks.json).
Live evidence index and limitations: [verification](verification.md) and
[limitations](limitations.md). [Final blueprint status](submission-status.md).
