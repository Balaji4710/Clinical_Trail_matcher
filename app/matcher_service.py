from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app import models
from app.ai_service import evaluate_eligibility
from app.chroma_service import search_trials


def _patient_to_query(patient: Dict[str, Any]) -> str:
    return (
        f"Patient {patient.get('patient_name', '')} "
        f"age {patient.get('age', 'NA')} gender {patient.get('gender', 'NA')}. "
        f"Disease: {patient.get('disease', '')}. "
        f"Medications: {patient.get('medication', '')}. "
        f"History: {patient.get('medical_history', '')}."
    )


def match_patient_to_trials(
    db: Session, patient: Dict[str, Any], top_k: int = 5
) -> Dict[str, Any]:
    query = _patient_to_query(patient)
    hits = search_trials(query, top_k=top_k)

    retrieved: List[Dict[str, Any]] = []
    for hit in hits:
        meta = hit.get("metadata", {}) or {}
        trial_id = meta.get("trial_id")
        trial_row = None
        if trial_id is not None:
            trial_row = db.query(models.ClinicalTrial).filter_by(id=int(trial_id)).first()

        if trial_row is not None:
            trial_payload = {
                "id": trial_row.id,
                "title": trial_row.title,
                "disease": trial_row.disease,
                "description": trial_row.description,
                "inclusion_criteria": trial_row.inclusion_criteria,
                "exclusion_criteria": trial_row.exclusion_criteria,
                "min_age": trial_row.min_age,
                "max_age": trial_row.max_age,
                "status": trial_row.status,
            }
        else:
            trial_payload = {
                "id": trial_id,
                "title": meta.get("title", ""),
                "disease": meta.get("disease", ""),
                "description": hit.get("document", ""),
                "inclusion_criteria": "",
                "exclusion_criteria": "",
                "min_age": meta.get("min_age"),
                "max_age": meta.get("max_age"),
                "status": meta.get("status", ""),
            }

        try:
            verdict = evaluate_eligibility(patient, trial_payload)
        except Exception as exc:  # don't kill the whole match on one trial
            verdict = {
                "eligible": False,
                "match_score": 0,
                "reason": f"Evaluation failed: {exc}",
                "recommendation": "Manual review required.",
            }

        retrieved.append({
            "trial_id": trial_payload.get("id"),
            "title": trial_payload.get("title", ""),
            "disease": trial_payload.get("disease", ""),
            "eligible": verdict["eligible"],
            "match_score": verdict["match_score"],
            "reason": verdict["reason"],
            "recommendation": verdict["recommendation"],
        })

    retrieved.sort(key=lambda x: x["match_score"], reverse=True)
    best = retrieved[0] if retrieved else None
    return {
        "patient": patient,
        "retrieved_trials": retrieved,
        "best_match": best,
    }
