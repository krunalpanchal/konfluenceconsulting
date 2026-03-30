import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.models.analysis import ResumeAnalysis
from app.schemas.job import JobCreate, JobRead, JobSearchRequest, RankedJob, LiveJobSearchRequest
from app.schemas.analysis import ResumeAnalyzeRequest, ResumeAnalyzeResponse, AnalysisRead
from app.services.adapters.resume_engine_adapter import run_resume_engine, build_resume_pdf, build_radar_png_from_result
from app.services.adapters.job_engine_adapter import rank_jobs_for_profile, run_live_job_search
from app.core.config import get_settings

router = APIRouter(prefix="/api", tags=["konfluence"])

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/resume/analyze", response_model=ResumeAnalyzeResponse)
def analyze_resume(payload: ResumeAnalyzeRequest, db: Session = Depends(get_db)):
    result = run_resume_engine(payload.resume_text, payload.job_description, payload.use_auto_must_haves)
    row = ResumeAnalysis(
        candidate_name=payload.candidate_name,
        source_filename=None,
        resume_text=payload.resume_text,
        job_description=payload.job_description,
        result_json=json.dumps(result),
    )
    db.add(row); db.commit(); db.refresh(row)
    result["analysis_id"] = row.id
    result["pdf_download_path"] = f"/api/analyses/{row.id}/report.pdf"
    return result

@router.post("/resume/analyze-upload", response_model=ResumeAnalyzeResponse)
async def analyze_resume_upload(
    job_description: str = Form(...),
    candidate_name: str | None = Form(default=None),
    use_auto_must_haves: bool = Form(default=True),
    resume_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    raw = await resume_file.read()
    resume_text = raw.decode("utf-8", errors="ignore")
    result = run_resume_engine(resume_text, job_description, use_auto_must_haves)
    row = ResumeAnalysis(
        candidate_name=candidate_name,
        source_filename=resume_file.filename,
        resume_text=resume_text,
        job_description=job_description,
        result_json=json.dumps(result),
    )
    db.add(row); db.commit(); db.refresh(row)
    result["analysis_id"] = row.id
    result["pdf_download_path"] = f"/api/analyses/{row.id}/report.pdf"
    return result

@router.get("/analyses/{analysis_id}", response_model=AnalysisRead)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    row = db.get(ResumeAnalysis, analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return row

@router.get("/analyses/{analysis_id}/report.pdf")
def get_analysis_pdf(analysis_id: int, db: Session = Depends(get_db)):
    row = db.get(ResumeAnalysis, analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    pdf_bytes = build_resume_pdf(row.resume_text, row.job_description)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f'inline; filename="konfluence_resume_fit_report_{analysis_id}.pdf"'})

@router.get("/analyses/{analysis_id}/radar.png")
def get_analysis_radar(analysis_id: int, db: Session = Depends(get_db)):
    row = db.get(ResumeAnalysis, analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    result = json.loads(row.result_json)
    png_bytes = build_radar_png_from_result(result)
    return Response(content=png_bytes, media_type="image/png")

@router.post("/jobs", response_model=JobRead)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    row = Job(**payload.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return row

@router.post("/jobs/bulk", response_model=list[JobRead])
def create_jobs_bulk(payload: list[JobCreate], db: Session = Depends(get_db)):
    rows = [Job(**item.model_dump()) for item in payload]
    db.add_all(rows); db.commit()
    for row in rows:
        db.refresh(row)
    return rows

@router.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)):
    row = db.get(Job, job_id)
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return row

@router.post("/jobs/search", response_model=list[RankedJob])
def search_jobs(payload: JobSearchRequest, db: Session = Depends(get_db)):
    query = db.query(Job)
    if payload.location:
        query = query.filter(Job.location.ilike(f"%{payload.location}%"))
    if payload.company:
        query = query.filter(Job.company.ilike(f"%{payload.company}%"))
    if payload.title_keywords:
        for keyword in payload.title_keywords:
            query = query.filter(Job.title.ilike(f"%{keyword}%"))
    jobs = query.all()
    job_docs = [{"id": job.id, "title": job.title, "company": job.company, "location": job.location, "description": job.description, "url": job.url} for job in jobs]
    return rank_jobs_for_profile(payload.profile_text, job_docs, payload.top_k)

@router.post("/jobs/live-search")
def live_search_jobs(payload: LiveJobSearchRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    if not settings.serpapi_key:
        raise HTTPException(status_code=400, detail="SERPAPI_KEY is not configured.")
    results = run_live_job_search(
        api_key=settings.serpapi_key,
        resume_text=payload.resume_text,
        queries=payload.queries,
        locations=payload.locations,
        per_query_results=payload.per_query_results,
        min_score=payload.min_score,
        include_indeed_engine=payload.include_indeed_engine,
        use_embeddings=payload.use_embeddings,
        days_back=payload.days_back,
    )
    if payload.save_results:
        for item in results:
            exists = db.query(Job).filter(Job.external_id == item.get("job_id")).first()
            if exists:
                continue
            row = Job(
                external_id=item.get("job_id"),
                title=item.get("title") or "(missing title)",
                company=item.get("company"),
                location=item.get("location"),
                url=item.get("url"),
                description=item.get("description_snippet", ""),
                source=item.get("source"),
                score=float(item.get("score", 0.0)),
            )
            db.add(row)
        db.commit()
    return {"count": len(results), "results": results}
