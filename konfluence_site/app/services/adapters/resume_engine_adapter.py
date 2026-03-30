from dataclasses import asdict, is_dataclass
from app.engines.fit_engine import evaluate_fit, build_pdf_report, render_radar_png

def run_resume_engine(resume_text: str, job_description: str, use_auto_must_haves: bool = True) -> dict:
    result = evaluate_fit(
        resume_text=resume_text,
        job_text=job_description,
        use_auto_must_haves=use_auto_must_haves,
    )
    return asdict(result) if is_dataclass(result) else dict(result)

def build_resume_pdf(resume_text: str, job_description: str) -> bytes:
    result = evaluate_fit(
        resume_text=resume_text,
        job_text=job_description,
        use_auto_must_haves=True,
    )
    return build_pdf_report(resume_text, job_description, result)

def build_radar_png_from_result(result_dict: dict) -> bytes:
    return render_radar_png(result_dict.get("radar_values", {}))
