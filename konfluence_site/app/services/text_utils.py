import re
STOPWORDS = {"and","the","with","for","from","that","this","into","your","their","have","has","using","used","will","role","team","work","works","working","strong","ability","experience"}

def tokenize(text: str) -> list[str]:
    cleaned = re.sub(r"[^a-zA-Z0-9+#./ -]", " ", text.lower())
    tokens = [t.strip() for t in cleaned.split() if t.strip()]
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]
