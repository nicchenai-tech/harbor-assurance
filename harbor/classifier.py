"""Transparent baseline intent routing. No IDs, filenames or reference labels."""
import re


def current_message(body):
    text = re.sub(r'^WARNING:.*?(?:\n\s*\n|$)', '', body, flags=re.I|re.S)
    text = re.split(r'\n(?:_{5,}|-{5,}|From:|On .+ wrote:)', text, maxsplit=1, flags=re.I)[0]
    text = re.split(r'\n(?:Best Regards|Kind Regards|Regards,|Best,)', text, maxsplit=1, flags=re.I)[0]
    return text.strip()


def classify(email):
    body = current_message(email.get('body',''))
    subject = email.get('subject','')
    text = body.lower()
    rules = [
        ('SPAM', r'mailbox.{0,50}(?:limit|full)|verify your account|you.{0,15}won|lottery|claim.{0,30}prize|parcel.{0,60}(?:fee|pay)|package.{0,60}unpaid|crypto|investment.{0,30}return|click.{0,30}(?:claim|prize)|weird trick|limited time offer|bank officer.{0,100}million', 'Suspicious prize, account, promotional or payment solicitation.'),
        ('GENERAL', r'berthing report|update summary|outstanding bl|daily.{0,20}report|public holiday|holiday notice|maintenance|sla|reminder:.{0,40}submit si|billing process.{0,100}(?:completed|processed)|team.{0,20}meeting|happy and prosperous new year|no action required', 'Operational update or general notice, not a document comparison.'),
        ('SI_REQUEST', r'please find shipping instruction|(?:prepare|provide|send|need|request|submit).{0,25}(?:shipping instruction|\bsi\b)(?!.{0,10}(?:and|against))', 'Request or provision of shipping instructions.'),
        ('INVOICE_QUERY', r'query on invoice|invoice.{0,40}(?:cancel|incorrect|amend|missing|payment)|(?:cancel|amend|missing).{0,30}invoice|detention charges|d&d|local charge|freight.{0,30}(?:breakdown|amount)|release payment|billing.{0,30}gr', 'Invoice, billing or charge-related action.'),
        ('BL_COMPARISON', r'(?:compare|check|verify|confirm|amend).{0,100}(?:draft|\bbl\b|bill of lading|\bsi\b)|(?:draft bl|draft bill of lading).{0,100}(?:check|confirm|verify|amend)|attached.{0,80}(?:\bsi\b|shipping instruction).{0,50}(?:draft|\bbl\b)|send.{0,30}draft bl', 'Request to obtain or verify draft BL against SI.'),
    ]
    # An explicit comparison request in the opening sentence outranks unrelated
    # operational notices later in the message, but never a spam signal.
    opening = re.split(r'[.!?\n]', text, maxsplit=1)[0]
    if re.search(rules[-1][1], opening, re.I):
        rules = [rules[0], rules[-1], *rules[1:-1]]
    for category, pattern, reason in rules:
        m = re.search(pattern, text, re.I|re.S)
        if m:
            return {'category': category, 'reason': reason, 'evidence': body[max(0,m.start()-30):min(len(body),m.end()+70)], 'method': 'intent_rule', 'needs_review': False}
    # Subject is secondary, after checking the current message.
    for category, pattern in [('SPAM',r'prize|lottery|mailbox|free money|weird trick'),('INVOICE_QUERY',r'invoice|local charges|total freight|d\s*&\s*d charges|billing'),('SI_REQUEST',r'\bsi\s*(?:-|needed)|cust si|request si')]:
        if re.search(pattern,subject,re.I):
            return {'category':category,'reason':'Subject provides the intent signal; current body has no stronger matched action.','evidence':subject,'method':'subject_rule','needs_review':False}
    return {'category':'GENERAL','reason':'No supported specific action detected; review routing if needed.','evidence':body[:240],'method':'fallback','needs_review':True}


def awaiting_documents(email):
    text = current_message(email.get('body','')).lower()
    return bool(re.search(r'(?:send|provide|revert with).{0,30}draft bl', text)) and not re.search(r'missing|dropped|lost|attached|compare', text)
