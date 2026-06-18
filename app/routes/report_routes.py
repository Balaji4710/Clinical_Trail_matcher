
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.report_service import generate_patient_report
from app.schemas import ReportRequest

router = APIRouter(prefix="", tags=["Reports"])


@router.post("/generate-report")
def generate_report(payload: ReportRequest):
    path = generate_patient_report(
        patient=payload.patient.model_dump(),
        match_result=payload.match_result.model_dump(),
    )
    return {"report_path": path}


@router.get("/download-report")
def download_report(path: str):
    """Download a previously generated report by path."""
    if not os.path.exists(path) or not path.startswith("reports"):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=os.path.basename(path),
    )
