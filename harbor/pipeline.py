"""Pure per-email processing and batch export with case-level failure isolation."""
from pathlib import Path
import json
import time
from .classifier import classify, awaiting_documents
from .parsers import read_document, document_role
from .extract import extract_fields
from .domain import FIELDS, equal, prediction, validate_submission


def compare(case):
    comparisons=[]
    uncertain=[]
    defects=[]
    for f in FIELDS:
        a=case.get('fields',{}).get('SI',{}).get(f)
        b=case.get('fields',{}).get('BL',{}).get(f)
        if not a or not b or a['normalized_value'] is None or b['normalized_value'] is None or a.get('warning') or b.get('warning'):
            state='REVIEW'; reason='Missing, ambiguous or invalid source value.'; uncertain.append(f)
        elif any(x.get('requires_confirmation') and not x.get('confirmed') for x in (a,b)):
            state='REVIEW';reason='OCR suggestion requires human confirmation.';uncertain.append(f)
        else:
            state='MATCH' if equal(f,a['normalized_value'],b['normalized_value']) else 'MISMATCH'
            reason='Equivalent after the stated normalization.' if state=='MATCH' else 'SI and BL values differ after normalization.'
            if state=='MISMATCH': defects.append(f)
        comparisons.append({'field':f,'state':state,'reason':reason,'SI':a,'BL':b})
    case['comparisons']=comparisons
    case['unresolved_fields']=uncertain
    case['known_defects']=defects
    return uncertain,defects


def decide(case):
    category=case['classification']['category']
    if category!='BL_COMPARISON':
        case['workflow_state']='classified'
        case['prediction']=prediction(category)
        return case
    uncertain,defects=compare(case)
    docs=case['documents']
    roles=[d['role'] for d in docs]
    reason=None
    if any(d['errors'] for d in docs): reason='unreadable'
    elif any(r=='OTHER' for r in roles): reason='wrong_doc_type'
    elif not docs or len(docs)<2: reason='missing_attachment'
    elif roles.count('SI')!=1 or roles.count('BL')!=1: reason='unreadable' if any(d['scan'] for d in docs) else 'wrong_doc_type'
    elif uncertain: reason='unreadable' if any(d['scan'] for d in docs) else 'missing_value'
    if reason:
        case['workflow_state']='awaiting_documents' if reason=='missing_attachment' and awaiting_documents(case['email']) else 'needs_review'
        case['prediction']=prediction(category) if case['workflow_state']=='awaiting_documents' else prediction(category,'NEEDS_REVIEW',reason=reason)
        case['processing_errors']=[error for d in docs for error in d['errors'] if any(word in error.lower() for word in ('timed out','timeout','worker failed'))]
        if case['processing_errors']:
            case['workflow_state']='processing_failed'
        case['decision_reason']={'unreadable':'Source could not be read reliably. Inspect the file or replace it.',
          'wrong_doc_type':'Exactly one SI and one draft BL are required. Check document content and roles.',
          'missing_attachment':'The documents needed for verification have not both been received.',
          'missing_value':'One or more required values are missing, invalid or conflicting.'}[reason]
        if case['workflow_state']=='awaiting_documents': case['export_note']='Pending document request maps to OK in evaluator only. No verification has occurred.'
    else:
        case['workflow_state']='mismatch' if defects else 'verified_ok'
        case['prediction']=prediction(category,'MISMATCH' if defects else 'OK',defects)
        case['decision_reason']='Differences require correction before release.' if defects else 'No mismatch detected.'
    return case


def process_email(email,root,reader=read_document):
    start=time.perf_counter()
    case={'email_id':email['email_id'],'email':email,'classification':classify(email),
          'documents':[],'fields':{},'comparisons':[],'unresolved_fields':[], 'known_defects':[],
          'report_version':1,'engine_version':'0.1.0','review_events':[],'processing_errors':[]}
    if case['classification']['category']=='BL_COMPARISON':
        for path in email.get('attachments',[]):
            try:
                doc=reader(root,path)
            except Exception as exc:
                doc={'file':path,'sha256':None,'format':Path(path).suffix,'lines':[], 'scan':False,
                     'method':'native_text','errors':[f'{type(exc).__name__}: {str(exc)[:200]}']}
            doc['role']=document_role(doc)
            case['documents'].append(doc)
            if doc['role'] in ('SI','BL') and doc['role'] not in case['fields']:
                case['fields'][doc['role']]=extract_fields(doc)
    decide(case)
    case['elapsed_ms']=round((time.perf_counter()-start)*1000,2)
    return case


def run_batch(root,out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter();cases=[]
    for p in sorted((root/'inbox').glob('*.json')):
        email=json.loads(p.read_text())
        cases.append(process_email(email,root))
    submission={c['email_id']:c['prediction'] for c in cases}
    validate_submission(submission,[c['email_id'] for c in cases])
    (out/'submission.json').write_text(json.dumps(submission,indent=2))
    (out/'cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2))
    from collections import Counter
    summary={'emails':len(cases),'elapsed_seconds':round(time.perf_counter()-start,3),
             'categories':dict(Counter(c['classification']['category'] for c in cases)),
             'states':dict(Counter(c['workflow_state'] for c in cases)),
             'schema_valid':True,'cloud_model_calls':0,
             'ocr_documents':sum(d['method'].endswith('_ocr') for c in cases for d in c['documents']),
             'note':'Evidence-led rules and native document parsers; OCR suggestions require human confirmation.'}
    (out/'run-summary.json').write_text(json.dumps(summary,indent=2))
    return summary
