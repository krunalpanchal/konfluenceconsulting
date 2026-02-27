"""
KONFLUENCE CONSULTING - Static Website Generator (Python) [FIXED + COMPLETE]

Fixes vs your current script:
- Generates ALL NAV pages (Solutions + Technology were missing)
- Proper favicon placement (inside <head>)
- Converts logo.jfif -> konfluence_site/assets/logo.png (correct path)
- Removes broken HTML inside CSS (footer__brand bug)
- Writes resume_checker.js automatically
- Adds missing CSS utilities (container/section/badges/hero grid)
- Uses real domain in sitemap.xml

How to run:
1) Ensure logo.jfif is in the same folder as this script
2) pip install pillow
3) python build_site.py
4) Open konfluence_site/index.html
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

SITE_DIR = Path("konfluence_site")
ASSETS_DIR = SITE_DIR / "assets"
PAGES_DIR = SITE_DIR  # keep pages in root for simpler hosting

LOGO_INPUT = Path("logo.jfif")
LOGO_OUTPUT = ASSETS_DIR / "logo.png"

SITE_URL = "https://konfluenceconsulting.com"  # <-- your real domain


BRAND = {
    "name": "KONFLUENCE CONSULTING",
    "tagline": "White-glove hiring + workforce solutions.",
    # Brand palette based on your logo
    "bg": "#FFFDF0",
    "muted_bg": "#F7F3E6",
    "primary": "#0A0A0A",
    "text": "#0A0A0A",
    "muted_text": "#3F3F3F",
    "border": "#E6E1D0",
    "accent": "#0A0A0A",
}

NAV = [
    ("Home", "index.html"),
    ("Solutions", "solutions.html"),
    ("Resume Checker", "resume-checker.html"),
    ("For Companies", "companies.html"),
    ("For Talent", "talent.html"),
    ("Technology", "technology.html"),
    ("About", "about.html"),
    ("Contact", "contact.html"),
]


def ensure_dirs() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"✅ Wrote {path}")


def convert_logo() -> None:
    """
    Convert logo.jfif -> assets/logo.png
    Requires Pillow: pip install pillow
    """
    if not LOGO_INPUT.exists():
        raise FileNotFoundError(
            f"Logo file not found: {LOGO_INPUT.resolve()}\n"
            f"Place 'logo.jfif' next to build_site.py."
        )

    try:
        from PIL import Image  # type: ignore
        Image.open(LOGO_INPUT).save(LOGO_OUTPUT, format="PNG")
        print(f"✅ Saved {LOGO_OUTPUT}")
    except Exception as e:
        raise RuntimeError(
            f"Could not convert logo. Install Pillow: pip install pillow\nError: {e}"
        )


def nav_html(active_href: str) -> str:
    links = []
    for label, href in NAV:
        cls = "nav__link"
        if href == active_href:
            cls += " nav__link--active"
        links.append(f'<a class="{cls}" href="{href}">{label}</a>')
    return "\n".join(links)


def base_html(title: str, active_href: str, body: str, description: str = "") -> str:
    meta_desc = description or (
        "KONFLUENCE CONSULTING connects asset management firms and startups "
        "with premium talent, outsourcing partners, and executive leadership."
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title} | {BRAND["name"]}</title>
  <meta name="description" content="{meta_desc}" />
  <link rel="stylesheet" href="assets/styles.css" />
  <link rel="icon" href="assets/logo.png" />
</head>
<body>
  <header class="header">
    <div class="container header__inner">
      <a class="brand" href="index.html" aria-label="{BRAND["name"]} home">
        <img class="brand__logo" src="assets/logo.png" alt="KC logo" />
        <div class="brand__stack">
          <div class="brand__name">{BRAND["name"]}</div>
          <div class="brand__tagline">{BRAND["tagline"]}</div>
        </div>
      </a>

      <nav class="nav">
        {nav_html(active_href)}
        <a class="btn btn--primary nav__cta" href="contact.html">Book a Discovery Call</a>
      </nav>

      <button class="nav__toggle" aria-label="Open menu" onclick="toggleMenu()">☰</button>
    </div>

    <div class="nav__mobile" id="mobileNav">
      <div class="container nav__mobileInner">
        {nav_html(active_href)}
        <a class="btn btn--primary" href="contact.html">Book a Discovery Call</a>
      </div>
    </div>
  </header>

  <main>
    {body}
  </main>

  <footer class="footer">
    <div class="container footer__inner">
      <div class="footer__left">
        <div class="footer__brandRow">
          <img src="assets/logo.png" alt="KC logo" class="footer__logo" />
          <div class="footer__brand">{BRAND["name"]}</div>
        </div>
        <div class="footer__muted">© {datetime.now().year} {BRAND["name"]}. All rights reserved.</div>
      </div>

      <div class="footer__right">
        <a class="footer__link" href="privacy.html">Privacy</a>
        <a class="footer__link" href="terms.html">Terms</a>
        <a class="footer__link" href="contact.html">Contact</a>
      </div>
    </div>
  </footer>

  <script src="assets/main.js"></script>
</body>
</html>
"""


def styles_css() -> str:
    return f"""
:root{{
  --primary: {BRAND["primary"]};
  --accent: {BRAND["accent"]};
  --bg: {BRAND["bg"]};
  --muted-bg: {BRAND["muted_bg"]};
  --text: {BRAND["text"]};
  --muted: {BRAND["muted_text"]};
  --border: {BRAND["border"]};
  --radius: 16px;
  --shadow: 0 14px 40px rgba(0,0,0,0.08);
}}

*{{ box-sizing: border-box; }}
html, body {{
  margin: 0; padding: 0;
  font-family: ui-serif, Georgia, "Times New Roman", Times, serif;
  color: var(--text);
  background: var(--bg);
}}
a {{ color: inherit; text-decoration: none; }}
p {{ line-height: 1.7; }}

.container {{
  width: min(1120px, calc(100% - 40px));
  margin: 0 auto;
}}

.section {{ padding: 52px 0; }}
.section--muted {{
  background: var(--muted-bg);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}}

.header{{
  position: sticky; top: 0; z-index: 50;
  background: rgba(255,253,240,0.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
}}
.header__inner {{
  display:flex; align-items:center; justify-content:space-between;
  padding: 14px 0;
}}

.brand{{ display:flex; align-items:center; gap:12px; }}
.brand__logo{{ width:44px; height:44px; display:block; border-radius:10px; }}
.brand__name{{ font-weight: 900; letter-spacing: 0.2px; color: var(--primary); }}
.brand__tagline{{ font-size: 13px; color: var(--muted); margin-top: 2px; }}

.nav {{ display:flex; align-items:center; gap:14px; }}
.nav__link {{
  font-size: 14px;
  color: var(--muted);
  padding: 8px 10px;
  border-radius: 12px;
}}
.nav__link:hover {{ background: rgba(0,0,0,0.04); color: var(--primary); }}
.nav__link--active {{ background: rgba(0,0,0,0.06); color: var(--primary); font-weight: 900; }}

.nav__toggle {{
  display:none;
  border: 1px solid var(--border);
  background: var(--bg);
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 16px;
}}
.nav__mobile {{ display:none; border-top: 1px solid var(--border); background: var(--bg); }}
.nav__mobileInner {{ padding: 16px 0; display:grid; gap:10px; }}
.nav__mobile.show {{ display:block; }}

.btn{{
  display:inline-flex; align-items:center; justify-content:center;
  padding: 11px 14px;
  border-radius: 12px;
  font-weight: 800;
  font-size: 14px;
  border: 1px solid var(--border);
  background: var(--bg);
}}
.btn--primary{{
  background: var(--primary);
  color: var(--bg);
  border-color: var(--primary);
  box-shadow: 0 12px 26px rgba(0,0,0,0.18);
  transition: transform .12s ease, box-shadow .12s ease, filter .12s ease;
}}
.btn--primary:hover{{
  transform: translateY(-1px);
  box-shadow: 0 16px 32px rgba(0,0,0,0.22);
  filter: brightness(0.98);
}}

.hero{{
  padding: 70px 0 40px;
  background:
    radial-gradient(900px 400px at 20% 0%, rgba(0,0,0,0.06), transparent),
    radial-gradient(700px 320px at 85% 10%, rgba(0,0,0,0.04), transparent);
}}
.hero__grid {{
  display:grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 22px;
  align-items: start;
}}

.kicker {{
  font-size: 12px;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  font-weight: 900;
  color: var(--muted);
}}
.h1 {{ font-size: 44px; margin: 10px 0 10px; color: var(--primary); line-height: 1.08; }}
.lead {{ font-size: 18px; color: var(--muted); margin: 0 0 18px; }}
.hero__cta {{ display:flex; gap:12px; flex-wrap:wrap; margin-top: 12px; }}

.badge {{
  display:inline-flex; align-items:center;
  background: rgba(0,0,0,0.04);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 8px 12px;
  font-size: 13px;
  color: var(--muted);
}}

.card{{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 18px;
}}

.h2 {{ font-size: 28px; margin: 0 0 12px; color: var(--primary); }}
.sub {{ color: var(--muted); margin: 0 0 18px; }}

.grid3 {{ display:grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
.grid2 {{ display:grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}

.list {{ margin: 0; padding-left: 18px; color: var(--muted); }}
.list li {{ margin: 8px 0; }}

.form {{ display:grid; gap: 12px; }}
.input {{
  width: 100%;
  padding: 12px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  outline: none;
  background: var(--bg);
}}
textarea.input {{ min-height: 120px; resize: vertical; }}
.small {{ font-size: 13px; color: var(--muted); }}

.ctaBar {{
  display:flex; align-items:center; justify-content:space-between; gap: 16px;
  padding: 18px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--bg);
  box-shadow: var(--shadow);
}}
.ctaBar__left .h3 {{ margin: 0; font-size: 18px; color: var(--primary); font-weight: 900; }}
.ctaBar__left .muted {{ margin: 6px 0 0; color: var(--muted); }}

.footer {{
  padding: 24px 0;
  border-top: 1px solid var(--border);
  background: var(--bg);
}}
.footer__inner {{ display:flex; align-items:center; justify-content:space-between; gap: 16px; flex-wrap: wrap; }}
.footer__brandRow {{ display:flex; align-items:center; gap:10px; }}
.footer__logo {{ width: 28px; height: 28px; border-radius: 8px; }}
.footer__brand {{ font-weight: 900; }}
.footer__muted {{ font-size: 13px; color: var(--muted); }}
.footer__right {{ display:flex; gap: 14px; }}
.footer__link {{ font-size: 13px; color: var(--muted); }}
.footer__link:hover {{ color: var(--primary); }}

@media (max-width: 900px) {{
  .hero__grid {{ grid-template-columns: 1fr; }}
  .h1 {{ font-size: 38px; }}
  .grid3 {{ grid-template-columns: 1fr; }}
  .grid2 {{ grid-template-columns: 1fr; }}
  .nav {{ display: none; }}
  .nav__toggle {{ display: inline-flex; }}
}}
""".strip() + "\n"


def main_js() -> str:
    return """
function toggleMenu(){
  const el = document.getElementById('mobileNav');
  if(!el) return;
  el.classList.toggle('show');
}
""".strip() + "\n"


def resume_checker_js() -> str:
    # client-side heuristic resume checker (no backend)
    return r"""
const ACTION_VERBS = [
  "led","managed","built","delivered","implemented","designed","owned","optimized","reduced","increased",
  "launched","migrated","automated","improved","analyzed","created","developed","partnered","drove",
  "streamlined","executed","scaled","architected","coordinated","facilitated","negotiated"
];

const COMMON_SECTIONS = [
  { key: "summary", patterns: [/summary/i, /professional summary/i, /profile/i] },
  { key: "skills", patterns: [/skills/i, /core competencies/i, /technical skills/i] },
  { key: "experience", patterns: [/experience/i, /work experience/i, /professional experience/i] },
  { key: "education", patterns: [/education/i] },
];

function $(id){ return document.getElementById(id); }

async function extractTextFromFile(file){
  const name = file.name.toLowerCase();
  const buf = await file.arrayBuffer();

  if(name.endsWith(".txt")){
    return new TextDecoder("utf-8").decode(buf);
  }

  if(name.endsWith(".docx")){
    const result = await window.mammoth.extractRawText({ arrayBuffer: buf });
    return result.value || "";
  }

  if(name.endsWith(".pdf")){
    const pdfjsLib = window["pdfjs-dist/build/pdf"];
    pdfjsLib.GlobalWorkerOptions.workerSrc =
      "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.2.67/pdf.worker.min.js";

    const pdf = await pdfjsLib.getDocument({ data: buf }).promise;
    let text = "";
    for(let i=1; i<=pdf.numPages; i++){
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      const strings = content.items.map(it => it.str);
      text += strings.join(" ") + "\n";
    }
    return text;
  }

  throw new Error("Unsupported file type. Please upload PDF, DOCX, or TXT.");
}

function normalize(text){
  return (text || "")
    .replace(/\u00a0/g, " ")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function wordCount(text){
  return text.split(/\s+/).filter(Boolean).length;
}

function estimatePages(words){
  return Math.max(1, Math.round(words / 500));
}

function findSections(text){
  const found = {};
  for(const s of COMMON_SECTIONS){
    found[s.key] = s.patterns.some(r => r.test(text));
  }
  return found;
}

function countMetrics(text){
  const matches = text.match(/(\$?\d[\d,]*\.?\d*\s?(%|x|X|bps|M|MM|B|K)?)\b/g);
  return matches ? matches.length : 0;
}

function countActionVerbs(text){
  const lower = text.toLowerCase();
  let count = 0;
  for(const v of ACTION_VERBS){
    const re = new RegExp("\\b" + v + "\\b", "g");
    const m = lower.match(re);
    if(m) count += m.length;
  }
  return count;
}

function atsRiskFlags(text){
  const flags = [];
  const lower = text.toLowerCase();

  if(/references available/i.test(lower)) flags.push("Remove “References available upon request” (wastes space).");
  if(/\bobjective\b/i.test(text)) flags.push("Replace Objective with a modern Summary.");
  if(/table of contents/i.test(text)) flags.push("Avoid Table of Contents (ATS may misread).");

  const weird = (text.match(/[•●▪■◆]/g) || []).length;
  if(weird > 80) flags.push("Too many special bullets; use simple bullets consistently.");

  return flags;
}

function keywordCoverage(text, targetRole, targetIndustry){
  const tokens = new Set((text.toLowerCase().match(/[a-z][a-z+\-#]{2,}/g) || []));
  const wanted = [];

  if(targetRole) wanted.push(...targetRole.toLowerCase().split(/\s+/));
  if(targetIndustry) wanted.push(...targetIndustry.toLowerCase().split(/\s+/));

  wanted.push("stakeholder","roadmap","requirements","agile","scrum","jira","testing","qa","automation","python","sql","api","cloud","devops","risk");

  let hit = 0;
  for(const w of wanted){
    if(w.length < 3) continue;
    if(tokens.has(w)) hit++;
  }
  const score = Math.round((hit / Math.max(10, wanted.length)) * 100);
  return { score: Math.min(100, score), hits: hit, total: wanted.length };
}

function scoreResume(text, targetRole, targetIndustry){
  const fixes = [];
  const strengths = [];

  const words = wordCount(text);
  const pages = estimatePages(words);

  const sections = findSections(text);
  const metrics = countMetrics(text);
  const verbs = countActionVerbs(text);
  const flags = atsRiskFlags(text);
  const kw = keywordCoverage(text, targetRole, targetIndustry);

  if(!sections.summary) fixes.push("Add a 3–5 line Summary with role + domain + measurable impact.");
  else strengths.push("Summary section detected.");

  if(!sections.skills) fixes.push("Add a Skills/Core Competencies section with 12–18 keywords.");
  else strengths.push("Skills section detected.");

  if(!sections.experience) fixes.push("Ensure your Experience section is clearly labeled and easy for ATS.");
  else strengths.push("Experience section detected.");

  if(!sections.education) fixes.push("Add Education (even if brief).");
  else strengths.push("Education section detected.");

  if(words < 350) fixes.push("Resume feels thin. Add impact bullets and key projects (aim 500–900 words).");
  if(words > 1100) fixes.push("Resume may be too long. Tighten to strongest bullets (aim 1–2 pages).");
  if(pages > 2) fixes.push("Try to keep to 1–2 pages unless you’re applying to senior/academic CV contexts.");

  if(metrics < 6) fixes.push("Add more quantified outcomes (%, $, time saved, scale, risk reduced).");
  else strengths.push("Good use of measurable outcomes.");

  if(verbs < 12) fixes.push("Start bullets with strong action verbs (Led, Delivered, Implemented, Reduced…).");
  else strengths.push("Good action verb density.");

  for(const f of flags) fixes.push(f);

  if(kw.score < 45) fixes.push("Increase keyword alignment for your target role/industry (skills + tools + domain terms).");
  else strengths.push("Decent keyword coverage for target role/industry.");

  let score = 100;
  score -= (fixes.length * 4);
  score -= metrics < 6 ? 10 : 0;
  score -= verbs < 12 ? 8 : 0;
  score -= kw.score < 45 ? 10 : 0;
  score = Math.max(0, Math.min(100, score));

  const ats = (sections.experience && sections.skills) ? "Good" : "Needs work";
  const length = `${pages} page est. (${words} words)`;

  const atsChecklist = [
    { ok: sections.summary, text: "Summary/Profile section present" },
    { ok: sections.skills, text: "Skills/Core Competencies present" },
    { ok: sections.experience, text: "Experience section clearly labeled" },
    { ok: sections.education, text: "Education present" },
    { ok: flags.length === 0, text: "No obvious ATS risk phrases found" },
  ];

  return { score, ats, length, fixes, strengths, atsChecklist, kw };
}

function renderResults(result, rawText){
  $("resultsCard").style.display = "block";
  $("scoreBadge").textContent = `Score: ${result.score}/100`;
  $("atsBadge").textContent = `ATS: ${result.ats}`;
  $("lengthBadge").textContent = `Length: ${result.length}`;

  const fixesList = $("fixesList");
  fixesList.innerHTML = "";
  result.fixes.slice(0, 10).forEach(x => {
    const li = document.createElement("li");
    li.textContent = x;
    fixesList.appendChild(li);
  });

  const strengthsList = $("strengthsList");
  strengthsList.innerHTML = "";
  result.strengths.slice(0, 10).forEach(x => {
    const li = document.createElement("li");
    li.textContent = x;
    strengthsList.appendChild(li);
  });

  const atsList = $("atsList");
  atsList.innerHTML = "";
  result.atsChecklist.forEach(item => {
    const li = document.createElement("li");
    li.textContent = `${item.ok ? "✅" : "⚠️"} ${item.text}`;
    atsList.appendChild(li);
  });

  $("rawText").textContent = rawText;
}

async function main(){
  const analyzeBtn = $("analyzeBtn");
  analyzeBtn.addEventListener("click", async () => {
    const file = $("resumeFile").files?.[0];
    const role = $("targetRole").value || "";
    const industry = $("targetIndustry").value || "";

    if(!file){
      $("statusText").textContent = "Please choose a resume file first.";
      return;
    }

    $("statusText").textContent = "Extracting text…";
    analyzeBtn.disabled = true;

    try{
      const text = normalize(await extractTextFromFile(file));
      if(!text || text.length < 80){
        throw new Error("Could not extract enough text. Try a different file (or a text-based PDF).");
      }

      $("statusText").textContent = "Analyzing…";
      const result = scoreResume(text, role, industry);

      $("statusText").textContent = `Done. Keyword coverage score: ${result.kw.score}/100`;
      renderResults(result, text);
    } catch(err){
      $("statusText").textContent = `Error: ${err.message || err}`;
    } finally{
      analyzeBtn.disabled = false;
    }
  });
}

document.addEventListener("DOMContentLoaded", main);
""".strip() + "\n"


# -----------------------------
# Page bodies
# -----------------------------

def home_body() -> str:
    return f"""
<section class="hero">
  <div class="container hero__grid">
    <div>
      <div class="kicker">Talent • Outsourcing • Executive Search</div>
      <h1 class="h1">Premium talent and strategic workforce solutions for growing companies.</h1>
      <p class="lead">
        {BRAND["name"]} connects asset management firms and startups with exceptional professionals,
        trusted outsourcing partners, and executive leadership — through one high-signal network.
      </p>
      <div class="hero__cta">
        <a class="btn btn--primary" href="contact.html">Book a Discovery Call</a>
        <a class="btn" href="resume-checker.html">Try Resume Checker</a>
      </div>
      <div style="margin-top:18px; display:flex; gap:10px; flex-wrap:wrap;">
        <span class="badge">Flat-fee FTE</span>
        <span class="badge">Retainer consulting & temp</span>
        <span class="badge">Temp-to-FTE conversion</span>
      </div>
    </div>

    <div class="card">
      <h3 class="card__title">Core roles we place</h3>
      <p class="card__text">Project Managers • Business Analysts • QA • Developers • Leaders</p>
      <div style="height:12px"></div>
      <h3 class="card__title">Industries</h3>
      <p class="card__text">Asset Management • Startups • Growth-stage Tech • Financial Services</p>
      <div style="height:12px"></div>
      <h3 class="card__title">What you get</h3>
      <ul class="list">
        <li>High-signal vetting (no resume flooding)</li>
        <li>Speed with rigor (structured scorecards)</li>
        <li>Options: hire, contract, or outsource</li>
      </ul>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="h2">What we do</h2>
    <p class="sub">We help teams scale intelligently — full-time hires, expert consultants, outsourcing partners, and executive leadership.</p>
    <div class="grid3">
      <div class="card">
        <h3 class="card__title">Direct Hire (Flat Fee)</h3>
        <p class="card__text">Curated candidates aligned to the role, culture, and outcomes.</p>
      </div>
      <div class="card">
        <h3 class="card__title">Consulting & Contract (Retainer)</h3>
        <p class="card__text">Specialists for delivery, transformation, and urgent coverage.</p>
      </div>
      <div class="card">
        <h3 class="card__title">Outsourcing Partnerships</h3>
        <p class="card__text">Matched delivery partners that are cost-efficient or more experienced than in-house teams.</p>
      </div>
    </div>
  </div>
</section>
""".strip()


def solutions_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:40px;">Solutions</h1>
    <p class="lead">Flexible engagement models: hire, contract, or outsource—based on speed, cost, and risk.</p>

    <div class="grid2">
      <div class="card">
        <h3 class="card__title">Flat-fee FTE placement</h3>
        <ul class="list">
          <li>Role calibration + shortlist delivery</li>
          <li>Interview coordination + offer support</li>
          <li>Best for: core roles and leaders</li>
        </ul>
      </div>

      <div class="card">
        <h3 class="card__title">Consulting / temporary (retainer)</h3>
        <ul class="list">
          <li>Project managers, BAs, QA, developers</li>
          <li>Timeboxed scopes and milestones</li>
          <li>Temp-to-FTE conversion supported</li>
        </ul>
      </div>

      <div class="card">
        <h3 class="card__title">Outsourcing partner matching</h3>
        <ul class="list">
          <li>Vetted partners with capability fit</li>
          <li>Cost-efficient or higher expertise than in-house</li>
          <li>Scorecards to reduce delivery risk</li>
        </ul>
      </div>

      <div class="card">
        <h3 class="card__title">Executive search</h3>
        <ul class="list">
          <li>Startup and SMB leadership hiring</li>
          <li>Structured assessment + close support</li>
          <li>Confidential searches supported</li>
        </ul>
      </div>
    </div>
  </div>
</section>
""".strip()


def technology_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:40px;">Technology</h1>
    <p class="lead">
      Our goal is consistent, scalable evaluation—so hiring decisions are faster, clearer, and more defensible.
    </p>

    <div class="grid2">
      <div class="card">
        <h3 class="card__title">Resume Checker</h3>
        <p class="card__text">
          A browser-based tool to check ATS structure, impact signals, and keyword alignment.
        </p>
        <div style="height:10px"></div>
        <a class="btn btn--primary" href="resume-checker.html">Open Resume Checker</a>
      </div>

      <div class="card">
        <h3 class="card__title">Structured scorecards</h3>
        <p class="card__text">
          Consistent criteria across candidates and outsourcing partners to reduce noise and improve selection quality.
        </p>
      </div>
    </div>
  </div>
</section>
""".strip()


def resume_checker_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:40px;">Resume Checker</h1>
    <p class="lead">
      Upload your resume (PDF/DOCX/TXT). Get an instant score and actionable fixes:
      ATS structure, clarity, impact, and keyword alignment.
    </p>

    <div class="grid2">
      <div class="card">
        <h3 class="card__title">Upload your resume</h3>
        <p class="small">Supported formats: .pdf, .docx, .txt</p>

        <div class="form">
          <input class="input" id="resumeFile" type="file" accept=".pdf,.docx,.txt" />
          <input class="input" id="targetRole" placeholder="Target role (optional) e.g., Project Manager, Business Analyst" />
          <input class="input" id="targetIndustry" placeholder="Target industry (optional) e.g., Asset Management, FinTech" />
          <button class="btn btn--primary" id="analyzeBtn" type="button">Analyze Resume</button>
          <p class="small" id="statusText"></p>
        </div>
      </div>

      <div class="card">
        <h3 class="card__title">What this checks</h3>
        <ul class="list">
          <li>ATS-safe formatting (sections, headings)</li>
          <li>Length and density (1–2 pages guidance)</li>
          <li>Impact signals (metrics + outcomes)</li>
          <li>Keyword coverage (skills + role alignment)</li>
          <li>Missing essentials (summary, skills, experience, education)</li>
        </ul>
        <p class="small">Runs in your browser (no server upload).</p>
      </div>
    </div>

    <div style="height:18px"></div>

    <div class="card" id="resultsCard" style="display:none;">
      <h3 class="card__title">Results</h3>

      <div style="display:flex; gap:14px; flex-wrap:wrap; margin: 10px 0 14px;">
        <span class="badge" id="scoreBadge">Score: —</span>
        <span class="badge" id="atsBadge">ATS: —</span>
        <span class="badge" id="lengthBadge">Length: —</span>
      </div>

      <div class="grid2">
        <div>
          <h3 class="card__title">Top fixes</h3>
          <ul class="list" id="fixesList"></ul>
        </div>
        <div>
          <h3 class="card__title">Strengths</h3>
          <ul class="list" id="strengthsList"></ul>
        </div>
      </div>

      <div style="height:14px"></div>

      <h3 class="card__title">ATS Checklist</h3>
      <ul class="list" id="atsList"></ul>

      <div style="height:14px"></div>

      <details>
        <summary class="small" style="cursor:pointer;">Show extracted text (debug)</summary>
        <pre id="rawText" style="white-space:pre-wrap; font-size:12px; border:1px solid var(--border); padding:12px; border-radius:12px; background: rgba(0,0,0,0.02);"></pre>
      </details>
    </div>
  </div>
</section>

<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.2.67/pdf.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mammoth/1.6.0/mammoth.browser.min.js"></script>
<script src="assets/resume_checker.js"></script>
""".strip()


def companies_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:40px;">For Companies</h1>
    <p class="lead">Workforce solutions designed for growth and efficiency.</p>

    <div class="grid2">
      <div class="card">
        <h3 class="card__title">Direct Hire Placement (Flat Fee FTE)</h3>
        <p class="card__text">We deliver vetted professionals aligned to technical needs, culture, and outcomes.</p>
        <ul class="list">
          <li>Role calibration + market insight</li>
          <li>Targeted sourcing + screening</li>
          <li>Scorecards + interview coordination</li>
          <li>Offer and closing support</li>
        </ul>
      </div>

      <div class="card">
        <h3 class="card__title">Consulting & Temporary Talent (Retainer)</h3>
        <p class="card__text">Specialized experts for critical projects and short-term needs.</p>
        <ul class="list">
          <li>Immediate delivery capacity</li>
          <li>Timeboxed scopes and milestones</li>
          <li>Clear communication and accountability</li>
        </ul>
        <p class="small"><strong>Temp-to-FTE:</strong> If you convert a consultant to full-time, a success conversion fee applies.</p>
      </div>
    </div>
  </div>
</section>
""".strip()


def talent_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:40px;">For Talent</h1>
    <p class="lead">Get connected to high-impact opportunities with asset management firms and high-growth startups.</p>

    <div class="grid2">
      <div class="card">
        <h3 class="card__title">What you can expect</h3>
        <ul class="list">
          <li>Curated roles (no mass blasting)</li>
          <li>Transparent communication</li>
          <li>Prep support for interviews</li>
          <li>Options: full-time, contract, and temp-to-FTE</li>
        </ul>
      </div>

      <div class="card">
        <h3 class="card__title">Roles we place</h3>
        <p class="card__text">Project Managers • Business Analysts • QA • Developers • Technical Leadership</p>
      </div>
    </div>
  </div>
</section>
""".strip()


def about_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:40px;">About</h1>
    <p class="lead">We create meaningful alignment between companies, talent, and global capability — enabling smarter scale.</p>

    <div class="grid2">
      <div class="card">
        <h3 class="card__title">Our mission</h3>
        <p class="card__text">
          To raise the signal-to-noise in hiring and delivery by connecting organizations to premium talent,
          trusted outsourcing partners, and executive leadership.
        </p>
      </div>
      <div class="card">
        <h3 class="card__title">What we believe</h3>
        <ul class="list">
          <li>Precision beats volume.</li>
          <li>Transparency wins trust.</li>
          <li>Partnership beats transactions.</li>
          <li>Workforce strategy drives outcomes.</li>
        </ul>
      </div>
    </div>
  </div>
</section>
""".strip()


def contact_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:40px;">Contact</h1>
    <p class="lead">Book a discovery call or send a message. We typically respond within 1 business day.</p>

    <div class="grid2">
      <div class="card">
        <h3 class="card__title">Book a call</h3>
        <p class="card__text">Add your Calendly link here when ready.</p>
        <a class="btn btn--primary" href="#">Add Calendly Link</a>
      </div>

      <div class="card">
        <h3 class="card__title">Send a message</h3>
        <p class="small"><strong>Option A (simple):</strong> Email us.</p>
        <a class="btn" href="mailto:info@konfluenceconsulting.com?subject=Discovery%20Call%20Request">Email info@konfluenceconsulting.com</a>

        <div style="height:14px"></div>

        <p class="small"><strong>Option B:</strong> Formspree (replace yourFormId).</p>
        <form class="form" action="https://formspree.io/f/yourFormId" method="POST">
          <input class="input" name="name" placeholder="Your name" required />
          <input class="input" name="company" placeholder="Company" />
          <input class="input" type="email" name="email" placeholder="Email" required />
          <input class="input" name="need" placeholder="Hiring need (FTE / Contract / Outsource / Exec)" />
          <textarea class="input" name="message" placeholder="Tell us what you're trying to solve..." required></textarea>
          <button class="btn btn--primary" type="submit">Send</button>
          <p class="small">Replace <code>yourFormId</code> with your real Formspree form ID.</p>
        </form>
      </div>
    </div>
  </div>
</section>
""".strip()


def privacy_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:40px;">Privacy Policy</h1>
    <div class="card">
      <p class="card__text">
        We collect information you submit via forms or email solely to respond to inquiries and provide services.
        We do not sell personal data. If you want your data removed, email us.
      </p>
    </div>
  </div>
</section>
""".strip()


def terms_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:40px;">Terms</h1>
    <div class="card">
      <p class="card__text">
        This website is provided for informational purposes. Engagements are governed by separate service agreements.
      </p>
    </div>
  </div>
</section>
""".strip()


def robots_txt() -> str:
    return f"""User-agent: *
Allow: /

Sitemap: {SITE_URL.rstrip("/")}/sitemap.xml
"""


def sitemap_xml(pages: list[str]) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d")
    urls = "\n".join(
        f"""  <url>
    <loc>{SITE_URL.rstrip("/")}/{p}</loc>
    <lastmod>{now}</lastmod>
  </url>"""
        for p in pages
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""


def build() -> None:
    ensure_dirs()
    convert_logo()

    # assets
    write_file(ASSETS_DIR / "styles.css", styles_css())
    write_file(ASSETS_DIR / "main.js", main_js())
    write_file(ASSETS_DIR / "resume_checker.js", resume_checker_js())

    # pages
    pages = {
        "index.html": base_html("Home", "index.html", home_body()),
        "solutions.html": base_html("Solutions", "solutions.html", solutions_body()),
        "resume-checker.html": base_html("Resume Checker", "resume-checker.html", resume_checker_body()),
        "companies.html": base_html("For Companies", "companies.html", companies_body()),
        "talent.html": base_html("For Talent", "talent.html", talent_body()),
        "technology.html": base_html("Technology", "technology.html", technology_body()),
        "about.html": base_html("About", "about.html", about_body()),
        "contact.html": base_html("Contact", "contact.html", contact_body()),
        "privacy.html": base_html("Privacy", "privacy.html", privacy_body()),
        "terms.html": base_html("Terms", "terms.html", terms_body()),
    }

    for filename, html in pages.items():
        write_file(PAGES_DIR / filename, html)

    # SEO basics
    write_file(SITE_DIR / "robots.txt", robots_txt())
    write_file(SITE_DIR / "sitemap.xml", sitemap_xml(list(pages.keys())))

    # README
    readme = f"""# {BRAND["name"]} static site

Generated on {datetime.now().isoformat(timespec="seconds")}

## Run locally
python -m http.server 8000
Visit: http://localhost:8000

## Deploy
Upload contents of konfluence_site/ to Cloudflare Pages (Upload assets)

## Next edits
- Add Calendly link on Contact page
- Replace Formspree endpoint with your real form ID
"""
    write_file(SITE_DIR / "README.txt", readme)

    print("\n🎉 Done! Open konfluence_site/index.html")


if __name__ == "__main__":
    build()