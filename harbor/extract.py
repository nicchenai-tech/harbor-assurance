"""Evidence-preserving field extraction; label meaning, not literal equality."""
import re
from .domain import FIELDS, normalize

LABELS = [
 ('shipper', r'(?:shipper(?:/exporter)?(?:\s*\(principal or seller\))?)'),
 ('consignee', r'(?:consignee(?:\s*\(non-negotiable\))?|to the order of)'),
 ('notify_party', r'(?:notify(?: party)?(?:/intermediate consignee)?)'),
 ('port_of_loading', r'(?:port of loading(?:\s*\(pol\))?|load port|pol)'),
 ('port_of_discharge', r'(?:port of discharge(?:\s*\(pod\))?|discharge port|pod)'),
 ('container_count', r'(?:container count|total containers|no\.? of containers(?: or packages)?|containers)'),
 ('gross_weight_kg', r'(?:(?:total\s+)?gross\s*(?:weight|wt)(?:\s*(?:毛重|[■□�]+))?\s*(?:\((?:kg[s]?|毛重\s*kgs|mt[s]?)\))?)'),
]
OTHER = re.compile(r'^(?:vessel|voy|ocean vessel|export carrier|description|commodity|kinds of packages|hs code|h\.s\.|booking|b/l|bill of lading no|bl no|freight|oc no|net weight|container no\.|shipping instruction|bill of lading|={3,})',re.I)


def label_match(text):
    text = text.strip()
    text = re.sub(r'^portof\b','Port of',text,flags=re.I)
    text = re.sub(r'^(notify)\.\s+',r'\1: ',text,flags=re.I)
    for field,pattern in LABELS:
        m=re.match(r'^('+pattern+r')(?:\s*\([^)]*[\u4e00-\u9fff][^)]*\))?\s*(?::\s*(.*)|$)',text,re.I|re.S)
        if m: return field,m.group(1),m.group(2)
        m=re.match(r'^('+pattern+r')\s+([^:\n]+)$',text,re.I)
        if m: return field,m.group(1),m.group(2)
    return None


def extract_fields(document):
    candidates={f:[] for f in FIELDS}
    lines=document['lines']
    for i,line in enumerate(lines):
        match=label_match(line['text'])
        if not match: continue
        field,label,inline=match
        value=inline or ''
        evidence=[line['text']]
        # Preserve following lines until the next semantic label/metadata heading.
        if inline is None or field in ('shipper','consignee','notify_party'):
            for following in lines[i+1:]:
                t=following['text']
                if label_match(t) or OTHER.match(t) or (':' in t and field not in ('shipper','consignee','notify_party')): break
                # Container table column heading isn't a shipment total.
                if field in ('gross_weight_kg','container_count') and re.match(r'^[A-Z]{4}\d{7}',t): break
                value += ('\n' if value else '') + t
                evidence.append(t)
                if field not in ('shipper','consignee','notify_party'): break
        if not value.strip(): continue
        norm,rule,warning=normalize(field,value,label)
        candidates[field].append({'raw_value':value.strip(),'normalized_value':norm,'label':label,
            'source_file':document['file'],'source_hash':document['sha256'],
            'locator':line['locator'],'evidence':'\n'.join(evidence),
            'method':document['method'],'normalization':rule,'warning':warning,
            'requires_confirmation':document['scan'], 'confirmed':False})
    result={}
    for field,items in candidates.items():
        if field == 'gross_weight_kg':
            totals=[c for c in items if c['label'].lower().startswith('total')]
            if totals: items=totals
        if not items:
            result[field]={'raw_value':None,'normalized_value':None,'source_file':document['file'],
                           'source_hash':document['sha256'],'locator':{},'evidence':'',
                           'method':document['method'],'normalization':'No supported field located.',
                           'warning':'Required value could not be located.','requires_confirmation':False,'confirmed':False}
        else:
            selected=items[0].copy()
            if len({str(x['normalized_value']) for x in items})>1:
                selected['warning']='Conflicting values found for this field.'
                selected['normalized_value']=None
                selected['alternatives']=items
            result[field]=selected
    return result
