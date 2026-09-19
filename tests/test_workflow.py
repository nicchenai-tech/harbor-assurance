import copy
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from harbor.pipeline import process_email
from harbor.domain import normalize, validate_submission
from harbor.store import Store, Conflict

SI='''SHIPPING INSTRUCTION
Shipper: North Paper Ltd
  12 Orchard Road, Singapore
Consignee: West Trading Ltd
Notify Party: West Trading Ltd
Port of Loading: Singapore
Port of Discharge: Fremantle, Australia
Container Count: 3 x 40'HC
Gross Weight (KG): 22,000 KG
'''
BL=SI.replace('SHIPPING INSTRUCTION','BILL OF LADING (DRAFT)').replace('3 x 40','4 x 40')


@pytest.fixture
def case_data(tmp_path):
    (tmp_path/'a.txt').write_text(SI)
    (tmp_path/'b.txt').write_text(BL)
    email={'email_id':'independent-case','from':'shipping@example.test','subject':'Documents for review',
           'body':'Please compare the SI and draft BL and confirm the details.','attachments':['a.txt','b.txt']}
    return tmp_path,email


def test_core_source_and_export(case_data):
    root,email=case_data;c=process_email(email,root)
    assert c['prediction']['defect_fields']==['container_count']
    assert c['fields']['SI']['container_count']['normalized_value']==3
    assert '3 x 40' in c['fields']['SI']['container_count']['evidence']
    assert c['fields']['SI']['shipper']['raw_value'].endswith('Singapore')
    validate_submission({email['email_id']:c['prediction']},[email['email_id']])


def test_review_persists_and_retry_preserves(case_data,tmp_path):
    root,email=case_data;c=process_email(email,root)
    db=tmp_path/'case.sqlite';store=Store(db);store.seed([c])
    reviewed=store.correct(email['email_id'],'BL','container_count',"3 x 40'HC",'Nic','Confirmed against carrier amendment.',1)
    assert reviewed['workflow_state']=='verified_ok'
    assert reviewed['report_version']==2
    store=Store(db)
    assert store.get(email['email_id'])['prediction']['status']=='OK'
    assert store.get(email['email_id'],original=True)['prediction']['status']=='MISMATCH'
    retried=store.retry(email['email_id'],process_email(email,root),'Nic','Retry after correction',2)
    assert retried['prediction']['status']=='OK'
    assert retried['review_events'][-1]['preserved_corrections']==['BL.container_count']
    assert len(store.versions(email['email_id']))==3
    with pytest.raises(Conflict):store.correct(email['email_id'],'BL','container_count','2','Nic','Stale browser tab',1)


def test_changed_source_invalidates_correction(case_data,tmp_path):
    root,email=case_data;store=Store(tmp_path/'case.sqlite');store.seed([process_email(email,root)])
    store.correct(email['email_id'],'BL','container_count','3','Reviewer','Checked source.',1)
    (root/'b.txt').write_text(BL.replace('4 x','5 x'))
    updated=store.retry(email['email_id'],process_email(email,root),'Reviewer','Changed attachment',2)
    assert updated['workflow_state']=='needs_review'
    assert updated['review_events'][-1]['stale_corrections']==['BL.container_count']


def test_missing_source_not_clean(case_data):
    root,email=case_data;email['attachments']=['a.txt']
    c=process_email(email,root)
    assert c['prediction']['status']=='NEEDS_REVIEW'
    assert c['prediction']['review_reason']=='missing_attachment'


def test_corrupt_file_isolated(case_data):
    root,email=case_data;(root/'broken.pdf').write_bytes(b'%PDF-1.4 broken')
    email['attachments']=['a.txt','broken.pdf'];c=process_email(email,root)
    assert c['prediction']['status']=='NEEDS_REVIEW'
    assert c['documents'][-1]['errors']
    assert process_email({**email,'attachments':['a.txt','b.txt']},root)['prediction']['status']=='MISMATCH'


def test_timeout_is_visible(case_data):
    def timeout(*args):raise TimeoutError('Reader timed out')
    root,email=case_data;c=process_email(email,root,reader=timeout)
    assert c['prediction']['review_reason']=='unreadable'
    assert 'TimeoutError' in c['documents'][0]['errors'][0]
    assert c['workflow_state']=='processing_failed'


def test_numeric_missing_and_units():
    assert normalize('gross_weight_kg','22 MT')[0]=='22000'
    assert normalize('gross_weight_kg','22000 KG')[0]=='22000'
    assert normalize('gross_weight_kg','22,5 KG')[0] is None
    assert normalize('gross_weight_kg','N/A')[0] is None
    assert normalize('gross_weight_kg','0 KG')[0]=='0'
    assert normalize('container_count',"15 x 20'GP")[0]==15


def test_id_filename_attachment_order_invariance(case_data):
    root,email=case_data;c=process_email(email,root)
    (root/'renamed.txt').write_text(SI)
    other={**email,'email_id':'other-id','attachments':['b.txt','renamed.txt']}
    assert process_email(other,root)['prediction']==c['prediction']


def test_wrong_document_content(case_data):
    root,email=case_data;(root/'b.txt').write_text('COMMERCIAL INVOICE\nSeller: North Paper Ltd\nWeight: 22,000 KG')
    assert process_email(email,root)['prediction']['review_reason']=='wrong_doc_type'


def test_api_and_upload(case_data,tmp_path):
    import json
    from harbor.server import create_app
    root,email=case_data
    source=tmp_path/'source';(source/'inbox').mkdir(parents=True);(source/'attachments').mkdir()
    for name in ['a.txt','b.txt']:(source/'attachments'/name).write_text((root/name).read_text())
    email['attachments']=['attachments/a.txt','attachments/b.txt']
    (source/'inbox'/'email.json').write_text(json.dumps(email))
    app=create_app(source,tmp_path/'server-runtime')
    with TestClient(app) as client:
        assert client.get('/api/health').json()['emails']==1
        eid=email['email_id']
        response=client.post(f'/api/cases/{eid}/review',json={'role':'BL','field':'container_count','value':'3','reviewer':'Nic','reason':'Carrier amendment verified.','expected_version':1})
        assert response.status_code==200,response.text
        assert response.json()['workflow_state']=='verified_ok'
        assert client.get('/api/export').json()[eid]['status']=='MISMATCH'
        assert client.get('/api/export?original=false').json()[eid]['status']=='OK'
        response=client.post(f'/api/cases/{eid}/upload',data={'replace_file':'attachments/b.txt','reviewer':'Nic','reason':'New draft','expected_version':2},files={'file':('draft.txt',BL.replace('4 x','5 x').encode(),'text/plain')})
        assert response.status_code==200,response.text
        assert response.json()['workflow_state']=='needs_review'
        assert client.post(f'/api/cases/{eid}/retry',headers={'Origin':'https://unrelated.test'},json={'expected_version':3}).status_code==403
        assert (source/'attachments'/'b.txt').read_text()==BL


def test_real_parser_deadline(case_data):
    from harbor.parsers import read_document
    root,email=case_data
    doc=read_document(root,email['attachments'][0],timeout=0.00001)
    assert 'timed out' in doc['errors'][0]
    assert not doc['lines']


def test_unlocated_value_requires_human_source_location(case_data,tmp_path):
    root,email=case_data
    (root/'b.txt').write_text(BL.replace('Notify Party: West Trading Ltd\n','')+'\nNotify Contact: West Trading Ltd\n')
    store=Store(tmp_path/'location.sqlite');store.seed([process_email(email,root)])
    with pytest.raises(ValueError,match='source page'):
        store.correct(email['email_id'],'BL','notify_party','West Trading Ltd','Reviewer','Checked original',1)
    c=store.correct(email['email_id'],'BL','notify_party','West Trading Ltd','Reviewer','Checked original',1,source_location='last line: Notify Contact')
    assert c['fields']['BL']['notify_party']['reviewer_source_location']=='last line: Notify Contact'
    assert c['fields']['BL']['notify_party']['original_observation']['raw_value'] is None


def test_tesseract_tsv_groups_words_with_source_boxes():
    from harbor.ocr import _tesseract_rows
    header='level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n'
    body='5\t1\t1\t1\t1\t1\t10\t20\t40\t12\t96\tGross\n5\t1\t1\t1\t1\t2\t55\t20\t50\t12\t94\tWeight\n'
    rows=_tesseract_rows(header+body,(200,100),(180,80),(10,10,190,90))
    assert rows[0]['text']=='Gross Weight'
    assert rows[0]['backend']=='tesseract'
    assert rows[0]['confidence']==95.0
    assert rows[0]['bbox']==[0.1,0.3,0.475,0.12]


def test_public_demo_is_bounded_and_resettable(tmp_path):
    import json
    from harbor.server import create_app
    source=tmp_path/'public-source';(source/'inbox').mkdir(parents=True);(source/'attachments').mkdir()
    (source/'attachments'/'a.txt').write_text(SI);(source/'attachments'/'b.txt').write_text(BL)
    email={'email_id':'demo','from':'ops@example.test','subject':'Compare documents',
           'body':'Please compare the SI and draft BL.','attachments':['attachments/a.txt','attachments/b.txt']}
    (source/'inbox'/'demo.json').write_text(json.dumps(email))
    with TestClient(create_app(source,tmp_path/'public-runtime',public_demo=True)) as client:
        health=client.get('/api/health').json()
        assert health['mode']=='public synthetic sandbox' and not health['uploads_enabled']
        reviewed=client.post('/api/cases/demo/review',json={'role':'BL','field':'container_count','value':'3','reviewer':'Judge','reason':'Checked source.','expected_version':1})
        assert reviewed.status_code==200 and reviewed.json()['report_version']==2
        assert client.post('/api/demo/reset').json()['status']=='reset'
        assert client.get('/api/cases/demo').json()['report_version']==1
        blocked=client.post('/api/cases/demo/upload',data={'reviewer':'Judge','reason':'Test','expected_version':1},files={'file':('x.txt',b'x','text/plain')})
        assert blocked.status_code==403
