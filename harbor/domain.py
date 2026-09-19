"""Strict public contract and conservative, source-independent comparisons."""
import re
import unicodedata
from decimal import Decimal, InvalidOperation

FIELDS = ('shipper', 'consignee', 'notify_party', 'port_of_loading',
          'port_of_discharge', 'container_count', 'gross_weight_kg')
CATEGORIES = ('BL_COMPARISON', 'SI_REQUEST', 'INVOICE_QUERY', 'GENERAL', 'SPAM')
REASONS = ('wrong_doc_type', 'missing_attachment', 'unreadable', 'missing_value')
STATUSES = ('OK', 'MISMATCH', 'NEEDS_REVIEW')


def compact(value):
    return ' '.join(unicodedata.normalize('NFKC', str(value)).split())


def normalize(field, value, label=''):
    """Return canonical value, human-readable rule, and blocking warning."""
    raw = compact(value)
    upper = raw.upper()
    if not raw or re.fullmatch(r'(?:N/?A|TBA|TBD|NONE|NULL|UNKNOWN|NOT AVAILABLE|[-?_. ]+(?:MT[S]?)?)', upper):
        return None, 'Missing values are never replaced by zero.', 'Required value is missing.'
    if field == 'container_count':
        # Keep the quantity; a size such as 20 or 40 is not a container count.
        quantity_pattern = r'(\d+)\s*[x×]\s*(?:20|40|45)\s*[\x27’′]?\s*(?:GP|HC|HQ|DC|RF|FCL)?\b'
        parts = re.findall(quantity_pattern, raw, re.I)
        if parts:
            remainder = re.sub(quantity_pattern, '', raw, flags=re.I)
            if re.sub(r'[\s+,;&]|\band\b', '', remainder, flags=re.I):
                return None, 'Every container quantity must be explicit.', 'Unparsed container information requires review.'
            count = sum(int(n) for n in parts)
        elif re.fullmatch(r'\d+(?:\s*(?:containers?|units?|boxes))?', raw, re.I):
            count = int(re.match(r'\d+', raw)[0])
        else:
            return None, 'Explicit container quantity required.', 'Ambiguous container quantity.'
        if count <= 0:
            return None, 'Container count must be positive.', 'Invalid container count.'
        return count, 'Read quantity before container size; sum explicit quantities.', None
    if field == 'gross_weight_kg':
        match = re.fullmatch(r'([0-9][0-9, .]*)\s*(KG[S]?|KILOGRAM[S]?|MT[S]?|TONNE[S]?|TON[S]?|T|LB[S]?)?', upper)
        if not match:
            return None, 'A numeric weight with a supported unit is required.', 'Ambiguous weight.'
        number, unit = match.groups()
        number = number.strip().replace(' ', '')
        if ',' in number and not re.fullmatch(r'\d{1,3}(?:,\d{3})+(?:\.\d+)?', number):
            return None, 'Ambiguous decimal separators require review.', 'Ambiguous decimal separator.'
        if unit in ('TON','TONS'):
            return None, 'Unqualified ton may mean metric, short or long ton.', 'Weight unit is ambiguous; specify metric tonnes or kg.'
        implicit = unit is None
        label_unit = re.search(r'\b(KGS?|MTS?|LBS?)\b', label.upper())
        unit = unit or (label_unit[1] if label_unit else 'KG' if re.search(r'毛重|GROSS', label.upper()) else None)
        if not unit:
            return None, 'No implicit weight unit.', 'Weight unit is missing.'
        try:
            result = Decimal(number.replace(',', ''))
        except InvalidOperation:
            return None, 'Parse exact decimal weight.', 'Invalid weight.'
        factor = Decimal('1000') if unit in ('MT','MTS','TONNE','TONNES','TON','TONS','T') else Decimal('0.45359237') if unit in ('LB','LBS') else Decimal(1)
        if result < 0:
            return None, 'Weight must be nonnegative.', 'Invalid weight.'
        basis = ' Unit read from field label.' if implicit and label_unit else ' Bare gross weight uses the participant schema kg convention; deployment must confirm this convention.' if implicit else ''
        return format(result * factor, 'f'), f'Exact decimal conversion from {unit} to kg; no tolerance.'+basis, None
    # Do not collapse entity identity, addresses, port codes or fuzzy matches.
    clean = re.sub(r'[^\w]', '', upper, flags=re.UNICODE)
    return clean, 'Normalize Unicode, case, spacing and punctuation; preserve all words and digits.', None


def equal(field, a, b):
    if a is None or b is None:
        return False
    if field == 'gross_weight_kg':
        return Decimal(str(a)) == Decimal(str(b))
    return a == b


def prediction(category, status='OK', fields=None, reason=None):
    return {'category': category, 'status': status, 'review_reason': reason,
            'has_defect': status == 'MISMATCH',
            'defect_fields': [f for f in FIELDS if f in (fields or [])] if status == 'MISMATCH' else []}


def validate_submission(submission, expected_ids):
    if set(submission) != set(expected_ids):
        raise ValueError('Submission IDs do not exactly match the inbox.')
    keys = {'category','status','review_reason','has_defect','defect_fields'}
    for eid, row in submission.items():
        if set(row) != keys or row['category'] not in CATEGORIES or row['status'] not in STATUSES:
            raise ValueError(f'{eid}: invalid schema or enumeration')
        if type(row['has_defect']) is not bool or not isinstance(row['defect_fields'], list):
            raise ValueError(f'{eid}: invalid types')
        fs = row['defect_fields']
        if len(set(fs)) != len(fs) or any(f not in FIELDS for f in fs):
            raise ValueError(f'{eid}: invalid defect fields')
        if row['has_defect'] != (row['status'] == 'MISMATCH') or bool(fs) != row['has_defect']:
            raise ValueError(f'{eid}: inconsistent defect state')
        if (row['status'] == 'NEEDS_REVIEW' and row['review_reason'] not in REASONS) or (row['status'] != 'NEEDS_REVIEW' and row['review_reason'] is not None):
            raise ValueError(f'{eid}: invalid review reason')
        if row['category'] != 'BL_COMPARISON' and row['status'] != 'OK':
            raise ValueError(f'{eid}: non-comparison email cannot have a comparison outcome')
    return True
