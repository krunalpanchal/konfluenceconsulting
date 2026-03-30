from pydantic import BaseModel, Field
from typing import Optional

class JobCreate(BaseModel):
    external_id: Optional[str] = None
    title: str = Field(min_length=1)
    company: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    description: str = Field(min_length=1)
    employment_type: Optional[str] = None
    seniority: Optional[str] = None
    industry: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    source: Optional[str] = None
    score: Optional[float] = None

class JobRead(JobCreate):
    id: int
    model_config = {"from_attributes": True}

class JobSearchRequest(BaseModel):
    profile_text: str = Field(min_length=1)
    top_k: int = 10
    location: Optional[str] = None
    company: Optional[str] = None
    title_keywords: Optional[list[str]] = None

class RankedJob(BaseModel):
    job_id: int
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    score: float
    matched_terms: list[str] = []
    explanation: str
    url: Optional[str] = None

class LiveJobSearchRequest(BaseModel):
    resume_text: str = Field(min_length=1)
    queries: list[str]
    locations: list[str]
    per_query_results: int = 20
    min_score: float = 0.14
    include_indeed_engine: bool = True
    use_embeddings: bool = False
    days_back: int = 14
    save_results: bool = True
