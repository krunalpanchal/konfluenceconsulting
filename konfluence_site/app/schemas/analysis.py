from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class ResumeAnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=1)
    job_description: str = Field(min_length=1)
    candidate_name: Optional[str] = None
    use_auto_must_haves: bool = True

class ResumeAnalyzeResponse(BaseModel):
    analysis_id: int
    score: float
    band: str
    must_have_present: List[str]
    must_have_missing: List[str]
    similarity_tfidf: float
    similarity_embedding: float
    component_breakdown: Dict[str, float]
    top_matched_keywords: List[str]
    top_missing_keywords: List[str]
    radar_values: Dict[str, float]
    pdf_download_path: Optional[str] = None

class AnalysisRead(BaseModel):
    id: int
    candidate_name: Optional[str] = None
    source_filename: Optional[str] = None
    result_json: str
    model_config = {"from_attributes": True}
