async function generateListing() {
  const productName = document.getElementById('productName').value.trim();
  const features    = document.getElementById('features').value.trim();

  if (!productName || !features) {
    showToast('Product Name and Key Features are required.', true);
    return;
  }

  const btn = setLoading('generateBtn', 'Generating...');
  showOutputLoading('outputContainer', 'Qwen2.5-7B is writing your listing...');

  const payload = {
    product_name: productName,
    features:     features,
    audience:     document.getElementById('audience').value.trim() || 'General consumers',
    keywords:     document.getElementById('keywords').value.trim(),
    tone:         document.getElementById('tone').value,
    season:       document.getElementById('season').value,
    word_count:   parseInt(document.getElementById('wordCount').value, 10) || 200,
  };

  const data = await apiFetch('/api/v1/generate-listing', payload);
  resetBtn(btn, '✦ Generate Listing');

  if (data.error) {
    showError('outputContainer', data.error);
    return;
  }

  renderOutput('outputContainer', data.output, 'GENERATED LISTING', data.flagged || []);

  // Append quality score bar
  if (data.score) {
    const s = data.score;
    const div = document.createElement('div');
    div.style.cssText = 'margin-top:12px;padding:14px 16px;background:#0d0d0d;border:1px solid #1a1a1a;border-radius:8px;';
    div.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <span style="font-size:11px;color:#555;letter-spacing:1px;">LISTING QUALITY SCORE</span>
        <span style="color:#e8ff47;font-weight:700;font-size:15px;">${s.overall}<span style="font-size:11px;color:#444;">/99</span></span>
      </div>
      <div class="score-bar-track">
        <div id="q-bar" class="score-bar-fill" style="width:0%;background:#e8ff47;"></div>
      </div>
      <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:11px;color:#444;">
        <span>CTR Probability: ${s.ctr_probability}</span>
        <span>Conversion Est: ${s.conversion_likelihood}</span>
      </div>`;
    document.getElementById('outputContainer').appendChild(div);
    setTimeout(() => {
      const bar = document.getElementById('q-bar');
      if (bar) bar.style.width = s.overall + '%';
    }, 80);
  }
}