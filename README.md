# Harbor

A cloud-ready shipping document verification workspace for Averis × Monash Hackathon 2026.

Every result retains source evidence. Uncertain documents require human review. Reviewer corrections create a new report version, and retries preserve decisions when the source has not changed.

## Try the seven owned demo cases

Requirements: Python 3.13 recommended, Python 3.11+ supported by project metadata. Tested on macOS with Python 3.13. No API key. Internet is needed for the first dependency installation only.

```sh
bash scripts/setup.sh
bash scripts/run-demo.sh
```

Open **http://127.0.0.1:8766**. This uses seven owned synthetic demonstration emails, including image-only PDFs for OCR. Runtime data is separate from the inputs.

The guided cases show a real mismatch, equivalent KG/MT values, an unfamiliar label that needs a person, and scanned documents whose OCR evidence cannot auto-clear a shipment.

## Deploy the public sandbox

The repository includes a portable Docker image and `render.yaml`. Public mode serves only owned synthetic fixtures, disables uploads, rate-limits writes, resets on startup and exposes `/api/health`.

```sh
docker compose -f compose.demo.yml up --build
```

Open **http://127.0.0.1:8080**. The image installs Tesseract as the Linux/cloud OCR backend. macOS uses Apple Vision when available. See [deployment guide](docs/DEPLOYMENT.md) before publishing. The public sandbox is an interactive evaluation environment, not an authenticated production system.

For the organizer dataset, put its `inbox/` and `attachments/` folders together, then run:

```sh
.venv/bin/python -m harbor.server --data /absolute/path/to/participant-data --runtime runtime --port 8765
```

Open **http://127.0.0.1:8765**. The first startup processes all inputs. Later starts load persisted reports. A new engine version does not silently overwrite original reports: use a new runtime directory for a fresh evaluation. Do not delete a runtime containing reviews you want to retain.

## Batch export and official self-evaluation

```sh
.venv/bin/python -m harbor.cli batch --data /absolute/path/to/participant-data --out validation/my-run
python /path/to/sdoc-hackathon-docker/server/score_cli.py validation/my-run/submission.json --json
```

The September 19 organizer clarification explicitly permits the supplied ground truth for self-evaluation. Harbor keeps that process separate: the predictor reads inbox inputs, while the evaluator resolves labels after prediction. No reference file, answer table, generator or email-ID rule is packaged or imported into runtime code. Docker was unavailable on the development machine, so the organizer CLI is the verified scoring route; the supplied Docker service interface remains unclaimed here.

`validation/release/submission.json` is the unchanged automatic result for all 520 organizer emails. UI exports distinguish original automatic predictions and current reviewed predictions. Scores in the release report use only automatic predictions.

## Validation

```sh
.venv/bin/python -m pytest -q
.venv/bin/python scripts/validate_variants.py
.venv/bin/python scripts/validate_holdout.py
.venv/bin/python scripts/compare_baseline.py
```

Read [validation report](docs/VALIDATION.md) for denominators, first-run outcomes and limitations. `validation/holdout/freeze.json` records the engine and expectations before its first run. These are self-authored synthetic tests, not a representative external business benchmark.

## What the prototype does

- Routes five email categories and compares only BL comparison requests.
- Reads TXT, text PDF, DOCX and XLSX; verifies SI/BL roles from content.
- Compares seven fields with deterministic rules and exact decimal weights.
- Retains original text, file hash, page/line/cell location and normalization explanation.
- Uses Apple Vision OCR on macOS and Tesseract OCR in the Linux cloud image. Every scanned value requires confirmation.
- Supports field corrections, source locations, replacement attachments, report versioning and retry protection in SQLite.
- Isolates document readers in processes with a 60-second deadline. OCR workers have a 40-second deadline. Failures stay visible.

The private workspace does not authenticate users, connect to a production mailbox, release shipments or send emails. Reviewer names are self-reported. Never expose organizer/customer data with the public demo configuration. Production use requires authenticated identities, isolated durable storage and real carrier validation.

## What the evidence establishes

- Organizer development evaluator: **1.000**, with 46/46 positive defect sets and 20/20 review cases.
- First semantic suite: **38/42 → 42/42**, with the initial failures retained.
- Separately frozen authored suite: **40/40 on first run**.
- Same-extraction comparison: direct equality **22/40**, full Harbor **40/40**.
- Public-mode safety and workflow suite: **14/14 automated tests** plus a real browser review from report v1 to v2.

These are development and self-authored synthetic results, not production accuracy or a claim about unseen competitors. Run `python scripts/competition_gate.py` for the fail-closed evidence summary.

## Project guide

- `harbor/`: classifier, readers, extraction, comparison, review store and API.
- `web/`: browser workspace, no external frontend assets or analytics.
- `demo-data/`: owned fixtures and corrected carrier document for rehearsal.
- `docs/DESIGN.md`: architecture, rule boundaries and tradeoffs.
- `docs/DEMO_SCRIPT.md`: 4m30s video script and repeatable actions.
- `docs/COMPETITIVE_SCORECARD.md`: judge-facing advantage and proof matrix.
- `docs/USER_TEST_PROTOCOL.md`: first-time reviewer test and acceptance criteria.
- `docs/DEPLOYMENT.md`: public sandbox deployment and security checks.
- `docs/FINAL_PITCH.md`: 10-minute pitch and Q&A.
- `docs/SUBMISSION_CHECKLIST.md`: remaining account, recording and submission tasks.
- `PROGRESS.md`: status and unresolved dependencies.

Organizer documents and ground truth are not part of the public-ready source package. Screenshots containing organizer input belong only in the private competition submission unless redistribution permission is confirmed.
