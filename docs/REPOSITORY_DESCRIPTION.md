# Suggested repository description

Harbor: evidence-linked shipping document verification with deterministic checks and human review, built for Averis × Monash Hackathon 2026.

# Suggested submission abstract

Harbor checks a draft bill of lading against shipping instructions and gives shipping operations reviewers a traceable decision. It routes five email categories, reads TXT/PDF/DOCX/XLSX documents, verifies document roles, and compares seven required fields using explicit normalization rules. Every extracted value retains its original source and location. Uncertain values, scans and damaged documents become human tasks. Corrections produce versioned reports, while retries preserve confirmations only when the source is unchanged.

The automatic submission covers all 520 supplied emails. Official development evaluation reports all 46 positive defect cases detected end to end and all 20 required review cases escalated. A separate frozen suite of 40 self-authored semantic variants passed on its first run. Harbor includes a restricted public cloud sandbox with Apple Vision/Tesseract OCR, deterministic checks and versioned human review. These are development and synthetic-test results; production use still needs real-data validation, authenticated review and stronger layout handling.
