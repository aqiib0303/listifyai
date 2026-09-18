async function generateAB() {
  const product  = document.getElementById('ab-product').value.trim();
  const features = document.getElementById('ab-features').value.trim();
  const audience = document.getElementById('ab-audience').value.trim();

  if (!product) { showToast('Enter a product name first', true); return; }

  const btn = setLoading('ab-btn', 'Generating A/B variants...');
  document.getElementById('ab-versions').style.display = 'none';
  document.getElementById('ab-scores').style.display   = 'none';

  const data = await apiFetch('/api/v1/ab-test', { product, features, audience });
  resetBtn(btn, '⟳ Generate A/B Variants');

  if (data.error) { showToast(data.error, true); return; }

  document.getElementById('version-a').innerHTML = escH(data.version_a || '');
  document.getElementById('version-b').innerHTML = escH(data.version_b || '');
  document.getElementById('ab-versions').style.display = 'block';

  const sa = (data.score_a && data.score_a.overall) || 0;
  const sb = (data.score_b && data.score_b.overall) || 0;

  document.getElementById('score-a').textContent = sa + '/99';
  document.getElementById('score-b').textContent = sb + '/99';
  document.getElementById('ab-winner').innerHTML =
    `<span style="color:#e8ff47;">◉ Recommended: Version ${sb >= sa ? 'B — Lifestyle' : 'A — Feature'}</span>`;

  document.getElementById('ab-scores').style.display = 'block';
  setTimeout(() => {
    const ba = document.getElementById('bar-a');
    const bb = document.getElementById('bar-b');
    if (ba) ba.style.width = sa + '%';
    if (bb) bb.style.width = sb + '%';
  }, 80);
}