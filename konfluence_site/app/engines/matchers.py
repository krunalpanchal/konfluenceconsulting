\
from __future__ import annotations

from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def score_jobs_tfidf(resume_text: str, job_texts: List[str]) -> np.ndarray:
    """
    Fast + solid baseline. Good enough to start.
    """
    corpus = [resume_text] + list(job_texts)
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=60000)
    X = vec.fit_transform(corpus)
    sims = cosine_similarity(X[0:1], X[1:]).flatten()
    return sims


def score_jobs_embeddings(resume_text: str, job_texts: List[str]) -> np.ndarray:
    """
    Higher quality matching (semantic).
    Requires:
      pip install sentence-transformers torch

    In config.json: set "use_embeddings": true
    """
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise RuntimeError(
            "Embeddings enabled but sentence-transformers not installed. "
            "Run: pip install sentence-transformers torch"
        ) from e

    model = SentenceTransformer("all-MiniLM-L6-v2")
    emb_resume = model.encode([resume_text], normalize_embeddings=True)
    emb_jobs = model.encode(job_texts, normalize_embeddings=True)
    sims = (emb_jobs @ emb_resume[0]).astype(float)
    return np.array(sims)
