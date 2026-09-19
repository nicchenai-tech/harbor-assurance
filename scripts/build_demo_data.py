"""Owned synthetic fixtures for repeatable, non-destructive live rehearsal."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'demo-data'
(DATA/'inbox').mkdir(parents=True,exist_ok=True);(DATA/'attachments').mkdir(exist_ok=True)
BASE='''{title}
Shipper: North Paper Ltd
Consignee: West Trading Ltd
Port of Loading: Singapore
Port of Discharge: Fremantle, Australia
Container Count: 3 x 40'HC
Gross Weight (KG): 22,000 KG
Notify Party: West Trading Ltd
'''
SI=BASE.format(title='SHIPPING INSTRUCTION');BL=BASE.format(title='DRAFT BILL OF LADING')
def add(eid,subject,body,a=None,b=None):
    att=[]
    for role,text in [('SI',a),('BL',b)]:
        if text is not None:
            name=f'attachments/{eid}-{role}.txt';(DATA/name).write_text(text);att.append(name)
    (DATA/'inbox'/f'{eid}.json').write_text(json.dumps({'email_id':eid,'subject':subject,'from':'operations@example.test','body':body,'attachments':att},indent=2))
body='Please compare the SI and draft BL and confirm all fields.'
add('demo-01','Carrier draft: container quantity differs',body,SI,BL.replace("3 x 40'HC","4 x 40'HC"))
add('demo-02','Equivalent weights: KG and MT',body,SI,BL.replace('22,000 KG','22 MT'))
add('demo-03','New template: notify contact needs confirmation',body,SI,BL.replace('Notify Party:','Notify Contact:'))
add('demo-04','Shipping instruction request','Please send shipping instruction for the next sailing.')
add('demo-05','Invoice amount clarification','Please amend the invoice amount.')
add('demo-06','Document request pending','Please send the draft BL for checking.')
# Actual corrected source, used to demonstrate attachment replacement.
(DATA/'carrier-amended-BL.txt').write_text(BL)
print(DATA)
