import os
import sys
import streamlit as st

# Ensure project root (Konfluence_Consulting) is on Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# MUST be the first Streamlit command:
st.set_page_config(page_title="Konfluence Resume Fit Analyzer", layout="wide")

# Import the shared engine from the package (NOT from fit_engine directly)
from konfluence_ai.fit_engine import evaluate_fit, build_pdf_report, render_radar_png


st.title("Konfluence Resume Fit Analyzer")
st.caption("Compare your resume vs a job description. Semantic AI matching + gaps + PDF report.")

with st.sidebar:
    st.subheader("Analysis Settings")
    use_auto = st.checkbox("Auto-detect must-haves from JD", value=True)
    min_chars = st.slider("Minimum text length required", 200, 3000, 600)
    st.divider()
    st.markdown("**Note:** For best results, paste plain text (resume + JD).")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Resume")
    resume_text = st.text_area("Paste resume text", height=340, placeholder="Paste your resume here...")

with col2:
    st.subheader("Job Description")
    job_text = st.text_area("Paste job description text", height=340, placeholder="Paste the job description here...")

run = st.button("Analyze Fit", type="primary")

if run:
    if len(resume_text.strip()) < min_chars or len(job_text.strip()) < min_chars:
        st.error("Please paste more complete text for both Resume and Job Description.")
        st.stop()

    result = evaluate_fit(resume_text, job_text, use_auto_must_haves=use_auto)

    st.divider()
    a, b, c = st.columns([1, 1, 2])
    with a:
        st.metric("Fit Score", f"{result.score}/100")
    with b:
        st.metric("Fit Band", result.band)
    with c:
        st.write("**Component Breakdown**")
        for k, v in result.component_breakdown.items():
            st.write(f"- {k}: **{v}**")

    st.divider()
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Must-haves")
        st.write("✅ Present:", ", ".join(result.must_have_present) if result.must_have_present else "None")
        st.write("❌ Missing:", ", ".join(result.must_have_missing) if result.must_have_missing else "None")

        st.subheader("Top matched keywords (sample)")
        st.write(", ".join(result.top_matched_keywords) if result.top_matched_keywords else "None detected")

    with c2:
        st.subheader("Top missing keywords to add (truthfully)")
        st.write(", ".join(result.top_missing_keywords) if result.top_missing_keywords else "None detected")

        st.subheader("Similarity signals")
        st.write(f"Semantic (embeddings): **{result.similarity_embedding}**")
        st.write(f"TF-IDF: **{result.similarity_tfidf}**")

    st.divider()
    st.subheader("Fit Radar")
    radar_png = render_radar_png(result.radar_values)
    st.image(radar_png, use_container_width=False)

    st.divider()
    st.subheader("Download Report")
    pdf_bytes = build_pdf_report(resume_text, job_text, result)
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name="konfluence_resume_fit_report.pdf",
        mime="application/pdf",
        type="primary",
    )