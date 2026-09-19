# 4 minute 30 second demo recording

Status: recording-ready script and local environment. An MP4 has **not** been recorded. The current browser tools expose screenshots and interactions, but no screen-recording capability. Nic or the helper must capture the final recording and check its duration/audio.

Use English narration for judges. The owned synthetic fixtures make the actions reproducible. Clearly say the inbox results are preprocessed; field review and report recomputation happen during the demonstration. Never claim the synthetic fixtures are real customer shipments.

## Setup

1. Prefer the submitted public prototype URL. Press **Reset sandbox** so the review case starts unresolved. If the deployment is unavailable, run `.venv/bin/python -m harbor.server --data demo-data --runtime runtime-recording-01 --port 8766` locally.
2. Verify the public URL in an incognito window before recording. Do not expose organizer inputs or ground truth.
3. Use a desktop browser, 1280×900 or wider. Set zoom to 100%. Hide personal tabs and notifications. Use the operating system's screen recorder and a microphone.
4. Have `presentation/Harbor_Pitch.pdf` and `docs/VALIDATION.md` ready. Aim for 4m30s, allow up to 4m50s. Official maximum is five minutes.
5. Prepare `docs/VALIDATION.md` or the results slide for official metrics; do not host the organizer dataset publicly.

## Recording sequence and narration

| Time | On-screen action | English narration |
|---|---|---|
| 0:00–0:25 | Cover, then the public workspace URL | “Harbor helps a shipping reviewer verify a draft bill of lading against shipping instructions. Every conclusion links to source evidence. Uncertain fields go to a person, and every correction creates a traceable report. This cloud sandbox contains only our synthetic demonstration shipments.” |
| 0:25–0:50 | Open demo-04, show SI_REQUEST routing evidence. Open demo-06 waiting request. | “The inbox routes five categories. Only comparison requests enter document verification. A request still waiting for a draft remains unverified. It is never presented as a completed match. The inbox has been preprocessed for this recording.” |
| 0:50–1:30 | Open demo-01. Scroll to Container count. Show SI 3 and BL 4. Click each source link. | “Here the draft contains four containers, while the SI specifies three. Harbor reads the quantity separately from the forty-foot size. The result points to the original line in each file. The reviewer can see exactly what caused the discrepancy. The source files remain unchanged.” |
| 1:30–2:00 | Open demo-02, Gross weight source evidence. | “Formatting differences should not create unnecessary work. The SI gives twenty-two thousand kilograms. The draft gives twenty-two metric tonnes. Both normalize to the same exact kilogram value. Harbor shows the conversion rule and the original text, without a hidden tolerance.” |
| 2:00–2:55 | Open demo-03. Click BL Notify party “View source”. Point at line 8. Close. Review field, select BL Notify party if needed. Value `West Trading Ltd`, location `line 8, Notify Contact`, name, reason. Save. | “This document uses an unfamiliar label. Harbor leaves the notify party unresolved rather than guessing. The original document clearly gives West Trading Limited on line eight. I enter that value, identify the source location and explain the correction. Saving now recomputes the seven checks. The report changes to version two, and the original automatic result remains available.” |
| 2:55–3:20 | Scroll to Review history. Click Recheck, wait, show retained correction and next version. | “The audit records the old value, new value, reviewer, reason and time. Rechecking does not erase the human decision. If the source file changes, the confirmation must be revisited. Damaged or unreadable documents can be replaced through the same workspace.” |
| 3:20–3:45 | Click `4 · Scanned AI`, open one OCR source link. | “Image-only documents use computer-vision OCR in the cloud container. Every suggested value retains its page location and remains pending confirmation. OCR errors never become automatic clearance.” |
| 3:45–4:15 | Deck results and variants slides | “On the supplied 520-email development set, the automatic submission is complete. It catches all forty-six positive defect cases and escalates all twenty required reviews. These are development results. A separate forty-case synthetic variant suite passed on its first run. Real carrier layouts still need independent validation.” |
| 4:15–4:30 | Closing slide | “Harbor’s value is a reviewable decision, backed by the document and preserved through human correction. The next step is a real-data pilot and a measured reviewer-time study.” |

## Exact review values

For demo-03, correct **BL / Notify party**, not the SI. The actual source line is `Notify Contact: West Trading Ltd`. Use reason: `Confirmed the Notify Contact value in BL line 8; the label was not supported by the extractor.` The new value is supported by the original source, not copied from the SI to force a match.

For optional attachment recovery, demo-01's candidate really contains four containers. Do not simply overwrite it with three to make the comparison pass. Use Add / replace document, replace `demo-01-BL.txt` with `demo-data/carrier-amended-BL.txt`, and explain that the carrier supplied an amended draft. This file genuinely contains three containers.

## Final recording checks

Watch the whole recording once. Verify readable field values, audible voice, no private tabs, actual version transition, and total duration under five minutes. Check the video link in an incognito browser with no account session. The recording script and screenshots are not substitutes for the required uploaded video.
