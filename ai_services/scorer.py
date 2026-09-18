import re

EMOTIONAL_TRIGGERS = [
    'exclusive', 'limited', 'proven', 'love', 'perfect', 'amazing',
    'premium', 'save', 'free', 'now', 'today', 'only', 'best',
    'guarantee', 'trusted', 'authentic', 'genuine', 'fresh',
    'handcrafted', 'organic', 'natural', 'powerful', 'effortless',
]


def score_description(text: str) -> dict:
    score = 50

    word_count = len(text.split())
    if 100 <= word_count <= 600:
        score += 12
    elif word_count < 50:
        score -= 15

    bullet_count = len(re.findall(r'[•*\-]\s', text))
    score += min(bullet_count * 3, 15)

    text_lower = text.lower()
    triggers_found = sum(1 for t in EMOTIONAL_TRIGGERS if t in text_lower)
    score += min(triggers_found * 2, 16)

    cta_patterns = ['order now', 'buy now', 'shop now', 'get yours', 'add to cart', "don't miss"]
    if any(cta in text_lower for cta in cta_patterns):
        score += 8

    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    if sentences:
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if 8 <= avg_len <= 20:
            score += 7

    score = max(20, min(score, 99))

    return {
        'overall':               score,
        'ctr_probability':       round(score * 0.92),
        'conversion_likelihood': round(score * 0.78),
    }