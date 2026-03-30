import os
from typing import List
from app.engines.job_scanner import (
    search_google_jobs,
    search_indeed_jobs,
    normalize_google,
    normalize_indeed,
    clean_text,
    hash_id,
    dedupe_and_filter,
    JobResult,
)
from app.engines.matchers import score_jobs_tfidf, score_jobs_embeddings

def rank_jobs_for_profile(profile_text: str, jobs: list[dict], top_k: int = 10) -> list[dict]:
    job_texts = [clean_text(f"{j.get('title', '')} {j.get('company', '')} {j.get('location', '')} {j.get('description', '')}") for j in jobs]
    scores = score_jobs_tfidf(profile_text, job_texts)
    ranked = []
    for i, job in enumerate(jobs):
        ranked.append({
            "job_id": job["id"],
            "title": job["title"],
            "company": job.get("company"),
            "location": job.get("location"),
            "score": round(float(scores[i]) * 100, 2),
            "matched_terms": [],
            "explanation": "Ranked using uploaded job matcher engine.",
            "url": job.get("url"),
        })
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:top_k]

def run_live_job_search(
    api_key: str,
    resume_text: str,
    queries: list[str],
    locations: list[str],
    per_query_results: int = 20,
    min_score: float = 0.14,
    include_indeed_engine: bool = True,
    use_embeddings: bool = False,
    days_back: int = 14,
) -> list[dict]:
    raw_norm = []
    for loc in locations:
        for q in queries:
            try:
                jobs = search_google_jobs(api_key, q, loc, per_query_results)
                for item in jobs:
                    title, company, location, snippet, posted, url = normalize_google(item)
                    raw_norm.append(("google_jobs", title, company, location, snippet, posted, url))
            except Exception:
                pass
            if include_indeed_engine:
                try:
                    jobs = search_indeed_jobs(api_key, q, loc, per_query_results, days_back)
                    for item in jobs:
                        title, company, location, snippet, posted, url = normalize_indeed(item)
                        raw_norm.append(("indeed", title, company, location, snippet, posted, url))
                except Exception:
                    pass

    if not raw_norm:
        return []

    job_texts = [clean_text(f"{t} {c} {l} {s}") for (_src, t, c, l, s, _p, _u) in raw_norm]
    scores = score_jobs_embeddings(resume_text, job_texts) if use_embeddings else score_jobs_tfidf(resume_text, job_texts)

    results = []
    for i, (src, title, company, location, snippet, posted, url) in enumerate(raw_norm):
        score = float(scores[i])
        if score < min_score:
            continue
        results.append(JobResult(
            source=src,
            title=title or "(missing title)",
            company=company or "(missing company)",
            location=location or "(missing location)",
            description_snippet=(snippet or "")[:700],
            url=url,
            posted_at=posted,
            score=score,
            job_id=hash_id(src, title, company, location, url),
        ))

    results = dedupe_and_filter(results)
    return [r.to_row() for r in results]
