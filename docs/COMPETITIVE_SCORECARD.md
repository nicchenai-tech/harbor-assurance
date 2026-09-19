# Competitive scorecard

Harbor cannot claim superiority over unseen submissions. It can prove that it clears a harder, judge-visible bar than a happy-path extractor.

| Judge question | Harbor evidence | Release gate |
|---|---|---|
| Does the core workflow run? | Five-category route → four-format read → seven-field report | Two uninterrupted browser runs |
| Does it find real discrepancies? | 46/46 positive defect sets on organizer development evaluation | Official score remains1.000 |
| Does it avoid false differences? | KG/MT and container semantics; direct baseline22/40 vs Harbor40/40 | Frozen suite40/40 |
| Does it fail safely? | Missing, wrong-role, corrupt, scan and timeout paths | 20/20 review cases; zero unsafe clears in authored review suite |
| Can a reviewer verify the answer? | Raw value, normalized value, rule, source file/hash and page/line/cell | Every displayed comparison has a source or an explicit missing state |
| Can a person intervene safely? | Required source location, v1→v2 report, retry preservation, changed-source invalidation | Public demo review and reset pass |
| Is AI meaningful? | Computer-vision OCR proposes locatable evidence for image-only PDFs | Scanned demo uses Apple Vision locally/Tesseract in cloud and remains gated |
| Is cloud meaningful? | Public container, health endpoint, synthetic-data boundary and Linux OCR | Signed-out HTTPS check throughout judging |
| Are claims honest? | Development, regression, frozen authored suite and ablation are labeled separately | `scripts/competition_gate.py` passes |

## Ninety-second judge test

1. Click **Real mismatch** and identify the different field plus both sources.
2. Click **Equivalent units** and explain why `22 MT` equals `22,000 KG`.
3. Click **Human review**, correct BL Notify Party from its source line and observe report v2.
4. Click **Scanned AI** and verify that OCR suggestions do not auto-clear.

Success means the judge can see the product's difference without reading implementation notes or trusting an accuracy slogan.
