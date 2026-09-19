"""Paired ablation: identical parser output, direct text equality vs full logic."""
from pathlib import Path
import json,sys,re
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from harbor.pipeline import process_email
from harbor.domain import FIELDS
import validate_holdout as suite
out=suite.suite.ROOT/'validation'/'ablation';out.mkdir(parents=True,exist_ok=True)
rows=[]
for spec in suite.suite.specs:
    root=suite.suite.ROOT/'validation'/'holdout'/'inputs'/spec['name']
    email=json.loads((root/'email.json').read_text())
    def timeout(*args):raise TimeoutError('Injected parser deadline exceeded')
    c=process_email(email,root,reader=timeout) if spec.get('timeout') else process_email(email,root)
    # Honest minimal baseline: same classification/parser/field extraction,
    # missing/unreadable inputs abstain, raw text case and whitespace normalized.
    # No unit conversion, quantity parsing, role exclusion or OCR confirmation gate.
    docs=c['documents']; a=c['fields'].get('SI',{});b=c['fields'].get('BL',{})
    review=any(d['errors'] for d in docs) or any(not a.get(f,{}).get('raw_value') or not b.get(f,{}).get('raw_value') for f in FIELDS)
    direct=lambda x:' '.join(str(x).casefold().split())
    diffs=[] if review else [f for f in FIELDS if direct(a[f]['raw_value'])!=direct(b[f]['raw_value'])]
    base={'status':'NEEDS_REVIEW' if review else 'MISMATCH' if diffs else 'OK','defect_fields':diffs}
    expected={'status':spec['status'],'defect_fields':spec['fields']}
    full={k:c['prediction'][k] for k in expected}
    rows.append({'name':spec['name'],'expected':expected,'baseline':base,'full':full,'baseline_correct':base==expected,'full_correct':full==expected})
report={'design':'All 40 held-out semantic fixtures. Same extracted values. Baseline already abstains for missing/unreadable inputs and normalizes case/whitespace. Deterministic operations only; no inference-cost advantage claimed.',
 'n':len(rows),'baseline_exact':sum(r['baseline_correct'] for r in rows),'full_exact':sum(r['full_correct'] for r in rows),
 'baseline_false_alarms_on_clean':sum(r['expected']['status']=='OK' and r['baseline']['status']=='MISMATCH' for r in rows),
 'full_false_alarms_on_clean':sum(r['expected']['status']=='OK' and r['full']['status']=='MISMATCH' for r in rows),
 'baseline_unsafe_ok_on_review':sum(r['expected']['status']=='NEEDS_REVIEW' and r['baseline']['status']=='OK' for r in rows),
 'full_unsafe_ok_on_review':sum(r['expected']['status']=='NEEDS_REVIEW' and r['full']['status']=='OK' for r in rows),
 'clean_n':sum(r['expected']['status']=='OK' for r in rows),'review_n':sum(r['expected']['status']=='NEEDS_REVIEW' for r in rows),'rows':rows}
(out/'results.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
