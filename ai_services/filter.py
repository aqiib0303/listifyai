import re

BLOCKED_PATTERNS = [
    r'\bnike\b', r'\badidas\b', r'\bapple\b', r'\bsamsung\b', r'\bgucci\b',
    r'\bprada\b', r'\blouis\s*vuitton\b', r'\brolex\b',
    r'guaranteed cure', r'100% cure', r'clinically proven',
    r'fda approved', r'treats \w+', r'cures \w+', r'heals \w+',
    r'best in the world', r'number 1 brand', r'#1 in the world',
    r'nobody else', r'only one in the world',
    r'make money fast', r'get rich', r'guaranteed results',
]


def filter_negative_keywords(text: str) -> dict:
    flagged  = []
    filtered = text

    for pattern in BLOCKED_PATTERNS:
        regex   = re.compile(pattern, re.IGNORECASE)
        matches = regex.findall(filtered)
        if matches:
            flagged.extend(matches)
            filtered = regex.sub('[FLAGGED]', filtered)

    return {
        'filtered_text': filtered,
        'flagged':       list(set(flagged)),
        'is_clean':      len(flagged) == 0,
    }