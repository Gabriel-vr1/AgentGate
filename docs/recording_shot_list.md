# Recording shot list - 2:50 target

Before recording, start the reviewer at http://127.0.0.1:8765 at readable laptop
zoom. Prepare page 4 of the technical PDF in a second tab. Complete Azure
sign-in privately beforehand. Rehearse once and keep duration below 2:55.

| Time | Screen and action |
| --- | --- |
| 0:00-0:20 | Reviewer header, scenario selector and decision area. Explain the problem. |
| 0:20-0:25 | Select Unsafe authority expansion and Microsoft Foundry live. Click Run review once. |
| 0:25-0:45 | Keep running state visible. After completion show the three-stage workflow and deterministic safety band. |
| 0:45-1:15 | Frame BLOCK, reason, baseline/candidate and metric tiles. Scroll to Decision evidence; point out READ to WRITE, USD 0 to USD 5,000, approval removal, blockers and remediation. |
| 1:15-1:45 | Scroll to assurance evidence. Open View all tests briefly. Explain why passing stored results cannot override a hard blocker. Keep manifests closed. |
| 1:45-2:00 | Scroll to Audit record; show mode, trace ID and timing. Click Download review + trace. Optionally open Local structured application trace JSON if it is readable. |
| 2:00-2:15 | Switch to technical PDF page 4, explicitly introduced as saved verified live results. Show APPROVE, CONDITIONAL and nine first-attempt calls. |
| 2:15-2:35 | Keep 53 tests and 13/13 evaluations visible while stating limits. |
| 2:35-2:50 | Return to reviewer BLOCK summary; close with Evidence Before Authority. Stop recording. |

## Latency backup

If no result arrives by 0:45, stop that take. Record another using the PDF and
[saved unsafe trace](https://github.com/Gabriel-vr1/AgentGate/blob/main/docs/evidence/unsafe-foundry-trace.json),
labelled "Previously recorded live Foundry evidence - 25 September 2026."
Alternatively run Local deterministic and state that mode aloud, then show saved
live results separately. No replay-import feature exists. Never present a local
run as live or edit a long wait into an implied instantaneous response.

## Do not display

Keep .env, terminal account output, subscriptions, tenant IDs, tokens, unrelated
tabs, notifications and personal paths off screen. Do not imply portal agents,
Application Insights or formal Foundry evaluation. Emphasize authoritative
fields rather than potentially unsupported model prose. Inspect downloads
privately before sharing. Play back the video, check audio and readability,
then verify uploaded viewing permissions before submission.
