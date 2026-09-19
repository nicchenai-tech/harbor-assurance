"""Create reviewable archives from explicit allowlists, never the whole workspace."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT.parent/'harbor-delivery';OUT.mkdir(exist_ok=True)
files=[]
for name in ['README.md','pyproject.toml','requirements-lock.txt','.gitignore','.dockerignore','.env.example','Dockerfile','compose.demo.yml','render.yaml']:
    files.append(ROOT/name)
for directory in ['harbor','web','scripts','tests','demo-data']:
    files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.swift'))
files.extend((ROOT/'docs').glob('*.md'))
for name in ['release/scoreboard.json','release/run-summary.json','business-metrics.json','workflow-tests.xml','browser-qa.json','competition-gate.json','variants/first-run.json','variants/latest-run.json','variants/specifications.json','holdout/first-run.json','holdout/freeze.json','holdout/specifications.json','ablation/results.json']:
    p=ROOT/'validation'/name
    if p.exists():files.append(p)
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}
source=OUT/'Harbor_Source.zip'
with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(set(files)):z.write(p,'harbor/'+str(p.relative_to(ROOT)))
    z.writestr('harbor/RELEASE_MANIFEST.json',json.dumps(manifest,indent=2))
    z.writestr('harbor/PRIVATE_ARTIFACTS.md','The automatic 520-email submission and competition pitch are in the private submission pack. Organizer inbox, attachments, answer file, generator and runtime database are intentionally absent from this source archive.\n')
with zipfile.ZipFile(OUT/'Harbor_Submission_Pack.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.write(source,source.name)
    for p in (ROOT/'presentation').glob('*'):
        if p.suffix in ('.pptx','.pdf'):z.write(p,'presentation/'+p.name)
    for p in (ROOT/'docs').glob('*.md'):z.write(p,'docs/'+p.name)
    for name in ['submission.json','scoreboard.json','run-summary.json']:z.write(ROOT/'validation'/'release'/name,'evaluation/'+name)
    z.writestr('VIDEO_NOT_YET_RECORDED.txt','No MP4 is included. Follow docs/DEMO_SCRIPT.md to record the final video under five minutes. Do not submit this archive as though it contains a video.\n')
# Fail closed on accidentally packaged organizer files or credentials.
for package in [source,OUT/'Harbor_Submission_Pack.zip']:
    with zipfile.ZipFile(package) as z:
        names=z.namelist()
        assert not any('ground_truth' in n or 'generator' in n or 'runtime/' in n or n.endswith('.sqlite') or '/inbox/email_' in n for n in names)
    print(package,package.stat().st_size)
(OUT/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name for p in sorted(OUT.glob('*.zip')))+'\n')
