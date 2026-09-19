"""SQLite case versions and immutable originals; optimistic reviewer concurrency."""
import copy
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .domain import FIELDS, normalize
from .pipeline import decide


class Conflict(ValueError): pass


class Store:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY, original TEXT NOT NULL, current TEXT NOT NULL, version INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL, event TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS reports(case_id TEXT NOT NULL, version INTEGER NOT NULL, body TEXT NOT NULL, PRIMARY KEY(case_id,version));
            ''')

    def connect(self):
        db=sqlite3.connect(self.path,timeout=20)
        db.row_factory=sqlite3.Row
        return db

    def seed(self,cases):
        with self.connect() as db:
            for case in cases:
                body=json.dumps(case)
                db.execute('INSERT OR IGNORE INTO cases VALUES(?,?,?,?)',(case['email_id'],body,body,1))
                db.execute('INSERT OR IGNORE INTO reports VALUES(?,?,?)',(case['email_id'],1,body))

    def reset(self,cases):
        """Restore a synthetic public sandbox without touching the source fixtures."""
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('DELETE FROM events');db.execute('DELETE FROM reports');db.execute('DELETE FROM cases')
            for case in cases:
                body=json.dumps(case)
                db.execute('INSERT INTO cases VALUES(?,?,?,?)',(case['email_id'],body,body,1))
                db.execute('INSERT INTO reports VALUES(?,?,?)',(case['email_id'],1,body))

    def get(self,eid,original=False):
        with self.connect() as db:
            row=db.execute('SELECT * FROM cases WHERE id=?',(eid,)).fetchone()
            if row is None: raise KeyError(eid)
            case=json.loads(row['original' if original else 'current'])
            if not original:
                case['review_events']=[json.loads(e['event']) for e in db.execute('SELECT event FROM events WHERE case_id=? ORDER BY id',(eid,))]
            return case

    def all(self,original=False):
        with self.connect() as db:
            return [json.loads(r['original' if original else 'current']) for r in db.execute('SELECT * FROM cases ORDER BY id')]

    def commit(self,case,event,expected_version):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT version FROM cases WHERE id=?',(case['email_id'],)).fetchone()
            if row is None: raise KeyError(case['email_id'])
            if row['version']!=expected_version: raise Conflict('This case changed. Reload before saving your review.')
            case=copy.deepcopy(case)
            case['report_version']=expected_version+1
            event={**event,'timestamp':datetime.now(timezone.utc).isoformat(),'version':case['report_version']}
            case['review_events']=[]
            body=json.dumps(case)
            db.execute('UPDATE cases SET current=?,version=? WHERE id=?',(body,case['report_version'],case['email_id']))
            db.execute('INSERT INTO events(case_id,event) VALUES(?,?)',(case['email_id'],json.dumps(event)))
            db.execute('INSERT INTO reports VALUES(?,?,?)',(case['email_id'],case['report_version'],body))
        return self.get(case['email_id'])

    def correct(self,eid,role,field,value,reviewer,reason,expected_version,source_location=''):
        if role not in ('SI','BL') or field not in FIELDS: raise ValueError('Invalid document role or field.')
        if not reviewer.strip() or not reason.strip(): raise ValueError('Reviewer and reason are required.')
        case=self.get(eid)
        if role not in case['fields']: raise ValueError('A readable source document with this role is required. Add or replace the document first.')
        old=copy.deepcopy(case['fields'][role][field])
        if not old.get('locator') and not source_location.strip():
            raise ValueError('Enter the source page, line or cell for a value the parser did not locate.')
        norm,rule,warning=normalize(field,value,old.get('label', 'Gross Weight (KG)' if field=='gross_weight_kg' else field))
        if warning: raise ValueError(warning)
        new={**old,'raw_value':value,'normalized_value':norm,'warning':None,'confirmed':True,
             'method':'human_review','normalization':rule,'review_reason':reason,
             'original_observation':old.get('original_observation',old)}
        if source_location.strip():
            new['reviewer_source_location']=source_location.strip()
        case['fields'][role][field]=new
        decide(case)
        event={'action':'field_correction','role':role,'field':field,'before':old,'after':new,'reviewer':reviewer,'reason':reason,'source_hash':old.get('source_hash')}
        return self.commit(case,event,expected_version)

    def retry(self,eid,new_case,reviewer,reason,expected_version):
        previous=self.get(eid)
        preserved=[];stale=[]
        for role,fields in previous.get('fields',{}).items():
            for f,old in fields.items():
                if old.get('method')!='human_review': continue
                fresh=new_case.get('fields',{}).get(role,{}).get(f)
                if fresh and fresh.get('source_hash')==old.get('source_hash'):
                    new_case['fields'][role][f]=copy.deepcopy(old);preserved.append(f'{role}.{f}')
                elif fresh:
                    fresh['warning']='Source changed after human review. Confirm this value again.'
                    stale.append(f'{role}.{f}')
        decide(new_case)
        return self.commit(new_case,{'action':'retry','reviewer':reviewer,'reason':reason,'preserved_corrections':preserved,'stale_corrections':stale},expected_version)

    def versions(self,eid):
        with self.connect() as db:
            return [{'version':r['version'],'prediction':json.loads(r['body'])['prediction']} for r in db.execute('SELECT version,body FROM reports WHERE case_id=? ORDER BY version',(eid,))]
