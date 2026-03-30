const API_BASE = "https://api.konfluenceconsulting.com";
const $ = (id) => document.getElementById(id);

function setText(id, value) {
  const node = $(id);
  if (node) node.textContent = value;
}
function showStatus(id, msg, error = false) {
  const node = $(id);
  if (!node) return;
  node.textContent = msg;
  node.style.color = error ? "#ffb3b3" : "";
}
function chips(items, cls = "good") {
  if (!items || !items.length) return '<span class="muted">None</span>';
  return items.map(x => `<span class="chip ${cls}">${x}</span>`).join("");
}
function linesToArray(text) {
  return text.split("\n").map(v => v.trim()).filter(Boolean);
}
async function checkHealth() {
  setText("api-base-url", API_BASE);
  setText("api-base-mini", "Live");
  showStatus("health-result", "Checking...");
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    setText("api-health-text", "API is live");
    setText("api-health-detail", `${API_BASE}/health responded successfully`);
    showStatus("health-result", `${data.status} · ${data.app || "API live"}`);
  } catch (e) {
    setText("api-health-text", "API check failed");
    setText("api-health-detail", "Verify tunnel, service, and CORS");
    showStatus("health-result", `Failed: ${e.message}`, true);
  }
}
async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`);
  return await res.json();
}
function renderResumeResults(data) {
  $("resume-results").classList.remove("hidden");
  setText("result-score", data.score);
  setText("result-band", data.band);
  setText("result-semantic", data.similarity_embedding);
  setText("result-tfidf", data.similarity_tfidf);
  $("must-have-present").innerHTML = chips(data.must_have_present, "good");
  $("must-have-missing").innerHTML = chips(data.must_have_missing, "warn");
  $("top-missing-keywords").innerHTML = chips(data.top_missing_keywords || [], "warn");
  const ul = $("component-breakdown");
  ul.innerHTML = "";
  Object.entries(data.component_breakdown || {}).forEach(([k, v]) => {
    const li = document.createElement("li");
    li.textContent = `${k}: ${v}`;
    ul.appendChild(li);
  });
  $("pdf-link").href = `${API_BASE}${data.pdf_download_path}`;
  $("radar-image").src = `${API_BASE}/api/analyses/${data.analysis_id}/radar.png`;
}
function renderJobResults(data) {
  $("job-results").classList.remove("hidden");
  setText("job-results-count", `${data.count} result(s)`);
  const list = $("job-results-list");
  list.innerHTML = "";
  (data.results || []).forEach(job => {
    const node = document.createElement("article");
    node.className = "job-card";
    node.innerHTML = `
      <h4>${job.title || "(missing title)"}</h4>
      <div class="job-meta">
        <span>${job.company || ""}</span>
        <span>${job.location || ""}</span>
        <span>${job.source || ""}</span>
        <span>Score: ${job.score}</span>
      </div>
      <p class="muted">${job.description_snippet || ""}</p>
      ${job.url ? `<p><a class="button button-secondary button-small" href="${job.url}" target="_blank" rel="noopener">Open Job</a></p>` : ""}
    `;
    list.appendChild(node);
  });
  if (!data.results || !data.results.length) {
    list.innerHTML = '<div class="muted">No results returned. Lower the minimum score, expand locations, or verify SERPAPI_KEY.</div>';
  }
}
document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  $("check-health-btn").addEventListener("click", checkHealth);

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) entry.target.classList.add("visible");
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));

  document.querySelectorAll(".tab").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      $(btn.dataset.tab).classList.add("active");
    });
  });

  $("resume-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    showStatus("resume-form-status", "Analyzing...");
    try {
      const data = await postJSON(`${API_BASE}/api/resume/analyze`, {
        candidate_name: $("candidate_name").value || null,
        resume_text: $("resume_text").value,
        job_description: $("job_description").value,
        use_auto_must_haves: $("use_auto_must_haves").value === "true"
      });
      renderResumeResults(data);
      showStatus("resume-form-status", "Analysis complete.");
    } catch (e) {
      showStatus("resume-form-status", `Failed: ${e.message}`, true);
    }
  });

  $("resume-upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    showStatus("resume-upload-status", "Uploading and analyzing...");
    try {
      const file = $("resume_file").files[0];
      if (!file) throw new Error("Please choose a file.");
      const fd = new FormData();
      fd.append("candidate_name", $("upload_candidate_name").value || "");
      fd.append("job_description", $("upload_job_description").value);
      fd.append("use_auto_must_haves", String($("upload_use_auto_must_haves").value === "true"));
      fd.append("resume_file", file);

      const res = await fetch(`${API_BASE}/api/resume/analyze-upload`, { method: "POST", body: fd });
      if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`);
      const data = await res.json();
      renderResumeResults(data);
      showStatus("resume-upload-status", "Analysis complete.");
    } catch (e) {
      showStatus("resume-upload-status", `Failed: ${e.message}`, true);
    }
  });

  $("job-search-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    showStatus("job-search-status", "Searching live jobs...");
    try {
      const data = await postJSON(`${API_BASE}/api/jobs/live-search`, {
        resume_text: $("job_resume_text").value,
        queries: linesToArray($("queries").value),
        locations: linesToArray($("locations").value),
        per_query_results: Number($("per_query_results").value || 10),
        min_score: Number($("min_score").value || 0.14),
        include_indeed_engine: $("include_indeed_engine").checked,
        use_embeddings: $("use_embeddings").value === "true",
        days_back: Number($("days_back").value || 14),
        save_results: $("save_results").checked
      });
      renderJobResults(data);
      showStatus("job-search-status", "Job search complete.");
    } catch (e) {
      showStatus("job-search-status", `Failed: ${e.message}`, true);
    }
  });
});
