"""
KONFLUENCE CONSULTING — Modern AI-Themed Website Generator

What it does:
- Builds a modern AI-themed static website in ./konfluence_site/
- Uses your attached logo.jfif and converts it to assets/logo.png
- Pages:
  - Home
  - Solutions
  - Resume Checker
  - For Companies
  - For Talent
  - Technology
  - About
  - Contact
  - Privacy
  - Terms
- Includes:
  - modern dark AI theme
  - glassmorphism cards
  - gradient glow backgrounds
  - business-case-aligned messaging
  - client-side resume checker
  - sitemap.xml + robots.txt

How to run:
1) Place logo.jfif next to this script
2) pip install pillow
3) python build_site.py
4) Open konfluence_site/index.html
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from PIL import Image

SITE_DIR = Path("konfluence_site")
ASSETS_DIR = SITE_DIR / "assets"
PAGES_DIR = SITE_DIR

LOGO_INPUT = Path("logo.jfif")
LOGO_OUTPUT = ASSETS_DIR / "logo.png"

SITE_URL = "https://konfluenceconsulting.com"

BRAND = {
    "name": "KONFLUENCE CONSULTING",
    "tagline": "AI-powered hiring, workforce intelligence, and delivery partnerships.",
    "bg": "#09090B",
    "bg_soft": "#111318",
    "panel": "rgba(255,255,255,0.06)",
    "panel_strong": "rgba(255,255,255,0.09)",
    "text": "#F5F7FA",
    "muted_text": "#B7C0CC",
    "border": "rgba(255,255,255,0.12)",
    "accent": "#7C3AED",
    "accent2": "#22D3EE",
    "accent3": "#A78BFA",
    "cream": "#FFFDF0",
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
    if not LOGO_INPUT.exists():
        raise FileNotFoundError(
            f"Missing logo file: {LOGO_INPUT.resolve()}\n"
            f"Place logo.jfif next to build_site.py."
        )
    Image.open(LOGO_INPUT).save(LOGO_OUTPUT, format="PNG")
    print(f"✅ Saved {LOGO_OUTPUT}")


def nav_html(active_href: str) -> str:
    items = []
    for label, href in NAV:
        cls = "nav__link"
        if href == active_href:
            cls += " nav__link--active"
        items.append(f'<a class="{cls}" href="{href}">{label}</a>')
    return "\n".join(items)


def base_html(title: str, active_href: str, body: str, description: str = "") -> str:
    meta_desc = description or (
        "KONFLUENCE CONSULTING provides AI-powered hiring, workforce intelligence, "
        "outsourcing partner matching, and resume analysis."
    )
    year = datetime.now().year

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
  <div class="siteGlow siteGlow--one"></div>
  <div class="siteGlow siteGlow--two"></div>

  <header class="header">
    <div class="container header__inner">
      <a class="brand" href="index.html" aria-label="{BRAND["name"]} home">
        <div class="brand__logoWrap">
          <img class="brand__logo" src="assets/logo.png" alt="KC logo" />
        </div>
        <div class="brand__stack">
          <div class="brand__name">{BRAND["name"]}</div>
          <div class="brand__tagline">{BRAND["tagline"]}</div>
        </div>
      </a>

      <nav class="nav">
        {nav_html(active_href)}
        <a class="btn btn--primary nav__cta" href="contact.html">Book a Demo Call</a>
      </nav>

      <button class="nav__toggle" aria-label="Open menu" onclick="toggleMenu()">☰</button>
    </div>

    <div class="nav__mobile" id="mobileNav">
      <div class="container nav__mobileInner">
        {nav_html(active_href)}
        <a class="btn btn--primary" href="contact.html">Book a Demo Call</a>
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
          <div class="footer__logoWrap">
            <img src="assets/logo.png" alt="KC logo" class="footer__logo" />
          </div>
          <div class="footer__brand">{BRAND["name"]}</div>
        </div>
        <div class="footer__muted">© {year} {BRAND["name"]}. AI-powered workforce intelligence.</div>
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
:root {{
  --bg: {BRAND["bg"]};
  --bg-soft: {BRAND["bg_soft"]};
  --panel: {BRAND["panel"]};
  --panel-strong: {BRAND["panel_strong"]};
  --text: {BRAND["text"]};
  --muted: {BRAND["muted_text"]};
  --border: {BRAND["border"]};
  --accent: {BRAND["accent"]};
  --accent2: {BRAND["accent2"]};
  --accent3: {BRAND["accent3"]};
  --cream: {BRAND["cream"]};
  --radius: 20px;
  --shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
}}

* {{ box-sizing: border-box; }}
html, body {{
  margin: 0;
  padding: 0;
  background:
    radial-gradient(circle at top left, rgba(124,58,237,0.18), transparent 25%),
    radial-gradient(circle at top right, rgba(34,211,238,0.10), transparent 30%),
    linear-gradient(180deg, #08090C 0%, #0B0D12 45%, #09090B 100%);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  min-height: 100%;
}}

body {{
  position: relative;
  overflow-x: hidden;
}}

a {{ color: inherit; text-decoration: none; }}
p {{ line-height: 1.7; }}

.container {{
  width: min(1180px, calc(100% - 40px));
  margin: 0 auto;
}}

.siteGlow {{
  position: fixed;
  inset: auto;
  border-radius: 999px;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
  opacity: 0.55;
}}
.siteGlow--one {{
  width: 280px;
  height: 280px;
  top: 100px;
  left: -60px;
  background: rgba(124,58,237,0.22);
}}
.siteGlow--two {{
  width: 320px;
  height: 320px;
  top: 220px;
  right: -90px;
  background: rgba(34,211,238,0.14);
}}

.header {{
  position: sticky;
  top: 0;
  z-index: 20;
  backdrop-filter: blur(20px);
  background: rgba(10, 10, 12, 0.65);
  border-bottom: 1px solid var(--border);
}}

.header__inner {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
}}

.brand {{
  display: flex;
  align-items: center;
  gap: 12px;
}}

.brand__logoWrap,
.footer__logoWrap {{
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(34,211,238,0.10));
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}}

.brand__logo {{
  width: 36px;
  height: 36px;
  object-fit: contain;
  border-radius: 10px;
  background: var(--cream);
}}

.brand__name {{
  font-weight: 900;
  letter-spacing: 0.03em;
  font-size: 15px;
}}

.brand__tagline {{
  font-size: 12px;
  color: var(--muted);
}}

.nav {{
  display: flex;
  align-items: center;
  gap: 10px;
}}

.nav__link {{
  font-size: 14px;
  color: var(--muted);
  padding: 10px 12px;
  border-radius: 12px;
  transition: .15s ease;
}}
.nav__link:hover {{
  color: var(--text);
  background: rgba(255,255,255,0.05);
}}
.nav__link--active {{
  color: var(--text);
  background: rgba(255,255,255,0.08);
  font-weight: 700;
}}

.nav__toggle {{
  display: none;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.05);
  color: var(--text);
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 16px;
}}

.nav__mobile {{
  display: none;
  border-top: 1px solid var(--border);
  background: rgba(11,13,18,0.95);
}}
.nav__mobileInner {{
  padding: 16px 0;
  display: grid;
  gap: 10px;
}}
.nav__mobile.show {{
  display: block;
}}

.btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 14px;
  font-weight: 700;
  font-size: 14px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.04);
  color: var(--text);
  transition: .15s ease;
}}
.btn:hover {{
  transform: translateY(-1px);
}}
.btn--primary {{
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: white;
  border-color: transparent;
  box-shadow: 0 18px 40px rgba(124,58,237,0.25);
}}
.btn--secondary {{
  background: rgba(255,255,255,0.04);
}}

.hero {{
  position: relative;
  z-index: 1;
  padding: 88px 0 40px;
}}
.hero__grid {{
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 24px;
  align-items: center;
}}

.kicker {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(167,139,250,0.25);
  background: rgba(124,58,237,0.10);
  color: #D9CCFF;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}

.h1 {{
  font-size: clamp(42px, 6vw, 68px);
  line-height: 1.02;
  margin: 18px 0 16px;
  font-weight: 900;
  letter-spacing: -0.03em;
}}

.gradientText {{
  background: linear-gradient(135deg, #FFFFFF 0%, #D4C7FF 40%, #A5F3FC 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}}

.lead {{
  font-size: 18px;
  color: var(--muted);
  margin: 0 0 20px;
  max-width: 760px;
}}

.hero__cta {{
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 20px;
}}

.badgeRow {{
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 22px;
}}

.badge {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 9px 13px;
  font-size: 13px;
  color: var(--muted);
}}

.section {{
  position: relative;
  z-index: 1;
  padding: 36px 0 68px;
}}

.h2 {{
  font-size: 32px;
  margin: 0 0 10px;
  font-weight: 850;
  letter-spacing: -0.02em;
}}

.sub {{
  color: var(--muted);
  margin: 0 0 22px;
  max-width: 820px;
}}

.grid2 {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px;
}}

.grid3 {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}}

.card {{
  background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.04));
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  backdrop-filter: blur(16px);
  padding: 22px;
}}

.card--feature {{
  position: relative;
  overflow: hidden;
}}
.card--feature::before {{
  content: "";
  position: absolute;
  inset: 0 auto auto 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
}}

.card__title {{
  font-size: 20px;
  font-weight: 800;
  margin: 0 0 10px;
}}

.card__text {{
  color: var(--muted);
  margin: 0;
}}

.metricGrid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}}

.metric {{
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px;
}}
.metric__value {{
  font-size: 28px;
  font-weight: 900;
  margin-bottom: 6px;
}}
.metric__label {{
  font-size: 13px;
  color: var(--muted);
}}

.list {{
  margin: 0;
  padding-left: 18px;
  color: var(--muted);
}}
.list li {{
  margin: 8px 0;
}}

.ctaBar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: linear-gradient(135deg, rgba(124,58,237,0.12), rgba(34,211,238,0.08));
  box-shadow: var(--shadow);
}}
.ctaBar__left .h3 {{
  margin: 0;
  font-size: 20px;
  font-weight: 850;
}}
.ctaBar__left .muted {{
  margin: 6px 0 0;
  color: var(--muted);
}}

.form {{
  display: grid;
  gap: 12px;
}}

.input {{
  width: 100%;
  padding: 13px 14px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.04);
  color: var(--text);
  outline: none;
}}
.input::placeholder {{
  color: #94A3B8;
}}
textarea.input {{
  min-height: 130px;
  resize: vertical;
}}

.small {{
  font-size: 13px;
  color: var(--muted);
}}

.footer {{
  position: relative;
  z-index: 1;
  padding: 30px 0;
  border-top: 1px solid var(--border);
  background: rgba(8,9,12,0.72);
}}
.footer__inner {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}}
.footer__brandRow {{
  display: flex;
  align-items: center;
  gap: 10px;
}}
.footer__logo {{
  width: 20px;
  height: 20px;
  object-fit: contain;
  border-radius: 6px;
  background: var(--cream);
}}
.footer__brand {{
  font-weight: 850;
}}
.footer__muted {{
  font-size: 13px;
  color: var(--muted);
}}
.footer__right {{
  display: flex;
  gap: 14px;
}}
.footer__link {{
  font-size: 13px;
  color: var(--muted);
}}
.footer__link:hover {{
  color: var(--text);
}}

@media (max-width: 960px) {{
  .hero__grid,
  .grid2,
  .grid3,
  .metricGrid {{
    grid-template-columns: 1fr;
  }}

  .nav {{
    display: none;
  }}

  .nav__toggle {{
    display: inline-flex;
  }}

  .h1 {{
    font-size: 42px;
  }}
}}
""".strip() + "\n"


def main_js() -> str:
    return """
function toggleMenu() {
  const el = document.getElementById('mobileNav');
  if (!el) return;
  el.classList.toggle('show');
}
""".strip() + "\n"


def resume_checker_js() -> str:
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
  const kw = keywordCoverage(text, targetRole, targetIndustry);

  if(!sections.summary) fixes.push("Add a 3–5 line Summary with role + domain + measurable impact.");
  else strengths.push("Summary section detected.");

  if(!sections.skills) fixes.push("Add a Skills/Core Competencies section with 12–18 keywords.");
  else strengths.push("Skills section detected.");

  if(!sections.experience) fixes.push("Ensure your Experience section is clearly labeled and ATS-friendly.");
  else strengths.push("Experience section detected.");

  if(!sections.education) fixes.push("Add Education (even if brief).");
  else strengths.push("Education section detected.");

  if(words < 350) fixes.push("Resume feels thin. Add impact bullets and key projects.");
  if(words > 1100) fixes.push("Resume may be too long. Tighten to strongest bullets.");
  if(metrics < 6) fixes.push("Add more quantified outcomes (%, $, time saved, scale, risk reduced).");
  else strengths.push("Good measurable outcomes.");
  if(verbs < 12) fixes.push("Use stronger action verbs at the start of bullets.");
  else strengths.push("Good action verb density.");
  if(kw.score < 45) fixes.push("Increase keyword alignment for your target role and industry.");
  else strengths.push("Decent keyword coverage.");

  let score = 100;
  score -= fixes.length * 4;
  score -= metrics < 6 ? 10 : 0;
  score -= verbs < 12 ? 8 : 0;
  score -= kw.score < 45 ? 10 : 0;
  score = Math.max(0, Math.min(100, score));

  const ats = (sections.experience && sections.skills) ? "Good" : "Needs work";
  const length = `${pages} page est. (${words} words)`;

  const atsChecklist = [
    { ok: sections.summary, text: "Summary/Profile section present" },
    { ok: sections.skills, text: "Skills/Core Competencies present" },
    { ok: sections.experience, text: "Experience clearly labeled" },
    { ok: sections.education, text: "Education present" }
  ];

  return { score, ats, length, fixes, strengths, atsChecklist };
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
        throw new Error("Could not extract enough text.");
      }

      $("statusText").textContent = "Analyzing…";
      const result = scoreResume(text, role, industry);
      $("statusText").textContent = "Done.";
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


def home_body() -> str:
    return f"""
<section class="hero">
  <div class="container hero__grid">
    <div>
      <div class="kicker">Powered by SOTA Intel</div>
      <h1 class="h1">
        <span class="gradientText">AI-powered hiring</span><br />
        workforce intelligence, and smarter delivery partnerships.
      </h1>
      <p class="lead">
        {BRAND["name"]} helps startups and asset management firms hire better, screen faster,
        and scale through vetted outsourcing partners. Our business model centers on AI-driven
        candidate vetting, scorecards, and technology integration into workforce processes.
      </p>
      <div class="hero__cta">
        <a class="btn btn--primary" href="contact.html">Book a Demo Call</a>
        <a class="btn btn--secondary" href="resume-checker.html">Try Resume Checker</a>
      </div>
      <div class="badgeRow">
        <span class="badge">AI Vetting</span>
        <span class="badge">Resume Intelligence</span>
        <span class="badge">Outsourcing Scorecards</span>
        <span class="badge">Executive Search</span>
      </div>
    </div>

    <div class="card card--feature">
      <div class="metricGrid">
        <div class="metric">
          <div class="metric__value">3</div>
          <div class="metric__label">Delivery models: hire, contract, outsource</div>
        </div>
        <div class="metric">
          <div class="metric__value">AI</div>
          <div class="metric__label">Candidate screening and validation support</div>
        </div>
        <div class="metric">
          <div class="metric__value">24/7</div>
          <div class="metric__label">Digital-first client acquisition and lead generation</div>
        </div>
      </div>
      <div style="height:18px"></div>
      <h3 class="card__title">Why this looks like an AI company</h3>
      <p class="card__text">
        Because the business case itself positions Konfluence as a futuristic workforce portal with
        SOTA Intel at the center of candidate vetting, HR platform integration, and long-term scalable service delivery.
      </p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="h2">Built for modern workforce decisions</h2>
    <p class="sub">
      The company is positioned around AI-powered talent search, outsourcing partner evaluation,
      and sustainable low-overhead service delivery rather than a traditional recruiter-heavy model.
    </p>

    <div class="grid3">
      <div class="card card--feature">
        <h3 class="card__title">AI Talent Search</h3>
        <p class="card__text">Filter and vet large candidate pools faster with consistent logic and stronger signal detection.</p>
      </div>
      <div class="card card--feature">
        <h3 class="card__title">Partner Scorecards</h3>
        <p class="card__text">Evaluate outsourcing firms by size, quality, expertise, and market reputation before engagement.</p>
      </div>
      <div class="card card--feature">
        <h3 class="card__title">Technology Integration</h3>
        <p class="card__text">Bring screening logic into HR workflows so applicant quality improves before manual review begins.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="ctaBar">
      <div class="ctaBar__left">
        <div class="h3">Want the site to feel even more like a SaaS product?</div>
        <p class="muted">Next upgrade: animated dashboard visuals, AI workflow timeline, and a job-description match analyzer.</p>
      </div>
      <a class="btn btn--primary" href="technology.html">View Technology</a>
    </div>
  </div>
</section>
""".strip()


def solutions_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:48px;">Solutions</h1>
    <p class="lead">AI-enhanced hiring and delivery models designed for speed, quality, and lower operational drag.</p>

    <div class="grid2">
      <div class="card card--feature">
        <h3 class="card__title">Flat-fee FTE hiring</h3>
        <ul class="list">
          <li>Role calibration and intake</li>
          <li>Curated shortlist delivery</li>
          <li>Interview coordination and close support</li>
        </ul>
      </div>
      <div class="card card--feature">
        <h3 class="card__title">Consulting and contingent talent</h3>
        <ul class="list">
          <li>Project managers, business analysts, QA, developers</li>
          <li>Fast coverage for delivery gaps</li>
          <li>Temp-to-FTE optional conversion</li>
        </ul>
      </div>
      <div class="card card--feature">
        <h3 class="card__title">Outsourcing partner matching</h3>
        <ul class="list">
          <li>IT helpdesk, development, call center, cloud, DevOps</li>
          <li>Hardware/software customization</li>
          <li>Business continuity, change management, cyber services</li>
        </ul>
      </div>
      <div class="card card--feature">
        <h3 class="card__title">Executive search</h3>
        <ul class="list">
          <li>Leadership hiring for startups and SMBs</li>
          <li>Confidential searches</li>
          <li>Structured assessment model</li>
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
    <h1 class="h1" style="font-size:48px;">Technology</h1>
    <p class="lead">
      SOTA Intel is the foundation of the platform vision: higher-quality applicant validation, partner scoring,
      and integration into HR workflows.
    </p>

    <div class="grid2">
      <div class="card card--feature">
        <h3 class="card__title">AI screening layer</h3>
        <p class="card__text">
          Designed to help vet large applicant pools with background checks, credential validation,
          reference support, and online presence screening.
        </p>
      </div>
      <div class="card card--feature">
        <h3 class="card__title">HR platform integration</h3>
        <p class="card__text">
          A subset of the screening logic can be embedded into organizations’ HR processes so incoming
          applications are filtered by predefined criteria before reaching the hiring team.
        </p>
      </div>
      <div class="card card--feature">
        <h3 class="card__title">Partner quality scorecards</h3>
        <p class="card__text">
          Offshore and onshore providers can be compared using a repeatable framework based on expertise,
          quality, size, and market credibility.
        </p>
      </div>
      <div class="card card--feature">
        <h3 class="card__title">Resume intelligence tools</h3>
        <p class="card__text">
          The site already includes a browser-based resume checker as the first visible AI utility.
        </p>
        <div style="height:14px"></div>
        <a class="btn btn--primary" href="resume-checker.html">Open Resume Checker</a>
      </div>
    </div>
  </div>
</section>
""".strip()


def resume_checker_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:48px;">Resume Checker</h1>
    <p class="lead">
      Upload your resume and get an instant AI-style quality review for ATS structure, keyword alignment,
      measurable impact, and role readiness.
    </p>

    <div class="grid2">
      <div class="card card--feature">
        <h3 class="card__title">Analyze your resume</h3>
        <div class="form">
          <input class="input" id="resumeFile" type="file" accept=".pdf,.docx,.txt" />
          <input class="input" id="targetRole" placeholder="Target role (optional)" />
          <input class="input" id="targetIndustry" placeholder="Target industry (optional)" />
          <button class="btn btn--primary" id="analyzeBtn" type="button">Run Analysis</button>
          <p class="small" id="statusText"></p>
        </div>
      </div>

      <div class="card card--feature">
        <h3 class="card__title">What it scores</h3>
        <ul class="list">
          <li>ATS-friendly structure</li>
          <li>Keyword coverage</li>
          <li>Use of metrics and quantified impact</li>
          <li>Action verb quality</li>
          <li>Missing sections and formatting gaps</li>
        </ul>
      </div>
    </div>

    <div style="height:18px"></div>

    <div class="card" id="resultsCard" style="display:none;">
      <h3 class="card__title">Analysis Results</h3>

      <div class="badgeRow">
        <span class="badge" id="scoreBadge">Score: —</span>
        <span class="badge" id="atsBadge">ATS: —</span>
        <span class="badge" id="lengthBadge">Length: —</span>
      </div>

      <div style="height:18px"></div>

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

      <div style="height:18px"></div>

      <h3 class="card__title">ATS Checklist</h3>
      <ul class="list" id="atsList"></ul>

      <div style="height:18px"></div>

      <details>
        <summary class="small" style="cursor:pointer;">Show extracted text</summary>
        <pre id="rawText" style="white-space:pre-wrap; font-size:12px; border:1px solid var(--border); padding:12px; border-radius:14px; background: rgba(255,255,255,0.03); color: var(--muted);"></pre>
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
    <h1 class="h1" style="font-size:48px;">For Companies</h1>
    <p class="lead">A modern workforce intelligence partner for hiring, delivery capacity, and outsourcing optimization.</p>

    <div class="grid2">
      <div class="card card--feature">
        <h3 class="card__title">Why companies use Konfluence</h3>
        <ul class="list">
          <li>Lower overhead than building a full recruiting engine</li>
          <li>Higher trust through screening and partner evaluation</li>
          <li>Flexible models for hiring, contingent delivery, and outsourcing</li>
        </ul>
      </div>
      <div class="card card--feature">
        <h3 class="card__title">Ideal buyers</h3>
        <ul class="list">
          <li>Asset managers modernizing delivery teams</li>
          <li>Startups hiring core technical and operational talent</li>
          <li>Organizations needing offshore/onshore support partners</li>
        </ul>
      </div>
    </div>
  </div>
</section>
""".strip()


def talent_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:48px;">For Talent</h1>
    <p class="lead">We represent candidates and delivery partners with clarity, measurable expectations, and active communication.</p>

    <div class="grid2">
      <div class="card card--feature">
        <h3 class="card__title">What you can expect</h3>
        <ul class="list">
          <li>Direct communication and clear engagement details</li>
          <li>Structured expectations and performance transparency</li>
          <li>Opportunities across startups and larger organizations</li>
        </ul>
      </div>
      <div class="card card--feature">
        <h3 class="card__title">Where you fit</h3>
        <p class="card__text">Project management, QA, cloud, DevOps, cyber, business analysis, and software delivery roles.</p>
      </div>
    </div>
  </div>
</section>
""".strip()


def about_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:48px;">About</h1>
    <p class="lead">
      Konfluence is built around a long-term vision: meaningful connections, scalable quality,
      technology integration, and sustainable service delivery.
    </p>

    <div class="grid2">
      <div class="card card--feature">
        <h3 class="card__title">Operational foundation</h3>
        <p class="card__text">
          The business case emphasizes combined experience across Fortune 500 environments, asset management,
          SaaS, quality assurance, cybersecurity, and data integrity initiatives.
        </p>
      </div>
      <div class="card card--feature">
        <h3 class="card__title">Future direction</h3>
        <p class="card__text">
          The long-term roadmap extends beyond asset management and cyber into supply chain,
          manufacturing, and import-export operations.
        </p>
      </div>
    </div>
  </div>
</section>
""".strip()


def contact_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:48px;">Contact</h1>
    <p class="lead">Book a demo call or send a message. We typically respond within 1 business day.</p>

    <div class="grid2">
      <div class="card card--feature">
        <h3 class="card__title">Book a call</h3>
        <p class="card__text">Add your Calendly link here when ready.</p>
        <div style="height:14px"></div>
        <a class="btn btn--primary" href="#">Add Calendly Link</a>
      </div>

      <div class="card card--feature">
        <h3 class="card__title">Send a message</h3>
        <form class="form" action="https://formspree.io/f/yourFormId" method="POST">
          <input class="input" name="name" placeholder="Your name" required />
          <input class="input" name="company" placeholder="Company" />
          <input class="input" type="email" name="email" placeholder="Email" required />
          <input class="input" name="need" placeholder="Need (Hiring / Resume Checker / Outsourcing / Exec Search)" />
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
    <h1 class="h1" style="font-size:44px;">Privacy Policy</h1>
    <div class="card">
      <p class="card__text">
        We collect information submitted through forms or email solely to respond to inquiries and provide services.
        We do not sell personal data.
      </p>
    </div>
  </div>
</section>
""".strip()


def terms_body() -> str:
    return """
<section class="section">
  <div class="container">
    <h1 class="h1" style="font-size:44px;">Terms</h1>
    <div class="card">
      <p class="card__text">
        This website is provided for informational purposes. Client engagements are governed by separate service agreements.
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

    write_file(ASSETS_DIR / "styles.css", styles_css())
    write_file(ASSETS_DIR / "main.js", main_js())
    write_file(ASSETS_DIR / "resume_checker.js", resume_checker_js())

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

    write_file(SITE_DIR / "robots.txt", robots_txt())
    write_file(SITE_DIR / "sitemap.xml", sitemap_xml(list(pages.keys())))

    readme = f"""# {BRAND["name"]} static site

Generated on {datetime.now().isoformat(timespec="seconds")}

## Run locally
python -m http.server 8000

Then visit:
http://localhost:8000

## Deploy
Upload contents of konfluence_site/ to Cloudflare Pages

## Notes
- Replace Formspree endpoint in contact.html
- Replace Calendly link in contact.html
"""
    write_file(SITE_DIR / "README.txt", readme)

    print("\\n🎉 Done! Open konfluence_site/index.html")


if __name__ == "__main__":
    build()