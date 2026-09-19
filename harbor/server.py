"""Evidence workspace API with a restricted public synthetic-demo mode."""
import argparse
import copy
import io
import json
import os
import shutil
import time
import uuid
from collections import Counter, defaultdict, deque
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .store import Store, Conflict
from .pipeline import process_email, run_batch
from .parsers import safe_path
from .domain import validate_submission
from .ocr import available_backend

PROJECT=Path(__file__).resolve().parent.parent


class Review(BaseModel):
    role:str
    field:str
    value:str=Field(max_length=4000)
    reviewer:str=Field(min_length=1,max_length=100)
    reason:str=Field(min_length=1,max_length=2000)
    expected_version:int
    source_location:str=Field(default='',max_length=300)


class Retry(BaseModel):
    expected_version:int
    reviewer:str='Operator'
    reason:str='Reprocess source documents.'


def create_app(source_dir,runtime_dir,public_demo=False):
    source=Path(source_dir).resolve();runtime=Path(runtime_dir).resolve()
    data=runtime/'data';data.mkdir(parents=True,exist_ok=True)
    # Working copies allow uploads without modifying organizer inputs.
    for name in ('inbox','attachments'):
        if not (data/name).exists(): shutil.copytree(source/name,data/name)
    store=Store(runtime/'harbor.sqlite')
    initial_cases=None
    if public_demo or not store.all():
        batch=runtime/'initial'
        run_batch(data,batch)
        initial_cases=json.loads((batch/'cases.json').read_text())
        if public_demo: store.reset(initial_cases)
        else: store.seed(initial_cases)
    app=FastAPI(title='Harbor',version='0.1.0')
    app.state.store=store;app.state.data=data;app.state.public_demo=public_demo
    writes=defaultdict(deque)

    @app.middleware('http')
    async def local_origin(request:Request,call_next):
        # Prevent cross-origin browser writes to the local reviewer service.
        origin=request.headers.get('origin')
        if request.method not in ('GET','HEAD','OPTIONS') and origin and origin not in (str(request.base_url).rstrip('/'),):
            return Response('Cross-origin writes are not allowed.',status_code=403)
        if public_demo and request.method not in ('GET','HEAD','OPTIONS'):
            key=request.client.host if request.client else 'unknown';now=time.monotonic();bucket=writes[key]
            while bucket and bucket[0]<now-60:bucket.popleft()
            if len(bucket)>=20:return Response('Demo write limit reached. Wait one minute.',status_code=429)
            bucket.append(now)
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
        response.headers['Content-Security-Policy']="default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        return response

    @app.exception_handler(Conflict)
    async def conflict_handler(request,exc): return Response(str(exc),status_code=409)

    def get(eid):
        try:return store.get(eid)
        except KeyError:raise HTTPException(404,'Case not found.')

    @app.get('/api/health')
    def health():return {'status':'ok','emails':len(store.all()),
        'mode':'public synthetic sandbox' if public_demo else 'local workspace',
        'ocr_backend':available_backend(),'uploads_enabled':not public_demo,
        'ai_policy':'OCR proposes evidence; deterministic rules compare; uncertain values require a person.'}

    @app.post('/api/demo/reset')
    def reset_demo():
        if not public_demo:raise HTTPException(404,'Demo reset is only available in public mode.')
        store.reset(initial_cases)
        return {'status':'reset','emails':len(initial_cases)}

    @app.get('/api/cases')
    def cases():
        rows=store.all()
        return {'counts':dict(Counter(c['workflow_state'] for c in rows)),
                'cases':[{'id':c['email_id'],'subject':c['email']['subject'],'sender':c['email']['from'],
                          'category':c['classification']['category'],'state':c['workflow_state'],
                          'defects':c['known_defects'],'version':c['report_version'],
                          'attachments':len(c['email']['attachments'])} for c in rows]}

    @app.get('/api/cases/{eid}')
    def case(eid):return get(eid)

    @app.get('/api/cases/{eid}/versions')
    def versions(eid):get(eid);return store.versions(eid)

    @app.post('/api/cases/{eid}/review')
    def review(eid,payload:Review):
        get(eid)
        try:return store.correct(eid,**payload.model_dump())
        except Conflict:raise
        except ValueError as exc:raise HTTPException(400,str(exc))

    @app.post('/api/cases/{eid}/retry')
    def retry(eid,payload:Retry):
        previous=get(eid)
        fresh=process_email(previous['email'],data)
        return store.retry(eid,fresh,payload.reviewer,payload.reason,payload.expected_version)

    @app.post('/api/cases/{eid}/upload')
    async def upload(eid,file:UploadFile=File(...),replace_file:str=Form(''),reviewer:str=Form(...),reason:str=Form(...),expected_version:int=Form(...)):
        if public_demo:raise HTTPException(403,'Uploads are disabled in the public sandbox. Run Harbor locally to test private documents.')
        previous=get(eid)
        if previous['report_version']!=expected_version:raise Conflict('Case changed. Reload before upload.')
        if not reviewer.strip() or not reason.strip():raise HTTPException(400,'Reviewer and reason required.')
        suffix=Path(file.filename or '').suffix.lower()
        if suffix not in ('.txt','.pdf','.docx','.xlsx'):raise HTTPException(400,'Upload TXT, PDF, DOCX or XLSX.')
        content=await file.read(20*1024*1024+1)
        if not content or len(content)>20*1024*1024:raise HTTPException(400,'File must be between 1 byte and 20 MB.')
        email=copy.deepcopy(previous['email'])
        if replace_file:
            if replace_file not in email['attachments']:raise HTTPException(400,'Replacement source is not part of this case.')
            email['attachments'].remove(replace_file)
        name='uploads/'+uuid.uuid4().hex+suffix
        (data/'uploads').mkdir(exist_ok=True)
        (data/name).write_bytes(content)
        email['attachments'].append(name)
        fresh=process_email(email,data)
        result=store.retry(eid,fresh,reviewer,'Attachment update: '+reason,expected_version)
        return result

    @app.get('/api/cases/{eid}/document/{index}')
    def document(eid,index:int):
        c=get(eid)
        if index<0 or index>=len(c['documents']):raise HTTPException(404)
        p=safe_path(data,c['documents'][index]['file'])
        return FileResponse(p,filename=p.name,content_disposition_type='inline' if p.suffix=='.pdf' else 'attachment')

    @app.get('/api/cases/{eid}/preview/{index}/{page}')
    def preview(eid,index:int,page:int):
        c=get(eid)
        if index<0 or index>=len(c['documents']):raise HTTPException(404)
        p=safe_path(data,c['documents'][index]['file'])
        if p.suffix.lower()!='.pdf':raise HTTPException(400,'Preview is available for PDF pages.')
        try:
            import pypdfium2 as pdfium
            pdf=pdfium.PdfDocument(str(p))
            if not 1<=page<=len(pdf):raise ValueError('Invalid page.')
            pg=pdf[page-1];bitmap=pg.render(scale=1.5);image=bitmap.to_pil()
            buf=io.BytesIO();image.save(buf,format='PNG');bitmap.close();pg.close();pdf.close()
            return Response(buf.getvalue(),media_type='image/png')
        except Exception:raise HTTPException(422,'This PDF cannot be rendered. Replace the damaged file.')

    @app.get('/api/export')
    def export(original:bool=True):
        rows=store.all(original=original)
        sub={c['email_id']:c['prediction'] for c in rows}
        validate_submission(sub,[c['email_id'] for c in rows])
        return Response(json.dumps(sub,indent=2),media_type='application/json',headers={'Content-Disposition':f'attachment; filename="submission-{ "automatic" if original else "reviewed"}.json"'})

    @app.get('/api/cases/{eid}/report')
    def report(eid):
        c=get(eid)
        return Response(json.dumps(c,ensure_ascii=False,indent=2),media_type='application/json',headers={'Content-Disposition':f'attachment; filename="{eid}-report-v{c["report_version"]}.json"'})

    app.mount('/',StaticFiles(directory=PROJECT/'web',html=True),name='web')
    return app


def main():
    p=argparse.ArgumentParser()
    public=os.getenv('HARBOR_PUBLIC_DEMO','').lower() in ('1','true','yes')
    p.add_argument('--data',default=os.getenv('HARBOR_DATA',str(PROJECT/'demo-data' if public else PROJECT.parent/'participant-data')))
    p.add_argument('--runtime',default=os.getenv('HARBOR_RUNTIME',str(PROJECT/'runtime-demo' if public else PROJECT/'runtime')))
    p.add_argument('--port',type=int,default=int(os.getenv('PORT','8765')))
    p.add_argument('--host',default=os.getenv('HARBOR_HOST','0.0.0.0' if public else '127.0.0.1'))
    p.add_argument('--public-demo',action='store_true',default=public)
    args=p.parse_args()
    import uvicorn
    uvicorn.run(create_app(args.data,args.runtime,args.public_demo),host=args.host,port=args.port)


if __name__=='__main__':main()
