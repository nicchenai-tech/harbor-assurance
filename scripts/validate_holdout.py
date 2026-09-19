"""Second suite: expectations frozen before execution; do not tune on outcomes.
Self-authored contract tests, not an external or statistically representative set.
"""
import validate_variants as suite
from pathlib import Path
import hashlib,json
suite.specs=[]
case=suite.case
# New shipment identity and amounts, never copied from organizer documents.
suite.SI=suite.SI.replace('Cedar Export Ltd','Maple Fiber Co Ltd').replace('Ocean Supply Ltd','Bluewater Imports LLC').replace('Singapore','Port Klang').replace('Brisbane, Australia','Kobe, Japan').replace("5 x 20'GP","8 x 40'HC").replace('18,500 KG','24,640 KG')
suite.BL=suite.SI.replace('SHIPPING INSTRUCTION','DRAFT BILL OF LADING')
case('mixed_sizes_eight',[["8 x 40'HC","3 x 20'GP + 5 x 40'HC"]])
case('uppercase_unit_and_quantity',[["8 x 40'HC",'8 containers'],['24,640 KG','24.640 MT']])
case('three_quantity_terms',[["8 x 40'HC","2 x 20'GP; 4 x 40'HC; 2 x 45'HC"]])
case('new_weight_no_separator',[['24,640 KG','24640 KG']])
case('new_weight_tonnes',[['24,640 KG','24.64 tonnes']])
case('new_weight_label_mts',[['Gross Weight (KG): 24,640 KG','Gross Weight (MTS): 24.64']])
case('new_case_and_punctuation',[['Maple Fiber Co Ltd','MAPLE FIBER CO., LTD.']])
case('ports_long_labels',[['Port of Loading:','Load Port:'],['Port of Discharge:','Discharge Port:']])
case('distinct_si_bl_titles',[['DRAFT BILL OF LADING','BILL OF LADING (DRAFT)']])
case('same_fields_reverse_order',reverse=True)
case('new_identifier_and_filename',eid='case-c0b8cb4a',names=['unrelated.txt','another.txt'])
case('word_fields_new_identity',format='docx')
case('xlsx_new_identity',format='xlsx')
case('pdf_new_identity',format='pdf')
case('new_notify_diff',[['Notify Party: Bluewater Imports LLC','Notify Party: Greenwater Imports LLC']],status='MISMATCH',fields=['notify_party'])
case('new_consignee_diff',[['Consignee: Bluewater Imports LLC','Consignee: Bluewater Exports LLC']],status='MISMATCH',fields=['consignee'])
case('new_discharge_diff',[['Kobe, Japan','Osaka, Japan']],status='MISMATCH',fields=['port_of_discharge'])
case('numeric_rounding_not_allowed',[['24,640 KG','24640.01 KG']],status='MISMATCH',fields=['gross_weight_kg'])
case('seven_instead_eight',[["8 x 40'HC",'7']],status='MISMATCH',fields=['container_count'])
case('three_real_defects',[["8 x 40'HC",'9'],['24,640 KG','26 MT'],['Kobe, Japan','Osaka, Japan']],status='MISMATCH',fields=['port_of_discharge','container_count','gross_weight_kg'])
case('missing_shipper_value',[['Shipper: Maple Fiber Co Ltd','Shipper: TBD']],status='NEEDS_REVIEW')
case('blank_weight',[['24,640 KG','---']],status='NEEDS_REVIEW')
case('zero_container_count',[["8 x 40'HC",'0']],status='NEEDS_REVIEW')
case('unknown_container_size',[["8 x 40'HC",'8 x 99']],status='NEEDS_REVIEW')
case('partial_quantity_with_tba',[["8 x 40'HC","8 x 40'HC + TBA"]],status='NEEDS_REVIEW')
case('weight_ambiguous_comma',[['24,640 KG','24,640,0 KG']],status='NEEDS_REVIEW')
case('weight_unit_unsupported',[['24,640 KG','24640 stones']],status='NEEDS_REVIEW')
case('weight_negative',[['24,640 KG','-24640 KG']],status='NEEDS_REVIEW')
case('multiple_total_candidates',append='Total Gross Weight: 24.640 MT\nTotal Gross Weight: 25 MT',status='NEEDS_REVIEW')
case('packing_list_with_correct_fields',[['DRAFT BILL OF LADING','PACKING LIST']],status='NEEDS_REVIEW')
case('two_si_documents',[['DRAFT BILL OF LADING','SHIPPING INSTRUCTION']],status='NEEDS_REVIEW')
case('certificate_with_correct_fields',[['DRAFT BILL OF LADING','CERTIFICATE OF ORIGIN']],status='NEEDS_REVIEW')
case('missing_second_source',missing=True,status='NEEDS_REVIEW')
case('broken_new_pdf',format='corrupt',status='NEEDS_REVIEW')
case('scan_new_identity',format='scan',status='NEEDS_REVIEW')
case('deadline_new_source',timeout=True,status='NEEDS_REVIEW')
case('quoted_invoice_noise',body='Please verify draft BL against SI.\nFrom: old@example.test\nPlease cancel invoice 172.')
case('misleading_si_subject',subject='REQUEST SI',body='Please compare the attached draft BL against the SI.')
case('explicit_compare_then_maintenance',body='Please verify draft BL against SI. Maintenance starts tomorrow.')
case('word_multifield_difference',[['Maple Fiber Co Ltd','Maple Board Co Ltd'],['24,640 KG','25 MT']],format='docx',status='MISMATCH',fields=['shipper','gross_weight_kg'])
if __name__=='__main__':
    out=suite.ROOT/'validation'/'holdout';out.mkdir(parents=True,exist_ok=True)
    freeze={'method':'Self-authored unseen semantic cases; frozen before first execution; no tuning on this suite.',
      'engine_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((suite.ROOT/'harbor').glob('*.py'))},
      'suite_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if not (out/'freeze.json').exists():(out/'freeze.json').write_text(json.dumps(freeze,indent=2))
    suite.main('holdout')
