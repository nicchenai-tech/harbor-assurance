# Requirement-to-evidence audit

Audited September 18, 2026 and updated September 19 against the official FAQ, Participant Handbook and detailed Rules/Submission document. Local implementation is complete. Public deployment, recording, publication and formal competition submission remain incomplete outcomes.

| Requirement | Implementation | Verification evidence / boundary |
|---|---|---|
| Inspect packages and participant workflow | Prior workspace audit and handoff | 520 emails,250 attachments; input packages identical; official CLI verified; Docker unavailable |
| Five email categories | classifier.py | 520/520 official development classification; rule evidence in UI |
| Seven-field SI/BL comparison | pipeline.py, domain.py | 46/46 positive exact defect sets |
| Four native formats | parsers.py | Official examples plus independently authored PDF/DOCX/XLSX/TXT fixtures |
| Scan path | ocr.py, Apple Vision and cloud Tesseract | Six official scans plus two owned image-only PDFs processed; suggestions gated for review |
| Content roles, missing/corrupt/conflicting values | parsers.py, extract.py, pipeline.py | Official20/20 review, wrong-role/missing/total-conflict variants |
| No silent failure or timeout hang | bounded parser subprocess, OCR deadline | Actual deadline workflow test, injected timeout variants, processing_failed state |
| Evidence original + normalized + rule + location | field observations and evidence dialog | Browser source inspection, PDF original preview, source hash |
| Human correction and source reference | store.py, review form | Missing-value correction requires source location; report v1 to v2 |
| New attachments, immutable originals | server.py upload and Store originals | API upload recovery test, unchanged source file and original prediction |
| Persistence and retry | SQLite transactions and source hashes | Restart/reopen test, retry preserves correction, changed source invalidates, stale version409 |
| Internal states separate from evaluator | pipeline.py workflow states | Waiting,classified,verified,mismatch,review,processing_failed; strict export adapter |
| Full automatic submission | validation/release/submission.json | 520/520 strict schema, official score1.0 |
| At least30 unused-for-tuning semantic cases | Frozen second self-authored suite |40/40 first run, recorded hashes; synthetic, same author, not real-world generalization |
| Regression and first-failure honesty | First42 variant suite |38/42 initial,42/42 fixed; historical results retained |
| Workflow validation | tests/test_workflow.py |14/14 tests, including public reset/upload boundary and Tesseract parsing |
| Two browser rehearsals | Separate demo runtimes | Both corrected demo-03 to v2, retry retained correction at v3; browser QA report |
| Baseline comparison | Same extracted values, direct equality vs full rules |22/40 vs40/40 expected outcomes;8/17 vs0/17 clean false alarms |
| Business measurements | business-metrics.json |41.346s batch,109/220 comparisons complete,20review,91waiting; no unmeasured ROI claims |
| Running source + dependency lock | README, pyproject, lock, setup/run scripts | Editable install succeeded; no API key; current platform tested |
| Architecture and limitations | DESIGN.md and editable slide4 | Actual components and deployment gaps documented |
| Editable deck and PDF | presentation/Harbor_Pitch.pptx and.pdf |12 slides, package/layout/import checks, all slides and PDF pages visually inspected |
| Under5minute video | Explicitly permitted recording handoff |DEMO_SCRIPT.md:4m30s narration/actions, ready environment, repeated rehearsal. NO MP4 recorded |
| GitHub-ready contents | Explicitly allowlisted source archive | Excludes organizer inputs,labels,generator,runtime and official-input screenshots |
| Public live prototype | Mandatory; not yet delivered | Rules require a publicly accessible, deployed, functional project throughout judging; localhost does not qualify |
| Meaningful AI integration | Apple Vision locally; Tesseract computer-vision OCR in Linux image | Owned scanned-PDF demo retains bounding boxes and requires human confirmation |
| Meaningful cloud infrastructure | Restricted Docker public sandbox prepared; hosting URL pending | Health endpoint, ephemeral reseed, upload block, rate limit and portable OCR are implemented |
| GitHub/GitLab and README | Mandatory; public destination created | https://github.com/nicchenai-tech/harbor-assurance; final source push pending freeze |
| Public slide/documentation link | Mandatory; files ready locally | Must cover architecture, implementation, challenges and roadmap; public viewer permission not yet configured |
| Submission/helper checklist | SUBMISSION_CHECKLIST.md | Deadline,permissions,recording,portalreceipt and helper tasks |
| Final10minute pitch and5minute Q&A | FINAL_PITCH.md, deck notes | Timing and answers to likely technical/business questions |

## Outstanding external actions

Nic/helper must create the public cloud service from the prepared repository, record and upload the final video, publish the slide/documentation link, complete the Google Form written responses, verify all links without a signed-in session, submit by September21 and retain the receipt. There is no prescribed technology vendor. The portal timezone and September26 attendance remain to confirm. The rules state that every registered member of a finalist team must attend the physical final to remain eligible for the Top3. No paid purchase or formal submission has occurred.

## Scope limits

The public URL will be a shared synthetic sandbox, not an authenticated production system. Tests are synthetic. Native layout extraction and deterministic routing do not cover arbitrary documents. OCR requires human confirmation. The actual final competition rank cannot be guaranteed.
