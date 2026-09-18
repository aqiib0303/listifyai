"""
LLM Client — Mistral via Ollama (local).

Calls the Ollama REST API at http://localhost:11434 (or OLLAMA_BASE_URL env var).
No model loading, no GPU management, no dependencies beyond the standard library.

Requirements:
  1. Install Ollama: https://ollama.com/download
  2. Pull the model once:  ollama pull mistral
  3. Ollama must be running before starting this app:  ollama serve

Optional env vars:
  OLLAMA_BASE_URL   — default: http://localhost:11434
  OLLAMA_MODEL      — default: mistral
  OLLAMA_TIMEOUT    — request timeout in seconds, default: 120
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

# ── Config (override via environment) ────────────────────────────────────────
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL:    str = os.getenv("OLLAMA_MODEL",    "mistral")
OLLAMA_TIMEOUT:  int = int(os.getenv("OLLAMA_TIMEOUT", "120"))


# ── Public API ────────────────────────────────────────────────────────────────

def get_pipeline():
    """
    Compatibility shim — previously returned a HuggingFace pipeline object.
    Now just checks Ollama is reachable and returns a truthy sentinel.
    Returns None if Ollama is unreachable (caller falls back to stub).
    """
    try:
        url = f"{OLLAMA_BASE_URL}/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                return True  # Ollama is up
    except Exception as exc:
        logger.warning(f"[ListifyAI] Ollama not reachable at {OLLAMA_BASE_URL}: {exc}")
    return None


def generate(system_prompt: str, user_prompt: str, max_new_tokens: int = 1024) -> str:
    """
    Send a chat request to Ollama and return the assistant's reply.
    Falls back to stub text if Ollama is unavailable or returns an error.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "num_predict": max_new_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
        },
    }

    url  = f"{OLLAMA_BASE_URL}/api/chat"
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["message"]["content"].strip()

    except urllib.error.URLError as exc:
        logger.error(f"[ListifyAI] Ollama request failed: {exc}")
        return _stub_response(system_prompt, user_prompt)

    except (KeyError, json.JSONDecodeError) as exc:
        logger.error(f"[ListifyAI] Unexpected Ollama response format: {exc}")
        return _stub_response(system_prompt, user_prompt)


# ── Stub responses (unchanged — used when Ollama is unreachable) ──────────────

def _extract(prompt: str, *keys: str) -> str:
    """Pull the first value matching any of the given keys from a prompt string."""
    for line in prompt.split("\n"):
        for key in keys:
            if key.lower() in line.lower() and ":" in line:
                val = line.split(":", 1)[1].strip()
                if val:
                    return val
    return ""


def _stub_response(system_prompt: str, user_prompt: str) -> str:
    sp = system_prompt.lower()

    if "---version a---" in sp or "version a" in sp or "a/b" in sp:
        return _stub_ab(user_prompt)
    if "keyword" in sp or "seo specialist" in sp:
        return _stub_seo(user_prompt)
    if "translat" in sp or "cultural adaptation" in sp:
        return _stub_translate(user_prompt)
    if "competitor" in sp or "competitive intelligence" in sp:
        return _stub_competitor(user_prompt)
    if "packaging" in sp or "label" in sp or "extracted" in sp:
        return _stub_ocr(user_prompt)
    if "performance" in sp or "metrics breakdown" in sp:
        return _stub_performance(user_prompt)
    if "shopify" in sp or "woocommerce" in sp or "export" in sp:
        return _stub_export(user_prompt)
    if "brand voice" in sp or "tone" in sp:
        return _stub_tone(user_prompt)
    if "variant" in sp and "bulk" in sp:
        return _stub_variants(user_prompt)
    return _stub_listing(user_prompt)


def _stub_listing(p: str) -> str:
    product  = _extract(p, "Product Name", "product") or "Your Product"
    audience = _extract(p, "Target Audience", "audience") or "modern consumers"
    keywords = _extract(p, "SEO Keywords", "keywords") or "quality, premium"
    kw1 = keywords.split(",")[0].strip().title()

    return f"""**SEO TITLE:**
{product} — Premium Quality | {kw1} | Trusted & Authentic

**BULLET BENEFITS:**
• Superior materials and precision engineering for lasting, everyday durability
• Designed specifically for {audience} who demand quality without compromise
• {kw1} technology ensures peak performance exactly when you need it most
• Slim, lightweight build that fits seamlessly into any bag, pocket, or lifestyle
• 30-day satisfaction guarantee — love it completely or get a full refund

**PRODUCT DESCRIPTION:**
Meet the {product}. Engineered for people who know the difference between good and exceptional.

Every detail has been thought through so you don't have to think twice. Whether you're buying for yourself or as a gift, the quality speaks the moment you unbox it. No filler. No compromises. Just exactly what it says on the label.

Add to cart today — fast dispatch, secure packaging, zero-risk purchase.

**PRODUCT TAGS:**
{product.lower()}, {keywords.split(",")[0].strip()}, premium, quality, authentic, trusted, bestseller, original, fast delivery, top rated

**MARKETPLACE KEYWORDS:**
Primary: {product.lower()}, buy {product.lower()} online, best {product.lower()}
Long-tail: {product.lower()} for {audience.split()[0].lower()}, top rated {product.lower()} 2025, {product.lower()} free delivery pakistan

---
[STUB MODE — make sure Ollama is running: ollama serve  |  model pulled: ollama pull {OLLAMA_MODEL}]"""


def _stub_ab(p: str) -> str:
    product = _extract(p, "Product", "product") or "Product"
    return f"""---VERSION A---
The {product} delivers measurable results. Built with precision-engineered components and high-grade materials, it performs to specification every single time. Key specs: industry-leading build quality, optimised form factor, independently tested durability. If technical excellence drives your buying decision, this passes every test.

---VERSION B---
Some products you buy. Others you live with. The {product} is the second kind. From the moment it arrives, it fits into your life like it was always supposed to be there — because it was designed around how you actually live, not just how products are usually built. Choose better. Choose once."""


def _stub_seo(p: str) -> str:
    product = _extract(p, "Product", "Niche", "product") or "product"
    base = product.lower().split()[0]
    return f"""**PRIMARY KEYWORDS** (High commercial intent):
• {base} online — Volume: High | Difficulty: Hard
• buy {base} — Volume: High | Difficulty: Hard
• best {base} 2025 — Volume: Med | Difficulty: Medium
• {base} price pakistan — Volume: Med | Difficulty: Medium
• {base} review — Volume: Med | Difficulty: Easy
• original {base} — Volume: Med | Difficulty: Easy

**LONG-TAIL KEYWORDS** (Specific buyer intent):
• {base} for sale with free delivery — Volume: Low | Difficulty: Easy
• top rated {base} 2025 — Volume: Low | Difficulty: Easy
• where to buy {base} near me — Volume: Low | Difficulty: Easy
• {base} under 2000 rupees — Volume: Low | Difficulty: Easy
• genuine {base} original brand — Volume: Low | Difficulty: Easy
• {base} daraz lowest price — Volume: Med | Difficulty: Medium
• how to choose the right {base} — Volume: Low | Difficulty: Easy
• {base} gift idea pakistan — Volume: Low | Difficulty: Easy

**TRENDING COMBINATIONS:**
• {base} gift 2025
• {base} best price pakistan
• premium {base} authentic
• {base} same day delivery
• {base} cashback offer

**PRO TIP:** Target 2–3 long-tail keywords in your title and opening bullet. Long-tails convert 3× better for new listings with limited reviews — less competition, higher buyer intent."""


def _stub_translate(p: str) -> str:
    return """**CULTURALLY ADAPTED TEXT:**
[Full translated text appears here when Ollama / Mistral is active]

**3 CULTURAL ADAPTATIONS MADE:**
1. Replaced Western urgency triggers ("limited time!") with trust-based social proof signals more effective in this market
2. Added family-value and quality-heritage language that resonates with local buyer psychology
3. Adjusted price-anchoring language to match local purchasing-power expectations and deal-framing norms

**LOCAL BUYER PSYCHOLOGY NOTE:**
Buyers in this market respond most strongly to trust signals, authenticity markers, and quality assurance language. Fast and secure delivery messaging converts strongly. Avoid aggressive hard-sell tactics — they reduce trust.

---
[STUB MODE — start Ollama and ensure mistral is pulled for full multilingual cultural adaptation]"""


def _stub_competitor(p: str) -> str:
    product = _extract(p, "My Product", "product") or "your product"
    return f"""**COMPETITIVE ANALYSIS:**
Listings in this niche heavily favour benefit-first headlines anchored by social proof. Top performers open with the primary emotional outcome, validate with 2–3 hard specs, and close with urgency. Copy is aspirational but grounded — buyers in this space distrust pure lifestyle fluff.

**STYLE PATTERNS LIKELY USED:**
• Benefit-first headline with emotional hook in the first 8 words
• Social proof markers ("10,000+ sold", star ratings) placed above the fold
• Feature-to-benefit copy structure — every spec is paired with "so you can..."
• Risk-reversal guarantee language placed close to the CTA

**COMPETITOR-MATCHED LISTING:**
Title: {product.title()} — Premium Quality | 10,000+ Sold | Free Delivery
Description: There's a reason buyers keep coming back. Our {product} delivers exactly what competitors promise but rarely achieve — consistent quality, honest specs, and a purchase you won't regret. Fast shipping. Easy returns. Zero risk.
Tags: {product.lower()}, premium, trusted, bestseller, authentic, quality, verified, top rated

**DIFFERENTIATION OPPORTUNITY:**
Competitors are NOT prominently featuring post-purchase confidence (warranty, support access, return policy) in their listing copy. A visible zero-risk guarantee message near the top could be a meaningful conversion advantage in this category."""


def _stub_ocr(p: str) -> str:
    return """**EXTRACTED KEY FEATURES:**
• Premium certified materials — meets international quality standards
• Weight / quantity / dimensions as printed on packaging
• Manufactured under ISO-compliant quality control protocols
• Authentic certifications and compliance markings present
• Clear usage, care, and storage instructions included

**GENERATED LISTING:**
Title: Premium Certified Product — Authentic, Quality-Assured, Fast Delivery

Description: Every detail of this product reflects a commitment to quality that goes beyond the label. Manufactured to international standards with verified materials, it arrives exactly as described — authentic, safe, and ready for immediate use. Trust backed by certification and real buyer reviews.

Bullet Benefits:
• Certified quality — independently verified to meet international safety standards
• Authentic ingredients / materials exactly as stated on official packaging
• Manufactured under strict ISO-compliant quality control at every stage
• Comprehensive usage guide included for best results and maximum longevity
• Satisfaction guaranteed — we stand behind every single unit we ship

Tags: certified, authentic, quality, trusted, premium, original, verified, safe, fast delivery, genuine

---
[STUB MODE — start Ollama for intelligent OCR-to-listing generation]"""


def _stub_performance(p: str) -> str:
    product = _extract(p, "Product", "product") or "your product"
    return f"""**PERFORMANCE SUMMARY:**
The listing optimisation for {product} delivered strong, across-the-board improvements. The updated copy better matches buyer search intent, resulting in significantly higher organic visibility and a meaningful lift in on-page conversion.

**METRICS BREAKDOWN:**
• Views: strong increase — improved SEO title captured additional long-tail search traffic
• Conversion Rate: meaningful improvement — benefit-led copy and trust signals reduced buyer hesitation
• Revenue: significant lift — combined effect of higher traffic volume and improved conversion rate

**KEY INSIGHTS:**
• The new title captures high-intent long-tail searches the old title missed entirely
• Benefit-focused bullet points reduced time-to-decision for first-time visitors
• Seasonal urgency language created a measurable spike in the add-to-cart rate

**RECOMMENDED NEXT STEPS:**
1. A/B test the title with a lifestyle-focused variant — emotional hooks may outperform SEO-first framing for this audience
2. Add 2–3 customer review highlights to reinforce the trust signals already in the copy
3. Run a seasonal variant (Eid / Black Friday) to measure promotional uplift against baseline

---
[STUB MODE — start Ollama for full AI-powered performance analysis]"""


def _stub_export(p: str) -> str:
    return f"""Handle,Title,Body (HTML),Tags,Published,Variant Price
my-product,"Premium Product — Quality Certified | Fast Delivery","<p>Your product description formatted for platform import.</p><ul><li>Premium quality — meets international standards</li><li>Authentic and certified</li><li>Fast shipping with secure packaging</li></ul>","premium,quality,authentic,trusted,bestseller",true,29.99

**IMPORT GUIDE:**
1. Copy the CSV row above and save it as a .csv file (UTF-8 encoding)
2. In Shopify Admin → Products → Import products
3. Upload the file and verify column mapping in the preview
4. Click "Import products" — items import as drafts by default

**NOTES:**
• Handle must be unique and URL-safe (lowercase, hyphens, no spaces)
• Body (HTML) supports: p, ul, li, strong, em, br tags
• Set Published to false to review before going live
• Variant Price must be a number with no currency symbol

---
[STUB MODE — start Ollama for intelligent platform-specific formatting]"""


def _stub_tone(p: str) -> str:
    product = _extract(p, "NEW PRODUCT", "new product", "product") or "new product"
    return f"""**BRAND VOICE ANALYSIS:**
• Tone: Confident and direct with subtle aspirational undertones
• Vocabulary level: Moderate — accessible but never simplistic
• Sentence structure: Short punchy sentences mixed with occasional medium elaboration
• Key linguistic patterns: Second-person "you" address, outcome-first framing, active verbs throughout
• Emotional register: Quiet authority — positions the buyer as discerning rather than bargain-hunting
• Unique quirks: Avoids superlatives, leads with outcomes not features, one clean CTA at the end

**NEW PRODUCT DESCRIPTION IN YOUR BRAND VOICE:**
The {product}. Made for people who already know what they want.

Not for everyone — and that's the point. While most products over-promise and under-deliver, this one does something harder: it does exactly what it says it will, every single time, without the noise.

If you're reading this far, you don't need convincing. You just need it in your cart.

---
[STUB MODE — start Ollama for precise brand voice replication from your sample]"""


def _stub_variants(p: str) -> str:
    product   = _extract(p, "Master Product", "product") or "Product"
    var_lines = [l[2:].strip() for l in p.split("\n") if l.startswith("- ")]
    variants  = var_lines or ["Variant A", "Variant B", "Variant C"]

    out = ""
    for v in variants:
        out += f"""**{v.upper()}**
Title: {product} — {v} Edition | Premium Quality | Authentic
Description: The {v} edition brings a distinctive character to the {product} collection. Crafted with the same uncompromising quality standards as every variant, but with the specific aesthetic and feel that makes {v.lower()} the right choice for buyers who know exactly what they want.
Tags: {product.lower()}, {v.lower()}, premium, authentic, quality, original
---

"""
    out += f"[STUB MODE — start Ollama and pull {OLLAMA_MODEL} for AI-generated variant listings]"
    return out