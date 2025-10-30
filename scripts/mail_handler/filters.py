import logging

logger = logging.getLogger(__name__)

def load_filters(cfg):
    categories = {}
    raw = cfg.get('filters', {}) or {}
    for cat, body in raw.items():
        keywords = [k.lower() for k in (body.get('keywords') or [])]
        if keywords:
            categories[cat] = keywords
    logger.debug("Loaded categories: %s", list(categories.keys()))
    return categories

def categorize_message(categories, subject, snippet, sender):
    text = " ".join([subject or "", snippet or "", sender or ""]).lower()
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in text:
                return cat
    return None
