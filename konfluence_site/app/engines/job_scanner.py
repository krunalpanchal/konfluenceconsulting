\
"""
Krunal Job Hunter - job_scanner.py
- Searches jobs via SerpAPI Google Jobs (and optional SerpAPI Indeed engine)
- Scores job relevance vs your resume using TF-IDF (and optional embeddings)
- Dedupes and exports CSV + JSON
- Optional email digest via SMTP

Usage:
  1) pip install -r requirements.txt
  2) Copy config.example.json -> config.json and edit
  3) Set SERPAPI_KEY in your environment
  4) python job_scanner.py

Notes:
  - Direct scraping LinkedIn/Indeed pages is brittle and may violate their ToS.
  - This uses SerpAPI search engines and returns links you can open and apply.
"""
from __future__ import annotations

import os
import json
import time
import hashlib
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

import requests
import pandas as pd

from matchers import score_jobs_tfidf, score_jobs_embeddings
from emailer import send_email_digest


SERPAPI_URL = "https://serpapi.com/search.json"
USER_AGENT = "krunal-job-hunter/1.0"


@dataclass
class JobResult:
    source: str
    title: str
    company: str
    location: str
    description_snippet: str
    url: str
    posted_at: str
    score: float
    job_id: str

    def to_row(self) -> Dict:
        d = asdict(self)
        d["score"] = round(float(self.score), 4)
        return d


def clean_text(s: str) -> str:
    s = s or ""
    s = re.sub(r"\s+", " ", s).strip()
    return s


def hash_id(*parts: str) -> str:
    h = hashlib.sha256("||".join([p or "" for p in parts]).encode("utf-8")).hexdigest()
    return h[:16]


def load_config(path: str = "config.json") -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def serpapi_get(api_key: str, params: Dict, sleep_s: float = 0.5) -> Dict:
    params = dict(params)
    params["api_key"] = api_key
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(SERPAPI_URL, params=params, headers=headers, timeout=60)
    r.raise_for_status()
    time.sleep(sleep_s)
    return r.json()


def search_google_jobs(api_key: str, query: str, location: str, num_results: int) -> List[Dict]:
    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "hl": "en",
        "num": min(max(num_results, 10), 100),
    }
    data = serpapi_get(api_key, params)
    return data.get("jobs_results", []) or []


def search_indeed_jobs(api_key: str, query: str, location: str, num_results: int, days_back: int) -> List[Dict]:
    # Availability depends on SerpAPI plan/engine support.
    params = {
        "engine": "indeed",
        "q": query,
        "l": location,
        "fromage": str(days_back),
        "sort": "date",
        "limit": min(max(num_results, 10), 50),
    }
    data = serpapi_get(api_key, params)
    return data.get("jobs_results", data.get("organic_results", [])) or []


def normalize_google(raw: Dict) -> Tuple[str, str, str, str, str, str]:
    title = clean_text(raw.get("title", ""))
    company = clean_text(raw.get("company_name") or raw.get("company", ""))
    location = clean_text(raw.get("location", ""))
    snippet = clean_text(raw.get("description", raw.get("snippet", "")))
    posted = clean_text(raw.get("detected_extensions", {}).get("posted_at", raw.get("posted_at", "")))
    url = ""
    if raw.get("related_links"):
        url = raw["related_links"][0].get("link", "") or ""
    url = clean_text(url)
    return title, company, location, snippet, posted, url


def normalize_indeed(raw: Dict) -> Tuple[str, str, str, str, str, str]:
    title = clean_text(raw.get("title", raw.get("position", "")))
    company = clean_text(raw.get("company_name", raw.get("company", "")))
    location = clean_text(raw.get("location", raw.get("formattedLocation", "")))
    snippet = clean_text(raw.get("snippet", raw.get("description", "")))
    posted = clean_text(raw.get("date", raw.get("posted_at", "")))
    url = clean_text(raw.get("link", raw.get("jobkey", "")))
    return title, company, location, snippet, posted, url


def load_resume_text(resume_file: str, keywords_boost: List[str]) -> str:
    with open(resume_file, "r", encoding="utf-8") as f:
        base = f.read()
    # Light boost so the matcher prefers your domain terms
    boost = " ".join(keywords_boost or [])
    return clean_text(boost + " " + base)


def dedupe_and_filter(results: List[JobResult]) -> List[JobResult]:
    seen = set()
    out: List[JobResult] = []
    for r in results:
        key = (r.title.lower(), r.company.lower(), r.location.lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    out.sort(key=lambda x: x.score, reverse=True)
    return out


def main() -> None:
    cfg = load_config("config.json")
    api_key = os.getenv(cfg.get("serpapi_key_env", "SERPAPI_KEY"), "").strip()
    if not api_key:
        raise RuntimeError(f"Missing SerpAPI key. Set env var {cfg.get('serpapi_key_env','SERPAPI_KEY')}.")

    locations = cfg["locations"]
    queries = cfg["queries"]
    per_query_results = int(cfg.get("per_query_results", 20))
    min_score = float(cfg.get("min_score", 0.14))
    days_back = int(cfg.get("days_back", 14))
    include_indeed = bool(cfg.get("include_indeed_engine", True))
    use_embeddings = bool(cfg.get("use_embeddings", False))

    out_dir = cfg.get("output_dir", "outputs")
    os.makedirs(out_dir, exist_ok=True)

    resume_text = load_resume_text(cfg.get("resume_file", "resume.txt"), cfg.get("keywords_boost", []))

    raw_norm: List[Tuple[str, str, str, str, str, str]] = []

    for loc in locations:
        for q in queries:
            # Google Jobs
            try:
                jobs = search_google_jobs(api_key, q, loc, per_query_results)
                for item in jobs:
                    title, company, location, snippet, posted, url = normalize_google(item)
                    raw_norm.append(("google_jobs", title, company, location, snippet, posted, url))
            except Exception as e:
                print(f"[WARN] google_jobs failed: {q} / {loc} -> {e}")

            # Indeed (optional)
            if include_indeed:
                try:
                    jobs = search_indeed_jobs(api_key, q, loc, per_query_results, days_back)
                    for item in jobs:
                        title, company, location, snippet, posted, url = normalize_indeed(item)
                        raw_norm.append(("indeed", title, company, location, snippet, posted, url))
                except Exception as e:
                    print(f"[WARN] indeed failed: {q} / {loc} -> {e}")

    if not raw_norm:
        print("[INFO] No results returned.")
        return

    job_texts = [
        clean_text(f"{t} {c} {l} {s}")
        for (_src, t, c, l, s, _p, _u) in raw_norm
    ]

    if use_embeddings:
        scores = score_jobs_embeddings(resume_text, job_texts)
    else:
        scores = score_jobs_tfidf(resume_text, job_texts)

    results: List[JobResult] = []
    for i, (src, title, company, location, snippet, posted, url) in enumerate(raw_norm):
        score = float(scores[i])
        if score < min_score:
            continue

        job_id = hash_id(src, title, company, location, url)
        results.append(
            JobResult(
                source=src,
                title=title or "(missing title)",
                company=company or "(missing company)",
                location=location or "(missing location)",
                description_snippet=(snippet or "")[:700],
                url=url,
                posted_at=posted,
                score=score,
                job_id=job_id,
            )
        )

    results = dedupe_and_filter(results)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(out_dir, f"job_matches_{stamp}.csv")
    json_path = os.path.join(out_dir, f"job_matches_{stamp}.json")

    df = pd.DataFrame([r.to_row() for r in results])
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2)

    print(f"[DONE] {len(results)} matches saved:")
    print(f"  - {csv_path}")
    print(f"  - {json_path}")

    # Optional email
    email_cfg = cfg.get("email", {})
    if email_cfg.get("enabled"):
        try:
            send_email_digest(email_cfg, df.head(25), csv_path=csv_path)
            print("[DONE] Email digest sent.")
        except Exception as e:
            print(f"[WARN] Email sending failed: {e}")


if __name__ == "__main__":
    main()
