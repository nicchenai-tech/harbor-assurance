const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

const labels = {
  shipper: 'Shipper',
  consignee: 'Consignee',
  notify_party: 'Notify Party',
  port_of_loading: 'Port of Loading',
  port_of_discharge: 'Port of Discharge',
  container_count: 'Container Count',
  gross_weight_kg: 'Gross Weight'
};

const states = {
  verified_ok: 'Verified',
  mismatch: 'Issue Found',
  needs_review: 'Needs Review',
  awaiting_documents: 'Waiting',
  classified: 'Classified',
  processing_failed: 'Needs Review',
  MATCH: '✓ Match',
  MISMATCH: '× Mismatch',
  REVIEW: '! Needs Review'
};

const scenarioReasons = {
  'demo-01': 'Container quantity mismatch',
  'demo-02': 'Equivalent KG and MT values',
  'demo-03': 'Uncertain document label',
  'demo-04': 'Shipping instruction request',
  'demo-05': 'Invoice query routed',
  'demo-06': 'Required documents missing',
  'demo-07': 'Scanned PDF with Cloud OCR'
};

let rows = [];
let selected = null;
let current = null;
let health = {uploads_enabled: true};
let toastTimer;
let lastReview = null;

async function api(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let message = await response.text();
    try { message = JSON.parse(message).detail || message; } catch {}
    throw Error(typeof message === 'string' ? message : JSON.stringify(message));
  }
  return response.json();
}

function toast(text) {
  $('#toast').textContent = text;
  $('#toast').style.display = 'block';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => $('#toast').style.display = 'none', 4500);
}

function badge(state) {
  return `<span class="badge ${esc(state)}">${esc(states[state] || state)}</span>`;
}

function locator(location) {
  return Object.entries(location || {})
    .filter(([key]) => key !== 'bbox')
    .map(([key, value]) => `${key} ${value}`)
    .join(' · ');
}

function setActiveNav(filter) {
  $$('.nav[data-filter]').forEach(nav => nav.classList.toggle('active', nav.dataset.filter === filter));
  if (!filter) $$('.nav').forEach(nav => nav.classList.remove('active'));
}

function scrollToWorkspace() {
  $('#verification-workspace').scrollIntoView({behavior: 'smooth', block: 'start'});
}

async function refresh() {
  try {
    const [data, status] = await Promise.all([api('/api/cases'), api('/api/health')]);
    health = status;
    rows = data.cases;
    const publicMode = status.mode.includes('public');
    $('#runtime-mode').textContent = status.mode;
    $('#runtime-note').textContent = publicMode
      ? 'Shared synthetic data only. Uploads and private documents are blocked.'
      : 'Private source documents remain inside this workspace.';
    const ocrBackend = status.ocr_backend || 'unavailable';
    $('#ocr-status').textContent = ocrBackend === 'unavailable'
      ? 'OCR unavailable · human review remains active'
      : `${ocrBackend.replaceAll('_', ' ')} Cloud OCR · human confirmation required`;
    $('#reset-demo').hidden = !publicMode;
    $('#total').textContent = rows.length;
    $('#review-count').textContent = (data.counts.needs_review || 0) + (data.counts.processing_failed || 0);
    $('#m-total').textContent = rows.length;
    $('#m-ok').textContent = data.counts.verified_ok || 0;
    $('#m-mismatch').textContent = data.counts.mismatch || 0;
    $('#m-review').textContent = (data.counts.needs_review || 0) + (data.counts.processing_failed || 0);
    $('#m-wait').textContent = data.counts.awaiting_documents || 0;
    renderRecentCases();
    renderList();
    if (!selected) {
      const initial = rows.find(row => row.id === 'demo-01') || rows.find(row => row.state === 'mismatch') || rows[0];
      if (initial) await loadCase(initial.id, false);
    }
  } catch (error) {
    $('#detail').innerHTML = `<div class="empty">Unable to load cases.<br>${esc(error.message)}<br>Check that the service is running, then refresh.</div>`;
  }
}

function filteredRows() {
  const query = $('#search').value.toLowerCase();
  const filter = $('#filter').value;
  return rows.filter(row =>
    (filter === 'all' || row.state === filter || (filter === 'needs_review' && row.state === 'processing_failed')) &&
    `${row.id} ${row.subject} ${row.sender}`.toLowerCase().includes(query)
  );
}

function renderRecentCases() {
  const priority = ['demo-01', 'demo-02', 'demo-03', 'demo-07', 'demo-06'];
  const rank = id => priority.includes(id) ? priority.indexOf(id) : priority.length;
  const recent = [...rows].sort((a, b) => rank(a.id) - rank(b.id)).slice(0, 5);
  $('#recent-cases').innerHTML = recent.map(row => `
    <div class="recent-row" role="row">
      <div class="recent-case"><strong>${esc(row.id.toUpperCase())}</strong><small>${esc(row.subject)}</small></div>
      <div>${badge(row.state)}</div>
      <span>${esc(scenarioReasons[row.id] || row.category.replaceAll('_', ' ').toLowerCase())}</span>
      <span>v${esc(row.version)}</span>
      <button class="recent-open" data-open-case="${esc(row.id)}">Open →</button>
    </div>`).join('');
  $$('[data-open-case]').forEach(button => button.onclick = () => loadCase(button.dataset.openCase, true));
}

function renderList() {
  const filtered = filteredRows();
  $('#result-count').textContent = `${filtered.length} cases`;
  $('#case-list').innerHTML = filtered.length ? filtered.map(row => `
    <button class="case-item ${row.id === selected ? 'selected' : ''}" data-case="${esc(row.id)}" aria-label="${esc(row.id)} ${esc(states[row.state])}">
      <div class="case-meta"><span>${esc(row.id.toUpperCase())}</span>${badge(row.state)}</div>
      <h3>${esc(row.subject)}</h3>
      <div class="sender">${esc(scenarioReasons[row.id] || row.sender)}</div>
    </button>`).join('') : '<div class="empty">No cases match this filter.</div>';
  $$('[data-case]').forEach(button => button.onclick = () => loadCase(button.dataset.case, false));
}

async function loadCase(id, shouldScroll = true) {
  selected = id;
  renderList();
  $('#detail').classList.add('loading');
  try {
    const loaded = await api('/api/cases/' + encodeURIComponent(id));
    if (selected !== id) return;
    current = loaded;
    renderCase();
    if (shouldScroll) scrollToWorkspace();
  } catch (error) {
    toast(error.message);
  } finally {
    if (selected === id) $('#detail').classList.remove('loading');
  }
}

function normalizedNote(observation) {
  if (!observation || observation.normalized_value == null) return '';
  const suffix = observation.label?.toLowerCase().includes('weight') ? ' kg' : '';
  return `<span class="normalized-note">Normalized: ${esc(observation.normalized_value)}${suffix}</span>`;
}

function valueCell(observation, role, field, comparisonState) {
  if (!observation) return '<span class="empty-value">Document unavailable</span>';
  const method = observation.method === 'human_review' ? 'Human-confirmed' : observation.method?.endsWith('_ocr') ? 'OCR suggestion' : '';
  const showNormalized = comparisonState === 'MATCH' && observation.raw_value != null;
  return `<div class="value ${observation.raw_value == null ? 'empty-value' : ''}">${esc(observation.raw_value ?? 'Value not found')}</div>
    ${showNormalized ? normalizedNote(observation) : ''}
    <button class="source-link" data-evidence="${role}:${field}">${method ? esc(method) + ' · ' : ''}View Evidence ↗</button>`;
}

function caseSummary(caseData) {
  const matches = caseData.comparisons.filter(item => item.state === 'MATCH').length;
  const mismatches = caseData.comparisons.filter(item => item.state === 'MISMATCH').length;
  const reviews = caseData.comparisons.filter(item => item.state === 'REVIEW').length;
  const normalized = caseData.comparisons.filter(item => item.state === 'MATCH' && item.SI && item.BL && String(item.SI.raw_value) !== String(item.BL.raw_value) && String(item.SI.normalized_value) === String(item.BL.normalized_value)).length;
  const pieces = [];
  if (mismatches) pieces.push(`${mismatches} confirmed discrepanc${mismatches === 1 ? 'y' : 'ies'}`);
  if (matches) pieces.push(`${matches} matched field${matches === 1 ? '' : 's'}`);
  if (reviews) pieces.push(`${reviews} unresolved field${reviews === 1 ? '' : 's'}`);
  if (normalized) pieces.push(`${normalized} value${normalized === 1 ? '' : 's'} normalized`);
  return pieces;
}

function decisionTitle(caseData) {
  const count = caseData.known_defects.length;
  if (caseData.workflow_state === 'mismatch') return `${count} confirmed discrepanc${count === 1 ? 'y' : 'ies'}`;
  if (caseData.workflow_state === 'processing_failed') return 'Source document needs attention';
  if (caseData.workflow_state === 'needs_review') {
    const unresolved = caseData.unresolved_fields.length || 1;
    return `${unresolved} unresolved field${unresolved === 1 ? '' : 's'} require${unresolved === 1 ? 's' : ''} human review`;
  }
  if (caseData.workflow_state === 'awaiting_documents') return 'Waiting for source documents';
  if (caseData.workflow_state === 'verified_ok') return 'No discrepancy detected';
  return `Routed to ${caseData.classification.category.replaceAll('_', ' ').toLowerCase()}`;
}

function auditTimeline(caseData) {
  if (!caseData.review_events.length) return '<p class="muted">No human changes. The original automatic result is preserved separately.</p>';
  const events = caseData.review_events.map(event => `
    <div class="audit-event">
      <strong>Human Review · ${event.field ? `${esc(event.role)} ${esc(labels[event.field])}` : esc(event.action.replaceAll('_', ' '))}</strong>
      <small>${esc(event.reviewer)} · ${new Date(event.timestamp).toLocaleString()}</small>
      <p>${esc(event.reason)}</p>
      ${event.before ? `<p>${esc(event.before.raw_value ?? 'Unresolved')} → <strong>${esc(event.after.raw_value)}</strong></p>` : ''}
      ${event.after?.reviewer_source_location ? `<small>Evidence: ${esc(event.after.reviewer_source_location)}</small>` : ''}
    </div>`).join('');
  return `<div class="audit-timeline">
    <div class="audit-event"><strong>Version 1 · Automatic extraction</strong><small>Original result preserved</small></div>
    ${events}
    <div class="audit-event"><strong>Version ${caseData.report_version} · Recomputed report</strong><small>Human correction applied to deterministic verification</small></div>
  </div>`;
}

function renderCase() {
  const caseData = current;
  const isComparison = caseData.classification.category === 'BL_COMPARISON';
  const needsResolution = ['mismatch', 'needs_review', 'processing_failed'].includes(caseData.workflow_state);
  const summary = caseSummary(caseData);
  const success = lastReview?.emailId === caseData.email_id ? `
    <div class="review-success"><div><strong>✓ Review saved</strong><span>Report updated: v${lastReview.before} → v${lastReview.after}. Original automatic result preserved for audit.</span></div><button class="text-button" id="view-audit">View Audit History ↓</button></div>` : '';
  $('#detail').innerHTML = `
    <div class="detail-top"><span class="case-id">${esc(caseData.email_id.toUpperCase())} / ${esc(caseData.classification.category)}</span><span class="version">Report v${caseData.report_version}</span></div>
    <h2 class="subject">${esc(caseData.email.subject)}</h2>
    <div class="email-meta">From ${esc(caseData.email.from)} · ${caseData.email.attachments.length} attachment${caseData.email.attachments.length === 1 ? '' : 's'}</div>
    <div class="decision ${esc(caseData.workflow_state)}"><strong>${esc(decisionTitle(caseData))}</strong><p>${esc(caseData.decision_reason || caseData.classification.reason)}</p>${caseData.export_note ? '<p>Not verified. This request remains open until the required documents arrive.</p>' : ''}<div class="decision-summary">${summary.map(item => `<span>${esc(item)}</span>`).join('')}</div></div>
    ${success}
    <div class="action-row">${isComparison ? `${needsResolution ? '<button class="button primary" id="open-review">Resolve Issue</button>' : ''}${health.uploads_enabled ? '<button class="button secondary" id="open-upload">Add / replace document</button>' : ''}<button class="button secondary" id="retry">↻ Run Verification Again</button>` : ''}<a class="button secondary" href="/api/cases/${encodeURIComponent(caseData.email_id)}/report">Export report ↗</a></div>
    ${isComparison ? `<div class="section-title"><h3>Seven-field verification</h3><span>Shipping Instruction is the reference</span></div><div class="field-table"><div class="field-row table-head"><div>FIELD</div><div>SHIPPING INSTRUCTION</div><div>DRAFT BILL OF LADING</div><div>DECISION</div></div>${caseData.comparisons.map(comparison => `<div class="field-row row-${comparison.state.toLowerCase()}"><div class="field-name">${labels[comparison.field]}</div><div>${valueCell(comparison.SI, 'SI', comparison.field, comparison.state)}</div><div>${valueCell(comparison.BL, 'BL', comparison.field, comparison.state)}</div><div>${badge(comparison.state)}<button class="review-link" data-review="${comparison.field}">${comparison.state === 'REVIEW' ? 'Resolve Issue' : 'Review field'} →</button></div></div>`).join('')}</div>` : ''}
    <div class="section-title"><h3>Source documents</h3><span>Original evidence retained</span></div>
    ${caseData.documents.length ? caseData.documents.map((document, index) => `<div class="doc-row"><span class="doc-icon">${esc(document.format.toUpperCase())}</span><div class="doc-name">${esc(document.file.split('/').pop())}<small>${esc(document.role === 'UNKNOWN' ? 'Role unconfirmed' : document.role)} · ${esc(document.method.replaceAll('_', ' '))}${document.errors.length ? ' · Reading issue' : ''}</small></div><button class="text-button" data-document="${index}">View Evidence ↗</button></div>`).join('') : '<p class="muted">No documents processed for this email.</p>'}
    <details class="disclosure"><summary>Email & routing evidence</summary><p>${esc(caseData.classification.reason)}</p><blockquote>${esc(caseData.classification.evidence)}</blockquote><pre>${esc(caseData.email.body)}</pre></details>
    <details class="disclosure" id="audit-history" ${caseData.review_events.length ? 'open' : ''}><summary>Audit History · ${caseData.review_events.length} human event${caseData.review_events.length === 1 ? '' : 's'}</summary>${auditTimeline(caseData)}</details>`;

  $$('[data-evidence]').forEach(button => button.onclick = () => {
    const [role, field] = button.dataset.evidence.split(':');
    showEvidence(role, field);
  });
  $$('[data-review]').forEach(button => button.onclick = () => openReview(button.dataset.review));
  $$('[data-document]').forEach(button => button.onclick = () => showDocument(Number(button.dataset.document)));
  if ($('#view-audit')) $('#view-audit').onclick = () => $('#audit-history').scrollIntoView({behavior: 'smooth', block: 'start'});
  if (isComparison) {
    if ($('#open-review')) $('#open-review').onclick = () => openReview(caseData.unresolved_fields[0] || caseData.known_defects[0] || 'shipper');
    if ($('#open-upload')) $('#open-upload').onclick = openUpload;
    $('#retry').onclick = retry;
  }
}

function showEvidence(role, field) {
  const observation = current.fields[role]?.[field];
  if (!observation) return toast('No source observation is available for this field.');
  const index = current.documents.findIndex(document => document.file === observation.source_file);
  const original = observation.original_observation || observation;
  $('#evidence-title').textContent = `${role} · ${labels[field]}`;
  $('#evidence-content').innerHTML = `
    <p class="muted"><strong>${esc(role === 'SI' ? 'Shipping Instruction' : 'Draft Bill of Lading')}</strong> · ${esc(observation.source_file)} · ${esc(locator(observation.locator) || 'source location unavailable')}</p>
    <div class="evidence-quote">${esc(original.evidence || 'No value was extracted at this location. Inspect the full document.')}</div>
    <div class="evidence-rule"><strong>Normalization rule</strong><br>${esc(observation.normalization)}<br><small>Normalized value: ${esc(observation.normalized_value ?? 'Unresolved')}${field === 'gross_weight_kg' && observation.normalized_value != null ? ' kg' : ''}</small></div>
    ${observation.method === 'human_review' ? `<p class="muted">Human correction: ${esc(observation.raw_value)}. ${esc(observation.review_reason)} Source checked: ${esc(observation.reviewer_source_location || locator(observation.locator))}</p>` : ''}
    ${previewHTML(index, observation.locator)}${linesHTML(index, observation.locator)}`;
  $('#evidence-dialog').showModal();
}

function previewHTML(index, location = {}) {
  const document = current.documents[index];
  if (!document || document.format !== 'pdf') return '';
  const box = location.bbox;
  return `<div class="page-preview"><img src="/api/cases/${encodeURIComponent(current.email_id)}/preview/${index}/${location.page || 1}" alt="Original PDF page" onerror="this.replaceWith(document.createTextNode('This PDF cannot be rendered. Replace the damaged file.'))">${box ? `<div class="highlight" style="left:${box[0] * 100}%;top:${box[1] * 100}%;width:${box[2] * 100}%;height:${box[3] * 100}%"></div>` : ''}</div>`;
}

function linesHTML(index, location = {}) {
  const document = current.documents[index];
  if (!document) return '';
  return `<div class="source-lines">${document.lines.map(line => `<div class="source-line ${JSON.stringify(line.locator) === JSON.stringify(location) ? 'focus' : ''}"><span class="muted">${esc(locator(line.locator))}</span> ${esc(line.text)}</div>`).join('')}</div><p class="muted">Source SHA-256: ${esc(document.sha256 || 'Unavailable')}</p>`;
}

function showDocument(index) {
  const document = current.documents[index];
  $('#evidence-title').textContent = document.file.split('/').pop();
  $('#evidence-content').innerHTML = `<p>${esc(document.role)} · ${esc(document.method.replaceAll('_', ' '))}</p>${document.errors.map(error => `<p class="form-error">${esc(error)}</p>`).join('')}<a class="button secondary" href="/api/cases/${encodeURIComponent(current.email_id)}/document/${index}" target="_blank" rel="noopener">Open original file ↗</a>${previewHTML(index)}${linesHTML(index)}`;
  $('#evidence-dialog').showModal();
}

function openReview(field) {
  $('#review-field').innerHTML = Object.entries(labels).map(([key, value]) => `<option value="${key}">${value}</option>`).join('');
  $('#review-field').value = field;
  const available = Object.keys(current.fields);
  if (!available.length) return toast('Add or replace a readable SI/BL before reviewing fields.');
  $('#review-role').innerHTML = available.map(role => `<option>${role}</option>`).join('');
  $('#review-role').value = available.find(role => {
    const observation = current.fields[role][field];
    return observation.warning || (observation.requires_confirmation && !observation.confirmed);
  }) || (available.includes('BL') ? 'BL' : available[0]);
  $('#review-error').textContent = '';
  $('#review-form [name=reason]').value = '';
  updateReviewValue();
  $('#review-dialog').showModal();
}

function reviewEvidenceCandidate(role, field, observation) {
  const tokens = {
    shipper: ['shipper'], consignee: ['consignee'], notify_party: ['notify'],
    port_of_loading: ['port of loading', 'loading port'],
    port_of_discharge: ['port of discharge', 'discharge port'],
    container_count: ['container'], gross_weight_kg: ['gross weight', 'weight']
  }[field] || [];
  const index = current.documents.findIndex(document => document.role === role && document.lines.some(line => tokens.some(token => line.text.toLowerCase().includes(token))));
  if (index < 0) return null;
  const document = current.documents[index];
  const line = document.lines.find(item => tokens.some(token => item.text.toLowerCase().includes(token)));
  return {index, file: document.file, locator: line.locator, evidence: line.text, observation};
}

function updateReviewValue() {
  const role = $('#review-role').value;
  const field = $('#review-field').value;
  const observation = current.fields[role]?.[field];
  const candidate = (!observation?.evidence || !Object.keys(observation?.locator || {}).length) ? reviewEvidenceCandidate(role, field, observation) : null;
  const sourceLocator = candidate?.locator || observation?.locator || {};
  const sourceEvidence = candidate?.evidence || observation?.evidence || 'Missing source value. Enter a value only after checking the document.';
  const sourceFile = candidate?.file || observation?.source_file || '';
  $('#review-value').value = observation?.raw_value || '';
  $('#source-location').value = observation?.reviewer_source_location || locator(sourceLocator);
  $('#source-location').required = !Object.keys(sourceLocator).length;
  $('#review-why').textContent = observation?.warning === 'Required value could not be located.'
    ? `The detected label for ${labels[field]} could not be mapped confidently enough for automatic verification.`
    : observation?.warning || `Harbor could not confidently resolve ${labels[field]} from the source document. Confirm the value before verification continues.`;
  $('#review-source').innerHTML = `<strong>${esc(role)} · ${esc(locator(sourceLocator) || 'location unresolved')}</strong>\n${esc(sourceEvidence)}\n<small>${esc(sourceFile)}</small>\n<button type="button" class="text-button" id="review-evidence">View Evidence ↗</button>`;
  if ($('#review-evidence')) $('#review-evidence').onclick = () => candidate ? showDocument(candidate.index) : showEvidence(role, field);
}

$('#review-role').onchange = updateReviewValue;
$('#review-field').onchange = updateReviewValue;
$('#cancel-review').onclick = () => $('#review-dialog').close();

$('#review-form').onsubmit = async event => {
  event.preventDefault();
  const button = event.target.querySelector('[type=submit]');
  const before = current.report_version;
  button.disabled = true;
  try {
    const body = Object.fromEntries(new FormData(event.target));
    body.expected_version = before;
    current = await api(`/api/cases/${encodeURIComponent(selected)}/review`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
    lastReview = {emailId: selected, before, after: current.report_version};
    $('#review-dialog').close();
    renderCase();
    await refresh();
    toast(`Review saved. Report updated from v${before} to v${current.report_version}.`);
  } catch (error) {
    $('#review-error').textContent = error.message;
  } finally {
    button.disabled = false;
  }
};

function openUpload() {
  $('#replace-file').innerHTML = '<option value="">Add a missing document</option>' + current.email.attachments.map(file => `<option value="${esc(file)}">${esc(file.split('/').pop())}</option>`).join('');
  $('#upload-error').textContent = '';
  $('#upload-dialog').showModal();
}

$('#upload-form').onsubmit = async event => {
  event.preventDefault();
  const button = event.target.querySelector('[type=submit]');
  button.disabled = true;
  try {
    const form = new FormData(event.target);
    form.append('expected_version', current.report_version);
    current = await api(`/api/cases/${encodeURIComponent(selected)}/upload`, {method: 'POST', body: form});
    $('#upload-dialog').close();
    renderCase();
    await refresh();
    toast('Document saved and verification rerun.');
  } catch (error) {
    $('#upload-error').textContent = error.message;
  } finally {
    button.disabled = false;
  }
};

async function retry() {
  const button = $('#retry');
  button.disabled = true;
  button.textContent = 'Running verification…';
  try {
    current = await api(`/api/cases/${encodeURIComponent(selected)}/retry`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({expected_version: current.report_version, reviewer: $('#reviewer-name').value, reason: 'Rechecked source documents; preserve confirmed corrections.'})});
    renderCase();
    await refresh();
    toast('Verification complete. Human corrections were retained where sources were unchanged.');
  } catch (error) {
    toast(error.message);
    button.disabled = false;
    button.textContent = '↻ Run Verification Again';
  }
}

$('#search').oninput = renderList;
$('#filter').onchange = renderList;
$('#refresh').onclick = async () => { await refresh(); if (selected) await loadCase(selected, false); };

$$('[data-filter]').forEach(button => button.onclick = () => {
  $('#filter').value = button.dataset.filter;
  setActiveNav(button.dataset.filter);
  renderList();
  if (button.dataset.filter !== 'all') scrollToWorkspace();
});

$$('[data-scenario]').forEach(button => button.onclick = () => {
  setActiveNav(null);
  loadCase(button.dataset.scenario, true);
});

$('#audit-nav').onclick = async () => {
  setActiveNav(null);
  const candidate = rows.find(row => row.version > 1) || rows.find(row => row.id === 'demo-03') || rows[0];
  if (!candidate) return;
  await loadCase(candidate.id, true);
  const history = $('#audit-history');
  if (history) { history.open = true; setTimeout(() => history.scrollIntoView({behavior: 'smooth', block: 'start'}), 450); }
};

for (const name of ['evidence', 'review', 'upload']) $('#close-' + name).onclick = () => $('#' + name + '-dialog').close();

$('#reset-demo').onclick = async () => {
  if (!confirm('Reset the shared synthetic sandbox to its original reports?')) return;
  await api('/api/demo/reset', {method: 'POST'});
  selected = null;
  current = null;
  lastReview = null;
  await refresh();
  toast('Synthetic demo restored.');
};

refresh();
