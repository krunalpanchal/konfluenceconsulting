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
