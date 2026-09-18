/* ============================================================
   ListifyAI — Shared JavaScript Utilities
   ============================================================ */

// ---- Toast ----
function showToast(msg, isError = false) {
  const t = document.getElementById('toast');
  t.textContent = (isError ? '✕ ' : '✓ ') + msg;
  t.className = 'toast' + (isError ? ' error' : '') + ' show';
  setTimeout(() => t.classList.remove('show'), 3000);
}

// ---- Set loading state on a button ----
function setLoading(btnId, label) {
  const btn = document.getElementById(btnId);
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span>${label}`;
  return btn;
}

// ---- Reset button ----
function resetBtn(btn, label) {
  btn.disabled = false;
  btn.innerHTML = label;
}

// ---- Show loading state inside an output container ----
function showOutputLoading(containerId, message) {
  document.getElementById(containerId).innerHTML = `
    <div class="empty-state">
      <div class="spinner spinner-light" style="width:24px;height:24px;margin:0 0 12px;"></div>
      <div style="color:#555;">${message}</div>
      <div style="font-size:11px;color:#2a2a2a;margin-top:4px;">Powered by Qwen2.5-7B</div>
    </div>`;
}

// ---- Render output box with optional flags ----
function renderOutput(containerId, text, title = 'OUTPUT', flagged = []) {
  const flagHTML = flagged.length
    ? `<div class="flag-warning">⚠ Flagged keywords detected: ${flagged.join(', ')}</div>`
    : '';

  document.getElementById(containerId).innerHTML = `
    ${flagHTML}
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
      <span style="font-size:11px;color:#555;letter-spacing:1px;">${escHtml(title)}</span>
      <button onclick="copyText(this.dataset.text)" data-text="${escAttr(text)}"
        style="background:none;border:none;color:#e8ff47;font-family:'Space Mono',monospace;font-size:11px;cursor:pointer;letter-spacing:0.5px;">
        ⎘ COPY
      </button>
    </div>
    <div class="output-box">${escHtml(text)}</div>`;
}

// ---- Show error state ----
function showError(containerId, message) {
  document.getElementById(containerId).innerHTML = `
    <div style="background:#200a0a;border:1px solid #ff6b6b;border-radius:8px;padding:16px;color:#ff6b6b;font-size:13px;">
      ✕ ${escHtml(message)}
    </div>`;
}

// ---- Copy an element's text content ----
function copyEl(elId) {
  const el = document.getElementById(elId);
  const text = el ? (el.innerText || el.textContent) : '';
  navigator.clipboard.writeText(text).then(() => showToast('Copied!'));
}

// ---- Copy arbitrary text (used in data-text attr) ----
function copyText(text) {
  navigator.clipboard.writeText(text).then(() => showToast('Copied!'));
}

// ---- Preview file in an <img> ----
function previewFile(input, previewDivId, imgId) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = e => {
      document.getElementById(previewDivId).style.display = 'block';
      document.getElementById(imgId).src = e.target.result;
    };
    reader.readAsDataURL(input.files[0]);
  }
}

// ---- Generic JSON API fetch ----
async function apiFetch(url, payload) {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) return { error: data.error || `HTTP ${res.status}` };
    return data;
  } catch (err) {
    return { error: 'Network error: ' + err.message };
  }
}

// ---- Escape helpers ----
function escHtml(t) {
  return String(t)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>');
}
function escAttr(t) {
  return String(t).replace(/"/g, '&quot;').replace(/\n/g, '&#10;');
}