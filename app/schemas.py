from typing import List, Optional, Any
from pydantic import BaseModel, Field
class PatientCreate(BaseModel):
    patient_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    disease: Optional[str] = None
    medication: Optional[str] = None
    medical_history: Optional[str] = None
class TrialCreate(BaseModel):
    title: str
    disease: str
    description: Optional[str] = None
    inclusion_criteria: Optional[str] = None
    exclusion_criteria: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    status: Optional[str] = "recruiting"


class TrialResponse(TrialCreate):
    id: int

    class Config:
        from_attributes = True


class MatchRequest(BaseModel):
    patient_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    disease: Optional[str] = None
    medication: Optional[str] = None
    medical_history: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


class TrialMatch(BaseModel):
    trial_id: Optional[int] = None
    title: str
    disease: str
    eligible: bool
    match_score: int
    reason: str
    recommendation: str


class MatchResponse(BaseModel):
    patient: PatientCreate
    retrieved_trials: List[TrialMatch]
    best_match: Optional[TrialMatch] = None


class ReportRequest(BaseModel):
    patient: PatientCreate
    match_result: MatchResponse


class EHRExtractionResponse(BaseModel):
    raw_text_preview: str
    extracted: dict[str, Any]
