from __future__ import annotations

import io
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Semantic embeddings (much better matching)
from sentence_transformers import SentenceTransformer

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Radar chart
import matplotlib.pyplot as plt


# ----------------------------
# Concepts dictionary (tuneable)
# ----------------------------
CONCEPTS: Dict[str, List[str]] = {
    "requirements": ["requirements", "elicitation", "user stories", "brd", "frd", "acceptance criteria", "use cases"],
    "stakeholders": ["stakeholder", "executive", "leadership", "cross-functional", "business partner"],
    "agile": ["agile", "scrum", "kanban", "sprint", "jira", "backlog", "standup", "retrospective"],

    "sql": ["sql", "postgres", "snowflake", "oracle", "sql server", "tsql"],
    "python": ["python", "pandas", "numpy"],
    "bi": ["tableau", "power bi", "dashboard", "dashboards", "reporting"],
    "etl_data": ["etl", "data pipeline", "data ingestion", "data integration", "api", "api integration"],
    "data_quality": ["data quality", "dq", "reconciliation", "controls", "validation", "data governance", "metadata"],
    "vendor_mgmt": ["vendor", "third-party", "contract", "sla", "sow", "procurement"],
    "process_improvement": ["lean", "six sigma", "continuous improvement", "kaizen", "automation"],
    "program_project_mgmt": ["pmp", "program", "portfolio", "roadmap", "timeline", "raids", "risk log"],

    "leadership": ["lead", "managed", "manager", "director", "mentored", "coach", "owned", "accountable"],

    "asset_mgmt_domain": [
        "asset management", "fixed income", "equity", "derivatives", "trading", "trade lifecycle",
        "fund accounting", "nav", "performance attribution", "risk", "portfolio", "aum"
    ],
}

DEFAULT_MUST_HAVE = ["requirements", "stakeholders", "agile"]


# ----------------------------
# Models (load once)
# ----------------------------
_EMBED_MODEL: Optional[SentenceTransformer] = None

def get_embed_model() -> SentenceTransformer:
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        # Good default: fast and strong
        _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBED_MODEL


# ----------------------------
# Helpers
# ----------------------------
def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\s\-\/\.\,\:\;]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def keyword_hits(text: str, keywords: List[str]) -> List[str]:
    t = normalize(text)
    found = []
    for k in keywords:
        k2 = normalize(k)
        if k2 and k2 in t:
            found.append(k)
    return sorted(list(dict.fromkeys(found)))

def concept_present(resume: str, concept: str) -> bool:
    keys = CONCEPTS.get(concept, [concept])
    return len(keyword_hits(resume, keys)) > 0


# ----------------------------
# Similarity engines
# ----------------------------
def tfidf_sim(resume: str, job: str) -> float:
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    X = vec.fit_transform([normalize(resume), normalize(job)])
    # version-safe cosine similarity (fixes csr_matrix .A error)
    return float(cosine_similarity(X[0:1], X[1:2])[0][0])

def embed_sim(resume: str, job: str) -> float:
    model = get_embed_model()
    emb = model.encode([resume, job], normalize_embeddings=True)
    # cosine similarity
    return float(np.dot(emb[0], emb[1]))


# ----------------------------
# Must-have extraction (auto)
# ----------------------------
def extract_must_haves(job_text: str, max_items: int = 6) -> List[str]:
    """
    Heuristic:
    - If job mentions a concept keyword, it becomes a candidate.
    - Prioritize core BA/Product/DataOps concepts.
    """
    job_n = normalize(job_text)
    priority = ["requirements", "stakeholders", "agile", "data_quality", "etl_data", "sql", "python", "vendor_mgmt"]

    hits = []
    for c in priority:
        keys = CONCEPTS.get(c, [c])
        if any(normalize(k) in job_n for k in keys):
            hits.append(c)

    # Fall back
    if not hits:
        hits = DEFAULT_MUST_HAVE.copy()

    # Deduplicate + cap
    out = []
    for x in hits:
        if x not in out:
            out.append(x)
    return out[:max_items]


# ----------------------------
# Scoring
# ----------------------------
@dataclass
class FitResult:
    score: float
    band: str
    must_have_present: List[str]
    must_have_missing: List[str]
    similarity_tfidf: float
    similarity_embedding: float
    component_breakdown: Dict[str, float]
    top_matched_keywords: List[str]
    top_missing_keywords: List[str]
    radar_values: Dict[str, float]  # values 0-1 for radar


def score_must_haves(resume: str, must_haves: List[str]) -> Tuple[float, List[str], List[str]]:
    present, missing = [], []
    for c in must_haves:
        (present if concept_present(resume, c) else missing).append(c)
    if not must_haves:
        return 0.0, present, missing
    coverage = len(present) / len(must_haves)
    return float(35.0 * coverage), present, missing


def score_skills(resume: str) -> float:
    weights = {
        "sql": 2.0,
        "python": 1.5,
        "bi": 1.0,
        "etl_data": 2.0,
        "data_quality": 2.0,
        "requirements": 2.0,
        "stakeholders": 2.0,
        "agile": 1.5,
        "vendor_mgmt": 1.0,
        "process_improvement": 1.5,
        "program_project_mgmt": 1.5,
        "leadership": 1.0,
        "asset_mgmt_domain": 1.5,
    }
    total = sum(weights.values())
    got = 0.0
    for c, w in weights.items():
        got += w * (1.0 if concept_present(resume, c) else 0.0)
    return float(25.0 * (got / total))


def score_domain(resume: str, job: str) -> float:
    job_fin = len(keyword_hits(job, CONCEPTS["asset_mgmt_domain"])) > 0
    res_fin = concept_present(resume, "asset_mgmt_domain")
    if job_fin and res_fin:
        return 10.0
    if res_fin:
        return 6.0
    return 3.0


def score_similarity_component(sim: float, cap_at: float = 0.75) -> float:
    # embeddings often higher; scale to 0-10 smoothly
    return float(10.0 * min(sim / cap_at, 1.0))


def band(score: float, missing_must: List[str]) -> str:
    if score >= 85 and not missing_must:
        return "Best fit"
    if score >= 70:
        return "Strong fit"
    if score >= 55:
        return "Moderate fit"
    return "Weak fit"


def extract_job_keywords_pool() -> List[str]:
    pool = []
    for v in CONCEPTS.values():
        pool.extend(v)
    # prefer meaningful phrases
    pool = sorted(set(pool), key=lambda x: (-len(x), x))
    return pool


def evaluate_fit(
    resume_text: str,
    job_text: str,
    must_haves: Optional[List[str]] = None,
    use_auto_must_haves: bool = True,
) -> FitResult:
    resume = normalize(resume_text)
    job = normalize(job_text)

    if use_auto_must_haves:
        must = extract_must_haves(job_text)
    else:
        must = must_haves or DEFAULT_MUST_HAVE

    must_score, must_present, must_missing = score_must_haves(resume, must)
    skills_score = score_skills(resume)
    domain_score = score_domain(resume, job)

    sim_tfidf = tfidf_sim(resume, job)
    sim_embed = embed_sim(resume_text, job_text)

    # Use embedding similarity for the 0–10 "responsibilities match"
    sim_score = score_similarity_component(sim_embed)

    total = must_score + skills_score + domain_score + sim_score
    total = float(np.clip(total, 0, 100))

    pool = extract_job_keywords_pool()
    matched = keyword_hits(resume, pool)
    missing = [k for k in pool if k not in matched]

    breakdown = {
        "Must-haves coverage (0–35)": round(must_score, 1),
        "Skills & tools match (0–25)": round(skills_score, 1),
        "Domain alignment (0–10)": round(domain_score, 1),
        "Semantic responsibilities match (0–10)": round(sim_score, 1),
    }

    # Values for radar (0–1)
    radar = {
        "Must-haves": float(np.clip(must_score / 35.0, 0, 1)),
        "Skills": float(np.clip(skills_score / 25.0, 0, 1)),
        "Domain": float(np.clip(domain_score / 10.0, 0, 1)),
        "Semantic Match": float(np.clip(sim_score / 10.0, 0, 1)),
        "Leadership": 1.0 if concept_present(resume, "leadership") else 0.0,
    }

    return FitResult(
        score=round(total, 1),
        band=band(total, must_missing),
        must_have_present=must_present,
        must_have_missing=must_missing,
        similarity_tfidf=round(sim_tfidf, 3),
        similarity_embedding=round(sim_embed, 3),
        component_breakdown=breakdown,
        top_matched_keywords=matched[:20],
        top_missing_keywords=missing[:25],
        radar_values=radar,
    )


# ----------------------------
# Radar chart rendering
# ----------------------------
def render_radar_png(radar_values: Dict[str, float]) -> bytes:
    labels = list(radar_values.keys())
    values = np.array(list(radar_values.values()), dtype=float)

    # close the loop
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    values = np.concatenate([values, values[:1]])
    angles = np.concatenate([angles, angles[:1]])

    fig = plt.figure(figsize=(5, 5), dpi=180)
    ax = plt.subplot(111, polar=True)

    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.2)

    ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels)
    ax.set_ylim(0, 1)

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


# ----------------------------
# PDF report rendering
# ----------------------------
def build_pdf_report(resume_text: str, job_text: str, result: FitResult) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    left = 0.75 * inch
    y = height - 0.8 * inch

    def line(txt: str, dy: float = 14):
        nonlocal y
        c.drawString(left, y, txt)
        y -= dy

    c.setFont("Helvetica-Bold", 16)
    line("Konfluence Resume Fit Report", dy=22)

    c.setFont("Helvetica", 11)
    line(f"Fit Score: {result.score}/100    Band: {result.band}")
    line(f"Semantic Similarity: {result.similarity_embedding}    TF-IDF Similarity: {result.similarity_tfidf}")
    line("")

    c.setFont("Helvetica-Bold", 12)
    line("Component Breakdown", dy=16)
    c.setFont("Helvetica", 11)
    for k, v in result.component_breakdown.items():
        line(f"- {k}: {v}")

    line("")
    c.setFont("Helvetica-Bold", 12)
    line("Must-haves", dy=16)
    c.setFont("Helvetica", 11)
    line("Present: " + (", ".join(result.must_have_present) if result.must_have_present else "None"))
    line("Missing: " + (", ".join(result.must_have_missing) if result.must_have_missing else "None"))

    line("")
    c.setFont("Helvetica-Bold", 12)
    line("Top Matched Keywords (sample)", dy=16)
    c.setFont("Helvetica", 11)
    line(", ".join(result.top_matched_keywords) if result.top_matched_keywords else "None")

    line("")
    c.setFont("Helvetica-Bold", 12)
    line("Top Missing Keywords to Add (truthfully)", dy=16)
    c.setFont("Helvetica", 11)
    # Wrap long line a bit
    missing = result.top_missing_keywords or []
    chunk = []
    cur = ""
    for k in missing:
        add = (", " if cur else "") + k
        if len(cur) + len(add) > 90:
            chunk.append(cur)
            cur = k
        else:
            cur += add
    if cur:
        chunk.append(cur)
    for s in chunk[:6]:
        line(s)

    # Add radar chart image
    radar_png = render_radar_png(result.radar_values)
    img_path = io.BytesIO(radar_png)

    # reportlab needs a filename-like object; we can use ImageReader
    from reportlab.lib.utils import ImageReader
    ir = ImageReader(img_path)
    c.drawImage(ir, left, 1.2 * inch, width=3.0 * inch, height=3.0 * inch, preserveAspectRatio=True, mask="auto")

    c.showPage()
    c.save()
    return buf.getvalue()


def result_to_dict(result: FitResult) -> Dict[str, Any]:
    return asdict(result)