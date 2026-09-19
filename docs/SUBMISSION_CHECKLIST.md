# Submission and helper checklist

Target: complete essential work September 20 evening. September 21 is the internal latest finish/submission day. Official deadline: September 22 noon, as stated by Nic. Confirm the portal's actual timezone. Nic travels September 22. Registration is complete.

## Nic: minimum remaining actions

- Deploy a safe demonstration build and provide a publicly accessible, functional URL. This is mandatory, not optional. Keep it available throughout preliminary judging and, conservatively, through September 26. Do not expose the unauthenticated full organizer-data workspace.
- Show meaningful AI and cloud infrastructure integration. The rules do not prescribe a vendor or stack. Document exactly which capability is AI-backed and which cloud services host or execute the solution.
- Record the under-five-minute demo using `DEMO_SCRIPT.md`. The working environment and script are prepared; no MP4 exists yet.
- Publish the source to GitHub or GitLab with a clear setup README. The source archive is ready for review; nothing has been publicly published.
- Upload the finished video to YouTube as Public or Unlisted. A private video is not evaluated. Keep it at or under five minutes; every additional 30 seconds costs one mark.
- Publish the slides/documentation with public viewer access. It must cover architecture, implementation, challenges and roadmap.
- Prepare Google Form answers for project description, problem-solution alignment, AI/cloud integration, user feedback/testing, coding challenges, success metrics and scalability.
- Confirm the deadline timezone and any portal file-size fields. Fill member details and resumes using the actual registration records.
- Test repository, live prototype, slides and video without a signed-in session. Submit by September21 and retain the receipt.
- Confirm who can attend the September 26 onsite final for the 10-minute pitch and 5-minute Q&A.

## Helper: 60–90 minutes of high-value support

1. **20 minutes:** run the demo from README on another machine if possible. On non-macOS, expect scans to require manual review without OCR. Record any startup failure instead of changing settings blindly.
2. **20 minutes:** rehearse the three product scenarios twice. Ensure the missing value starts unresolved by using a new runtime directory each time.
3. **15 minutes:** watch the finished recording end to end. Check sound, readable values, duration and accurate statements. Confirm the video shows a real report change.
4. **20 minutes:** test repository, live prototype, video and slides links in an incognito browser and on another device. Verify no organizer data is exposed and all permissions match the rules.
5. **Optional:** time ten manually checked cases and ten equivalent assisted checks, randomize order and record errors. Do not claim savings before measuring.

## Before publishing a repository

Use `Harbor_Source.zip`, not the whole workspace. The public-ready archive excludes the organizer's inbox, attachments, ground truth, generator source, runtime databases and competition screenshots. Do not upload the original Docker bundle. The private submission pack separately contains the deck and automatic predictions.

Check README startup instructions, dependency lock, owned demo files, tests and known limitations. The project uses no paid API credentials. `.env.example` documents that no key is required. A repo link is not yet available.

## Evidence to include in judging materials

- Automatic submission: 520 valid records.
- Official development-set result: 1.000 weighted score; 46/46 positive defect cases; 20/20 review cases.
- Regression variants: 38/42 first run, 42/42 after fixes.
- Frozen second suite: 40/40 first run, explicitly self-authored synthetic tests.
- Same-extraction ablation: 22/40 direct versus 40/40 full expected outcomes.
- Workflow tests and browser rehearsal evidence.
- Explicit limits: no production benchmark, OCR requires confirmation, public demo is a shared synthetic sandbox, reviewer names are unauthenticated.

## Submission status

Not submitted. The public repository destination exists at `https://github.com/nicchenai-tech/harbor-assurance`; source publication is being finalized. Remote deployment and uploaded video remain mandatory. After submission, save the portal receipt, final filenames, deployment health check and link permissions in this checklist.
