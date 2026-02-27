from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


# -----------------------------
# 1) Customizable dictionaries
# -----------------------------

# Map “concepts” to keywords/synonyms. Add your own.
CONCEPTS: Dict[str, List[str]] = {
    "sql": ["sql", "postgres", "snowflake", "oracle", "sql server"],
    "python": ["python", "pandas", "numpy"],
    "excel": ["excel", "vlookup", "pivot", "power query"],
    "tableau": ["tableau", "power bi", "bi dashboard", "dashboards"],
    "etl_data_pipelines": ["etl", "data pipeline", "data ingestion", "data integration", "api integration"],
    "requirements": ["requirements", "elicitation", "user stories", "brd", "frd", "acceptance criteria"],
    "agile": ["agile", "scrum", "kanban", "sprint", "jira"],
    "stakeholders": ["stakeholder", "executive", "leadership", "cross-functional", "business partner"],
    "vendor_mgmt": ["vendor", "third-party", "procurement", "contract", "sla", "sow"],
    "data_ops": ["data operations", "data ops", "data quality", "dq", "metadata", "data governance"],
    "finance_domain": [
        "asset management", "fixed income", "equity", "derivatives", "trading",
        "trade lifecycle", "fund accounting", "performance attribution", "risk"
    ],
    "program_project_mgmt": ["pmp", "program", "portfolio", "roadmap", "timeline", "raids", "risk log"],
    "process_improvement": ["lean", "six sigma", "continuous improvement", "kaizen", "automation"],
    "leadership": ["lead", "managed", "manager", "director", "mentored", "coach", "owned", "accountable"],
}

# Some concepts are often “must-have” for certain role families.
DEFAULT_MUST_HAVE = ["requirements", "stakeholders"]


# -----------------------------
# 2) Text helpers
# -----------------------------

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\s\-\/\.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def count_any(text: str, phrases: List[str]) -> int:
    """Count how many distinct phrases appear at least once."""
    found = 0
    for p in phrases:
        if p in text:
            found += 1
    return found

def extract_years_requirement(job_text: str) -> Optional[int]:
    """
    Try to find patterns like:
    - "5+ years"
    - "3 years of experience"
    Returns the max found, if any.
    """
    job_text = normalize(job_text)
    matches = re.findall(r"(\d+)\s*\+?\s*years", job_text)
    if not matches:
        matches = re.findall(r"(\d+)\s*\+?\s*yrs", job_text)
    if matches:
        return max(int(x) for x in matches)
    return None

def estimate_years_from_resume(resume_text: str) -> Optional[int]:
    """
    Lightweight heuristic: look for year ranges like "2017-2022", "2019 – Present"
    and estimate total span (very rough).
    You can replace this with your own structured resume parsing later.
    """
    t = normalize(resume_text)
    year_pairs = re.findall(r"(20\d{2})\s*[\-\–]\s*(20\d{2}|present)", t)
    years = []
    for a, b in year_pairs:
        start = int(a)
        end = 2026 if b == "present" else int(b)
        if 1990 < start <= end <= 2035:
            years.append(end - start)
    if years:
        # sum of spans tends to overcount if roles overlap, so take max span
        return max(years)
    return None


# -----------------------------
# 3) Scoring components
# -----------------------------

@dataclass
class FitResult:
    score: float
    band: str
    must_have_missing: List[str]
    concept_hits: Dict[str, int]
    tfidf_similarity: float
    years_required: Optional[int]
    years_estimated: Optional[int]


def score_must_haves(resume: str, job: str, must_haves: List[str]) -> Tuple[float, List[str]]:
    """
    Must-have coverage heavily impacts fit.
    35 points max.
    """
    res = normalize(resume)
    missing = []
    hits = 0
    for concept in must_haves:
        keywords = CONCEPTS.get(concept, [concept])
        if count_any(res, [normalize(k) for k in keywords]) > 0:
            hits += 1
        else:
            missing.append(concept)

    if not must_haves:
        return 0.0, []

    coverage = hits / len(must_haves)
    return 35.0 * coverage, missing


def score_concepts(resume: str) -> Dict[str, int]:
    res = normalize(resume)
    hits = {}
    for concept, keywords in CONCEPTS.items():
        hits[concept] = count_any(res, [normalize(k) for k in keywords])
    return hits


def score_skills(concept_hits: Dict[str, int]) -> float:
    """
    25 points max.
    Reward breadth of relevant concepts present.
    """
    # Give more weight to these (tune to your target roles)
    weighted = {
        "sql": 2.0,
        "python": 2.0,
        "excel": 1.0,
        "tableau": 1.0,
        "etl_data_pipelines": 2.0,
        "requirements": 2.0,
        "agile": 1.5,
        "stakeholders": 2.0,
        "vendor_mgmt": 1.0,
        "data_ops": 2.0,
        "program_project_mgmt": 1.5,
        "process_improvement": 1.5,
    }
    total_w = sum(weighted.values())
    got = 0.0
    for c, w in weighted.items():
        got += w * (1.0 if concept_hits.get(c, 0) > 0 else 0.0)

    return 25.0 * (got / total_w)


def score_domain(concept_hits: Dict[str, int]) -> float:
    """
    10 points max.
    """
    finance = 1.0 if concept_hits.get("finance_domain", 0) > 0 else 0.0
    dataops = 1.0 if concept_hits.get("data_ops", 0) > 0 else 0.0
    return 10.0 * (0.6 * finance + 0.4 * dataops)


def score_experience(resume: str, job: str, concept_hits: Dict[str, int]) -> Tuple[float, Optional[int], Optional[int]]:
    """
    20 points max.
    Part A: years alignment (0–12)
    Part B: leadership signal (0–8)
    """
    years_required = extract_years_requirement(job)
    years_est = estimate_years_from_resume(resume)

    # Years score
    if years_required is None or years_est is None:
        years_score = 6.0  # neutral default if missing info
    else:
        # If you meet or exceed requirement => full
        if years_est >= years_required:
            years_score = 12.0
        else:
            # partial credit
            years_score = 12.0 * (years_est / max(years_required, 1))

    leadership = 1.0 if concept_hits.get("leadership", 0) > 0 else 0.0
    leadership_score = 8.0 * leadership

    return years_score + leadership_score, years_required, years_est


def tfidf_similarity(resume: str, job: str) -> float:
    """
    Return cosine similarity of TF-IDF vectors.
    """
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    X = vec.fit_transform([normalize(resume), normalize(job)])
    # cosine similarity between row0 and row1:
    sim = (X[0] @ X[1].T).A[0][0]
    return float(sim)


def score_similarity(sim: float) -> float:
    """
    10 points max. TF-IDF sim tends to be ~0.05–0.35 for related docs.
    We scale gently and cap.
    """
    scaled = min(sim / 0.35, 1.0)  # tune divisor if needed
    return 10.0 * scaled


def band(score: float, missing_must: List[str]) -> str:
    # If you miss any must-have, cap at Strong Fit (not Best Fit)
    if score >= 85 and not missing_must:
        return "Best fit"
    if score >= 70:
        return "Strong fit"
    if score >= 55:
        return "Moderate fit"
    return "Weak fit"


def evaluate_fit(resume_text: str, job_text: str, must_haves: Optional[List[str]] = None) -> FitResult:
    must = must_haves if must_haves is not None else DEFAULT_MUST_HAVE

    must_score, missing = score_must_haves(resume_text, job_text, must)
    hits = score_concepts(resume_text)
    skills_score = score_skills(hits)
    domain_score = score_domain(hits)
    exp_score, yrs_req, yrs_est = score_experience(resume_text, job_text, hits)

    sim = tfidf_similarity(resume_text, job_text)
    sim_score = score_similarity(sim)

    total = must_score + skills_score + domain_score + exp_score + sim_score
    total = float(np.clip(total, 0, 100))

    return FitResult(
        score=round(total, 1),
        band=band(total, missing),
        must_have_missing=missing,
        concept_hits=hits,
        tfidf_similarity=round(sim, 3),
        years_required=yrs_req,
        years_estimated=yrs_est,
    )


if __name__ == "__main__":
    # Paste your resume and the job description here (or load from files).
    RESUME = """PASTE YOUR RESUME TEXT HERE"""
    JOB = """PASTE JOB DESCRIPTION / REQUIREMENTS HERE"""

    result = evaluate_fit(RESUME, JOB, must_haves=["requirements", "stakeholders", "agile"])

    print("\n=== FIT RESULT ===")
    print("Score:", result.score)
    print("Band :", result.band)
    print("TF-IDF similarity:", result.tfidf_similarity)
    print("Years required:", result.years_required, " | Years estimated:", result.years_estimated)
    print("Missing must-haves:", result.must_have_missing)

    # Show top concept hits (present vs absent)
    present = [k for k, v in result.concept_hits.items() if v > 0]
    absent = [k for k, v in result.concept_hits.items() if v == 0]
    print("\nConcepts present:", ", ".join(sorted(present)))
    print("Concepts absent :", ", ".join(sorted(absent)))