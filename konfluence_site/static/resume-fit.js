// If you deploy API + site together (same domain), keep API_BASE empty.
const API_BASE = ""; // e.g. "https://api.konfluenceconsulting.com" if separate

const $ = (id) => document.getElementById(id);

function setStatus(msg, isError=false) {
  const el = $("status");
  el.textContent = msg || "";
  el.className = isError ? "status error" : "status";
}

function pill(container, items) {
  container.innerHTML = "";
  (items || []).forEach(t => {
    const s = document.createElement("span");
    s.className = "pill";
    s.textContent = t;
    container.appendChild(s);
  });
}

function downloadBase64Pdf(b64, filename="konfluence_resume_fit_report.pdf") {
  const a = document.createElement("a");
  a.href = "data:application/pdf;base64," + b64;
  a.download = filename;
  a.click();
}

$("analyzeBtn").onclick = async () => {
  const resume = $("resume").value;
  const job = $("job").value;
  const auto_must_haves = $("autoMust").checked;
  const pdf = $("wantPdf").checked;

  $("downloadPdfBtn").disabled = true;

  if (resume.trim().length < 200 || job.trim().length < 200) {
    setStatus("Please paste at least ~200 characters in both fields.", true);
    return;
  }

  setStatus("Analyzing…");

  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ resume, job, auto_must_haves, pdf })
    });

    const data = await res.json();
    if (!res.ok) {
      setStatus(data.error || "Analyze failed.", true);
      return;
    }

    const r = data.result;

    $("score").textContent = `${r.score}/100`;
    $("band").textContent = r.band;
    $("semSim").textContent = r.similarity_embedding;
    $("tfidfSim").textContent = r.similarity_tfidf;

    $("mustPresent").textContent = (r.must_have_present || []).join(", ") || "None";
    $("mustMissing").textContent = (r.must_have_missing || []).join(", ") || "None";

    // Fetch radar PNG from API
    const radarRes = await fetch(`${API_BASE}/radar.png`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ radar_values: r.radar_values })
    });
    const blob = await radarRes.blob();
    $("radarImg").src = URL.createObjectURL(blob);

    // Breakdown
    $("breakdown").innerHTML = "";
    Object.entries(r.component_breakdown || {}).forEach(([k,v]) => {
      const li = document.createElement("li");
      li.textContent = `${k}: ${v}`;
      $("breakdown").appendChild(li);
    });

    pill($("matched"), r.top_matched_keywords || []);
    pill($("missing"), r.top_missing_keywords || []);

    // Radar (we can generate client-side OR reuse engine output)
    // Here we ask the engine to generate radar only through the Streamlit UI,
    // but since you already have render_radar_png() on the engine, easiest is:
    // We'll generate a radar image client-side later if you want.
    // For now: just show a placeholder message.
    $("radarImg").src =
      "data:image/svg+xml;charset=utf-8," +
      encodeURIComponent(`<svg xmlns='http://www.w3.org/2000/svg' width='500' height='300'>
        <rect width='100%' height='100%' fill='#0b1020'/>
        <text x='20' y='60' fill='#e5e7eb' font-size='20'>Radar is available in Streamlit UI</text>
        <text x='20' y='100' fill='#9ca3af' font-size='14'>Want it on this page too? Tell me and I’ll add /radar.png endpoint.</text>
      </svg>`);

    if (data.pdf_base64) {
      $("downloadPdfBtn").disabled = false;
      $("downloadPdfBtn").onclick = () => downloadBase64Pdf(data.pdf_base64);
    }

    setStatus("Done.");
  } catch (e) {
    setStatus(String(e), true);
  }
};