# Harbor demo script v3 — 4 minutes 30 seconds

Use the public prototype at **https://harbor-assurance.onrender.com/**. The target runtime is 4m20s–4m40s and the hard maximum is five minutes.

## Before recording

1. Wake the Render service and confirm `/api/health` returns `status: ok`.
2. Press **Reset synthetic sandbox**. Confirm DEMO-03 is **Needs Review** and report v1.
3. Open the public URL in a private browser window at 1280×900 or wider, 100% zoom.
4. Keep the validation slide ready. Hide private tabs, credentials, organizer ground truth and notifications.
5. Use only the synthetic demo cases visible in the public sandbox.

## Recording sequence

| Time | On-screen action | English narration |
|---|---|---|
| 0:00–0:20 | Cover, then public URL | “Harbor verifies a draft Bill of Lading against its Shipping Instruction. AI and document tools help read the files, explicit rules make the comparison, uncertainty goes to a person, and every decision has a source.” |
| 0:20–0:40 | Overview: four status cards and **Try Harbor** | “The overview makes the operating queue clear: Verified, Issues Found, Needs Review and Waiting. The public cloud sandbox contains only our seven synthetic demonstration cases. These three guided paths let a reviewer test Harbor without knowing internal IDs.” |
| 0:40–1:00 | Click **Clean Match**. Point to “No discrepancy detected” and Gross Weight | “A clean case completes all seven checks. Here twenty-two thousand kilograms and twenty-two metric tonnes are equal after exact conversion to twenty-two thousand kilograms, so formatting does not create unnecessary work.” |
| 1:00–1:40 | Click **Find a Discrepancy**. Show Container Count: SI 3 vs Draft BL 4. Click both **View Evidence** links | “This carrier draft says four containers, while the Shipping Instruction says three. Harbor reports one confirmed discrepancy and six matched fields. View Evidence identifies the document, line and text Harbor read, so the reviewer can verify the result before acting.” |
| 1:40–2:05 | Return briefly to Gross Weight in **Clean Match** and open evidence | “Normalization remains visible rather than hidden. Harbor preserves both original values, shows the exact kilogram result and applies no tolerance. The rule handles equivalent meaning; it never invents a match.” |
| 2:05–3:05 | Click **Needs Human Review**, then **Resolve Issue**. Show “Why Harbor needs you”, BL line 8 and `Notify Contact: West Trading Ltd`. Enter the supported value and reason, then **Confirm & Save Review** | “This draft uses ‘Notify Contact’, a label the extractor cannot map confidently to Notify Party. Harbor does not guess. It explains why a person is needed and surfaces the supporting BL line. I confirm `West Trading Ltd`, keep `line 8` as the source location and record the reason. Saving recomputes the report.” |
| 3:05–3:30 | Show **Review saved**, `v1 → v2`, then **View Audit History** | “The case now moves from version one to version two. Audit History preserves the automatic result, reviewer, old and new value, reason, source location and recomputed report. Running verification again retains the confirmed correction while the source remains unchanged.” |
| 3:30–3:50 | Click **Scanned Documents**. Open one OCR-backed **View Evidence** link | “Image-only PDFs run through Cloud OCR. OCR suggestions retain their page evidence and stay in Needs Review. They cannot silently clear a shipment; a person must confirm them.” |
| 3:50–4:20 | Show validation slide | “In the organizer-provided development environment, Harbor produced five hundred and twenty valid automatic predictions, identified all forty-six positive defect cases and escalated all twenty required review cases, with classification macro-F1 of one point zero. Fourteen workflow tests and the competition gate also pass. These are development results, not production-accuracy claims.” |
| 4:20–4:35 | Closing slide with live URL | “Harbor turns document extraction into an accountable shipping decision. The next step is a real-carrier pilot measuring reviewer time, correction rate and exception handling. Every decision has a source.” |

## Exact review entry for DEMO-03

- **Document:** BL
- **Field:** Notify Party
- **Correct value:** `West Trading Ltd`
- **Source location:** `line 8`
- **Reason:** `Confirmed against BL line 8: Notify Contact.`

The value comes from the draft BL source line. Do not copy from the SI merely to force a match.

## Final recording checks

- Duration is under five minutes.
- Text is readable and narration is audible.
- The public URL works without login.
- DEMO-03 visibly changes from v1 to v2.
- Audit History shows the original automatic result and the human correction.
- No organizer dataset, ground truth, private database, credentials or personal tabs appear.
- The video link works in a private browser window.
