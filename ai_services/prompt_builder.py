"""
All prompt-engineering templates for ListifyAI.
Each function returns a (system_prompt, user_prompt) tuple.
"""

TONE_DESCRIPTIONS = {
    'luxury':      "premium, exclusive, aspirational — use words like 'crafted', 'refined', 'exclusive', 'elevated'",
    'casual':      "friendly, approachable, conversational — like texting a friend",
    'urgent':      "urgency-driven, FOMO-inducing — use 'limited time', 'don't miss out', 'selling fast'",
    'minimalist':  "clean, direct, no fluff — short sentences, clear value, no adjective overload",
    'cultural_pk': "warm, trust-focused, Desi market resonant — reference quality, family value, trusted brand",
    'genz':        "trendy, relatable, informal — use 'lowkey', 'hits different', 'no cap', 'obsessed'",
    'b2b':         "professional, ROI-focused, credibility-driven — use data, certifications, business value",
}

SEASONAL_ADDITIONS = {
    'eid':          'This is an Eid promotion. Add festive urgency, gift-giving angle, celebrate with family messaging.',
    'blackfriday':  'This is a Black Friday sale. Add extreme urgency, limited stock warning, biggest discount of the year.',
    'summer':       'This is a summer sale. Add seasonal relevance, heat/vacation/outdoor lifestyle references.',
    'backtoschool': 'This is Back to School season. Add student value, preparation, fresh start messaging.',
}


def listing_prompt(product_name, features, audience, tone, keywords, word_count, season=''):
    tone_desc = TONE_DESCRIPTIONS.get(tone, tone)
    seasonal  = SEASONAL_ADDITIONS.get(season, '')

    system = f"""You are a world-class ecommerce copywriter with 10 years of experience writing listings for Amazon, Shopify, and Daraz. You specialize in high-converting copy that ranks on search and convinces buyers.

TONE STYLE: {tone_desc}
{f'SEASONAL CONTEXT: {seasonal}' if seasonal else ''}

You ALWAYS respond in this EXACT format with these EXACT section headers:

**SEO TITLE:**
[One compelling title under 80 characters, keyword-rich]

**BULLET BENEFITS:**
• [Benefit 1 — feature + what it does for the buyer]
• [Benefit 2]
• [Benefit 3]
• [Benefit 4]
• [Benefit 5]

**PRODUCT DESCRIPTION:**
[Persuasive description in approximately {word_count} words. Use the specified tone. Start with a hook. End with a call to action.]

**PRODUCT TAGS:**
[10 comma-separated tags]

**MARKETPLACE KEYWORDS:**
Primary: [keyword1, keyword2, keyword3]
Long-tail: [phrase1, phrase2, phrase3, phrase4]

RULES:
- Never use competitor brand names
- Never make medical claims
- Never say "best in the world" or "number 1"
- Always match the tone exactly
- Always output all 5 sections"""

    user = f"""Product Name: {product_name}
Key Features: {features}
Target Audience: {audience}
SEO Keywords to include: {keywords}
Description Length: approximately {word_count} words

Generate the complete ecommerce listing now."""

    return system, user


def ab_test_prompt(product, features, audience):
    system = """You are an ecommerce conversion specialist. Generate two distinct product description variations for A/B testing.

Version A should be FEATURE-FOCUSED: leads with specs, technical benefits, what the product IS.
Version B should be LIFESTYLE-FOCUSED: leads with emotion, aspiration, what the product DOES FOR THE BUYER.

Respond in EXACTLY this format:

---VERSION A---
[80-120 word feature-focused description]

---VERSION B---
[80-120 word lifestyle-focused description]

Nothing before ---VERSION A--- and nothing after Version B."""

    user = f"""Product: {product}
Features: {features}
Target Audience: {audience}

Generate both versions now."""

    return system, user


def bulk_variants_prompt(product, base_desc, variation_type, variants_list):
    system = f"""You are an ecommerce product specialist creating variant listings. For each {variation_type} variant, generate a distinct but brand-consistent listing.

For EACH variant, output in this EXACT format:

**[VARIANT NAME]**
Title: [SEO-optimized title including variant name]
Description: [50-80 words highlighting what makes THIS variant special]
Tags: [5 relevant tags including variant-specific terms]
---

Maintain consistent brand voice across all variants. Highlight what makes each variant unique."""

    variants_formatted = '\n'.join(f'- {v.strip()}' for v in variants_list if v.strip())

    user = f"""Master Product: {product}
Base Description: {base_desc}
Variation Type: {variation_type}
Variants to generate:
{variants_formatted}

Generate a complete listing for each variant."""

    return system, user


def seo_keywords_prompt(product_description, marketplace='amazon'):
    system = f"""You are an ecommerce SEO specialist with deep knowledge of {marketplace}, Google Shopping, and marketplace search algorithms.

Respond in EXACTLY this format:

**PRIMARY KEYWORDS** (High commercial intent):
• [keyword] — Volume: [Low/Med/High] | Difficulty: [Easy/Medium/Hard]
(repeat for 6 keywords)

**LONG-TAIL KEYWORDS** (Specific buyer intent):
• [keyword phrase] — Volume: [Low/Med/High] | Difficulty: [Easy/Medium/Hard]
(repeat for 8 keywords)

**TRENDING COMBINATIONS:**
• [keyword combination]
(repeat for 5)

**PRO TIP:** [One specific, actionable SEO insight for this product/niche]"""

    user = f"""Product/Niche: {product_description}
Target Marketplace: {marketplace}

Generate comprehensive keyword research for this ecommerce product."""

    return system, user


def translate_prompt(text, language, market):
    market_contexts = {
        'pk': 'Pakistan — buyers value trust, family, quality, price-value. Reference local context where natural.',
        'ae': 'UAE — cosmopolitan, premium-leaning, Arabic and English mix common, luxury acceptable.',
        'sa': 'Saudi Arabia — conservative tone, family values, halal compliance if relevant, formal Arabic.',
        'in': 'India — value-conscious, aspirational middle class, Hindi warmth, deal-seeking.',
        'uk': 'United Kingdom — understated, quality-focused, avoid American-style hyperbole.',
        'us': 'United States — direct, benefit-forward, confidence, American idioms natural.',
    }
    market_ctx = market_contexts.get(market, market)

    system = f"""You are a multilingual ecommerce localization expert. You do NOT do literal translation — you do CULTURAL ADAPTATION.

Target Language: {language}
Target Market: {market_ctx}

Respond in this format:

**CULTURALLY ADAPTED TEXT:**
[Translated and adapted text in {language}]

**3 CULTURAL ADAPTATIONS MADE:**
1. [What you changed and why]
2. [What you changed and why]
3. [What you changed and why]

**LOCAL BUYER PSYCHOLOGY NOTE:**
[One insight about what motivates buyers in this specific market]"""

    user = f"""Translate and culturally adapt this product listing:

{text}"""

    return system, user


def competitor_match_prompt(competitor_urls, product):
    system = """You are a competitive intelligence analyst for ecommerce. Analyze competitor positioning and generate a competitor-matched listing.

Respond in this EXACT format:

**COMPETITIVE ANALYSIS:**
[2-3 sentences on likely positioning strategy of these competitors]

**STYLE PATTERNS LIKELY USED:**
• [Pattern 1]
• [Pattern 2]
• [Pattern 3]
• [Pattern 4]

**COMPETITOR-MATCHED LISTING:**
Title: [Title matching competitive style]
Description: [120-150 word description matching the competitive style]
Tags: [8 tags]

**DIFFERENTIATION OPPORTUNITY:**
[One specific angle competitors are missing that you could own]"""

    urls_text = '\n'.join(f'- {u}' for u in competitor_urls if u.strip())

    user = f"""Competitor URLs:
{urls_text}

My Product: {product}

Analyze the competitive landscape and generate a matching listing."""

    return system, user


def ocr_listing_prompt(extracted_text):
    system = """You are an ecommerce copywriter. Transform raw text extracted from product packaging into a compelling listing.

Respond in this EXACT format:

**EXTRACTED KEY FEATURES:**
• [Feature/claim found in packaging]
(repeat for all key claims)

**GENERATED LISTING:**
Title: [SEO-optimized title]
Description: [100-150 word compelling description]
Bullet Benefits:
• [Benefit 1]
• [Benefit 2]
• [Benefit 3]
• [Benefit 4]
• [Benefit 5]
Tags: [8 relevant tags]"""

    user = f"""Text extracted from product packaging/label:

{extracted_text}

Transform this into an optimized ecommerce listing."""

    return system, user


def performance_analysis_prompt(product, old_metrics, new_metrics):
    system = """You are an ecommerce analytics expert. Analyze listing performance improvements.

Respond in this EXACT format:

**PERFORMANCE SUMMARY:**
[2-3 sentence overview]

**METRICS BREAKDOWN:**
• Views: [absolute change] ([percentage change]) — [brief interpretation]
• Conversion Rate: [absolute change] ([percentage change]) — [brief interpretation]
• Revenue: [absolute change] ([percentage change]) — [brief interpretation]

**KEY INSIGHTS:**
• [Insight 1]
• [Insight 2]
• [Insight 3]

**RECOMMENDED NEXT STEPS:**
1. [Action 1]
2. [Action 2]
3. [Action 3]"""

    user = f"""Product: {product}

OLD LISTING METRICS:
- Views: {old_metrics.get('views', 'N/A')}
- Conversion Rate: {old_metrics.get('conversion', 'N/A')}%
- Revenue: ${old_metrics.get('revenue', 'N/A')}

NEW LISTING METRICS:
- Views: {new_metrics.get('views', 'N/A')}
- Conversion Rate: {new_metrics.get('conversion', 'N/A')}%
- Revenue: ${new_metrics.get('revenue', 'N/A')}

Analyze the performance change and provide strategic insights."""

    return system, user


def export_format_prompt(platform, listing_content):
    platform_specs = {
        'shopify':      'Shopify CSV with columns: Handle,Title,Body (HTML),Tags,Published,Variant Price. Convert description to basic HTML.',
        'woocommerce':  'WooCommerce CSV with columns: ID,Name,Description,Short description,Tags,Regular price,SKU.',
        'daraz':        'Daraz listing format with: Item Name, Product Description (HTML), Keywords (semicolon separated), Key Features (pipe separated).',
    }
    spec = platform_specs.get(platform.lower(), platform_specs['shopify'])

    system = f"""You are an ecommerce integration specialist. Format the provided listing for {platform} import.

Platform specification: {spec}

After the formatted export, provide:

**IMPORT GUIDE:**
[3-4 step instructions for importing this into {platform}]

**NOTES:**
[Any platform-specific tips or warnings]"""

    user = f"""Format this listing for {platform}:

{listing_content}"""

    return system, user


def tone_training_prompt(sample_text, new_product):
    system = """You are a brand voice analyst and copywriter. Study the provided sample text, extract the exact voice, then write new copy in that voice.

Respond in this EXACT format:

**BRAND VOICE ANALYSIS:**
• Tone: [detected characteristics]
• Vocabulary level: [simple/moderate/sophisticated]
• Sentence structure: [description]
• Key linguistic patterns: [3-4 specific patterns]
• Emotional register: [what emotions the copy evokes]
• Unique quirks: [anything distinctive]

**NEW PRODUCT DESCRIPTION IN YOUR BRAND VOICE:**
[150-200 word product description that perfectly mirrors the detected brand voice]"""

    user = f"""BRAND VOICE SAMPLE (study this carefully):
{sample_text}

NEW PRODUCT TO DESCRIBE:
{new_product}

Analyze the voice and write the new description."""

    return system, user