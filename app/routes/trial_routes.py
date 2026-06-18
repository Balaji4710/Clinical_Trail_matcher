from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.chroma_service import add_trial_to_vector_db
from app.database import get_db
from app.schemas import TrialCreate, TrialResponse

router = APIRouter(prefix="/trials", tags=["Clinical Trials"])


@router.post("", response_model=TrialResponse)
def create_trial(payload: TrialCreate, db: Session = Depends(get_db)):
    trial = models.ClinicalTrial(**payload.model_dump())
    db.add(trial)
    db.commit()
    db.refresh(trial)

    # Index in vector DB
    add_trial_to_vector_db({
        "id": trial.id,
        "title": trial.title,
        "disease": trial.disease,
        "description": trial.description,
        "inclusion_criteria": trial.inclusion_criteria,
        "exclusion_criteria": trial.exclusion_criteria,
        "min_age": trial.min_age,
        "max_age": trial.max_age,
        "status": trial.status,
    })
    return trial


@router.get("", response_model=List[TrialResponse])
def list_trials(db: Session = Depends(get_db)):
    return db.query(models.ClinicalTrial).all()


@router.get("/{trial_id}", response_model=TrialResponse)
def get_trial(trial_id: int, db: Session = Depends(get_db)):
    trial = db.query(models.ClinicalTrial).filter_by(id=trial_id).first()
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    return trial
