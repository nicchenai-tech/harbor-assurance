# Validation evidence

Recorded September 18, 2026. This is prototype evidence on synthetic data. No claim of production accuracy or a guaranteed competition rank.

## Official development data

520 emails, 250 attachments. The predictor reads participant inputs only. The official CLI runs separately with its own labels. Release artifacts: `validation/release/submission.json`, `scoreboard.json`, `run-summary.json` and `cases.json`.

| Metric | Result | Denominator or scope |
|---|---:|---|
| Output and strict schema validity | 520/520 | All inbox IDs, no extra or missing IDs |
| Classification macro-F1 | 1.000 | 5 classes, 520 emails |
| Classification accuracy | 520/520 | Same development data |
| Defect precision / recall / F1 | 1.000 / 1.000 / 1.000 | Organizer comparison evaluation |
| Field-level F1 | 1.000 | Organizer field labels |
| Exact defect sets end to end | 46/46 | Positive defect emails |
| Review recall / precision | 20/20 and 20/20 | Organizer review cases |
| Weighted official score | 1.000 | 0.3 classification + 0.2 defect F1 + 0.5 end-to-end |

The official comparison denominator is 200 and includes waiting requests represented as empty defect sets. Therefore we emphasize the 46 positive defect cases and the 20 review cases, not only exact-match accuracy. The product distinguishes 91 unverified requests waiting for documents from 63 verified matches. Some ordinary draft requests export as OK solely to match the documented evaluator convention.

The data informed implementation. This score is development-set performance and cannot establish generalization. `validation/baseline` is the early engine result (score 0.949985), not the direct-comparison ablation baseline. `v2` captures a temporary container suffix regression that was corrected using participant input inspection. Historical runs are retained for honesty.

## Independent semantic variants and regression

42 self-authored variants were frozen before their first evaluation, without organizer labels. First run: 38/42. Four failures exposed notice interference in intent routing, partial container parsing, ambiguous tons and a unit stored in the label. After fixes: 42/42. Once those results informed fixes, this suite became regression data. Both `first-run.json` and `latest-run.json` remain available.

A second set of 40 new semantic variants was frozen before first execution. First run: 40/40. It covers new identities and amounts, different formats, equivalent units, one and multiple defects, missing data, wrong roles, corrupt files, scan confirmation and deadlines. This suite did not inform fixes. The later FCL suffix correction came from an official-input regression check, not the withheld suite. The release paired ablation reproduced 40/40 on the same second suite.

These tests were written by the same development agent and intentionally exercise the stated contract. They are not an independently collected, statistically representative external benchmark. Before production, obtain real carrier layouts and a human-labeled holdout.

## Paired design comparison

All 40 second-suite cases, same extracted values. The baseline already normalizes case and whitespace and abstains for missing or unreadable fields. It does not implement semantic unit/quantity normalization, the full uncertainty gate or the full role rules. This tests the value of these explicit rules, not whether Harbor beats a commercial document model.

| Outcome | Direct comparison | Full Harbor |
|---|---:|---:|
| Exact expected status and defect set | 22/40 | 40/40 |
| False mismatch on clean cases | 8/17 | 0/17 |
| Automatic OK on review-required cases | 1/16 | 0/16 |

Results: `validation/ablation/results.json`. Improvements are concentrated in format/quantity/unit variants and uncertainty handling. A naturally sampled business distribution may show a different gain.

## Runtime and operational coverage

Measured release batch on this macOS/Python 3.13 environment: 41.346 seconds for 520 emails including six OCR documents and process isolation. Mean 78.8 ms per email, median 0.2 ms, p95 388.0 ms. Many emails require no attachment processing; these numbers must not be presented as full document-pair latency. OCR and operating-system caches were not controlled, so this is not a cold-start benchmark.

Among 220 comparison requests:
- 109/220 (49.5%) completed all seven comparison checks: 63 matches and 46 discrepancies.
- 20/220 (9.1%) require human input due to uncertainty.
- 91/220 (41.4%) are waiting requests with no completed verification.

The other 300 emails were routed to their inbox category, not document-verified. A detected discrepancy still needs operational handling; it is not automatically released.

Cloud model calls: 0. Cloud inference API charges for the measured run: USD 0. Device, electricity and development costs are excluded. No time-saving or financial ROI percentage is claimed because no controlled manual reviewer experiment has been conducted.

## Workflow and browser checks

Automated workflow checks cover persisted corrections, immutable automatic export, report versions, stale-version conflict, changed-source invalidation, corruption isolation, real reader deadline, schema checks, renamed sources, wrong document content, file upload and cross-origin write rejection. The final XML report states the actual test count.

Browser rehearsal verifies real routing, discrepancy evidence, equivalent units, a missing extracted value corrected from the original source, a new report version, and retry retaining that human decision. Rehearsal data is separate from the 520-email automatic submission.

## Limits that matter

Rule-based intent matching and template-label extraction may miss unseen wording. Native PDF reading order is limited. Apple Vision and Tesseract OCR can differ, and every scanned value needs confirmation. Entity normalization has no approved alias dictionary. Bare GROSS WEIGHT assumes the competition's kg field convention. Human identities and source-location statements are self-reported. Multiple shipments in one email and production mailbox ingestion are not implemented. The public deployment is a shared synthetic sandbox, not a production environment.
