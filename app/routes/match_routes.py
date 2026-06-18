from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.matcher_service import match_patient_to_trials
from app.schemas import MatchRequest, MatchResponse

router = APIRouter(prefix="", tags=["Matching"])


@router.post("/match-patient", response_model=MatchResponse)
def match_patient(payload: MatchRequest, db: Session = Depends(get_db)):
    patient = payload.model_dump(exclude={"top_k"})
    result = match_patient_to_trials(db, patient, top_k=payload.top_k)
    return result
