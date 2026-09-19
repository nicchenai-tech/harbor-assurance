"""Fail-closed summary of the evidence Harbor can substantiate."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
load=lambda name:json.loads((ROOT/name).read_text())
official=load('validation/release/scoreboard.json')
first=load('validation/variants/first-run.json');latest=load('validation/variants/latest-run.json')
holdout=load('validation/holdout/first-run.json');ablation=load('validation/ablation/results.json')
checks={
  'official_development_score_1':official['final_score']==1,
  'classification_macro_f1_1':official['stage1']['macro_f1']==1,
  'positive_defect_sets_46_of_46':official['end_to_end']=={'success':46,'total':46,'rate':1.0},
  'review_cases_20_of_20':official['reliability']['gold_review']==official['reliability']['pred_review']==20,
  'regression_42_of_42':latest['passed']==latest['total']==42,
  'frozen_first_run_40_of_40':holdout['passed']==holdout['total']==40,
  'first_failures_retained':first['passed']==38 and first['total']==42,
  'ablation_improves_22_to_40':ablation['baseline_exact']==22 and ablation['full_exact']==40,
  'public_demo_has_only_owned_ids':all(p.stem.startswith('demo-') for p in (ROOT/'demo-data'/'inbox').glob('*.json')),
  'portable_container_present':(ROOT/'Dockerfile').exists() and (ROOT/'render.yaml').exists(),
}
report={'status':'pass' if all(checks.values()) else 'fail','checks':checks,
        'claim':'Measured development and authored-test evidence only; no comparison with unseen competitor systems or production accuracy claim.'}
(ROOT/'validation'/'competition-gate.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['status']=='pass' else 1)
