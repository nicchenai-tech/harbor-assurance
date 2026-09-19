# Final: 10-minute pitch and 5-minute Q&A

Target final: September 26. Nic or the helper's attendance remains unconfirmed. Deck has 12 slides. English delivery assumed. Speaker notes contain sources and cautions.

## Timing

| Time | Slides or action | Point |
|---|---|---|
| 0:00–0:40 | 1 | Core promise: evidence, uncertainty, human accountability |
| 0:40–1:20 | 2 | SI is reference; seven fields; waiting is not verification |
| 1:20–2:00 | 3 | Real review workspace and user's task |
| 2:00–2:50 | 4 | Explain architecture and where deterministic checks act |
| 2:50–3:25 | 5 and demo-02 | Equivalent meaning despite units |
| 3:25–5:15 | 6, live demo-01 then demo-03 | Real discrepancy, source, correction, version, retry |
| 5:15–6:10 | 7 | Official development evidence with positive-case denominator |
| 6:10–7:00 | 8 | First failures, fixes, separate frozen variant suite |
| 7:00–7:40 | 9 | Same-parser baseline comparison and what it proves |
| 7:40–8:30 | 10 | Measured runtime and reviewer workload |
| 8:30–9:25 | 11 | Honest prototype boundaries and integration requirement |
| 9:25–10:00 | 12 | Core promise, next pilot, invite questions |

## Likely questions and direct answers

**Why deterministic comparison instead of asking a model whether documents match?**
Once values are extracted, the business checks should be reproducible. Exact decimal conversion and explicit quantity rules are easy to inspect. Models may help propose candidates, but should not silently redefine equivalence.

**Where is the AI?**
Computer-vision OCR recognizes image-only documents: Apple Vision locally and Tesseract in the cloud container. OCR proposes locatable source evidence. Explicit code then normalizes and compares the seven fields, and a person must confirm every scanned value. We do not claim an LLM or agent system that is absent.

**How do you reduce hallucinations?**
This pipeline does not generate source facts. It retains file hashes and page/line/cell evidence. OCR results require confirmation. Human values identify the reviewer and source location. Production would need stronger source-claim verification and access controls.

**What happens when OCR is wrong or unavailable?**
The case remains in review. The person opens the original page, confirms values or replaces the file. The prototype does not claim calibrated business confidence scores. If neither OCR backend is available, the failure remains a visible review task.

**Is a perfect official score overfitting?**
It is development-set performance, not proof of generalization. The supplied inputs informed implementation. We keep first-run failures, a separate frozen 40-case semantic suite, and an honest label that these tests are synthetic and self-authored. We need a human-labeled real-world holdout next.

**Did you read the provided answers?**
The predictor consumes only participant inbox and attachments. The organizer scoring tool runs separately with its own reference file. We do not use per-email reference labels or the organizer generator to design predictions. We exclude the answer file and generator from the release.

**Why not multiple agents?**
The task has a clear, bounded verification path. Extra autonomous coordination does not improve deterministic equivalence checks. Complexity would make failures harder to reproduce within this team's time constraints.

**How much time or money does this save?**
The measured full batch took 41.346 seconds on this machine. It makes zero cloud model calls. Of 220 comparison requests, 109 completed comparisons, 20 required review and 91 were waiting. We have not conducted a controlled manual time study, so we do not claim a savings percentage or financial ROI.

**Can the human just type anything?**
A local prototype uses self-reported identities and locations. It records the decision but does not guarantee its truth. Production requires authentication, permissions, review policies and stronger audit storage. A discrepancy should be fixed in the carrier document, not typed away without evidence.

**What does retry preserve?**
Confirmed fields survive when the source hash is unchanged. A changed source invalidates the corresponding confirmation. SQLite transactions and expected-version checks prevent stale edits overwriting a newer report.

**What are the main limitations?**
Unseen wording and visual layouts, unsupported aliases, single SI/BL pairing, OCR variation across engines, no production mailbox, and no authenticated review. The next investment should be real-data validation and reliable layout extraction.

**Can judges access a remote demo?**
The Dockerized public sandbox uses only owned synthetic cases, disables uploads and exposes a health endpoint. The submission URL must be tested without an account and kept available throughout judging. The private organizer-data workspace remains local and separate.

## Offline fallback

Keep the PDF, the finished video once recorded, source package, demo fixtures and an already installed environment locally. If live interaction fails, disclose the failure and play the recording or show the documented report transitions. Never present a screenshot as a live result.
