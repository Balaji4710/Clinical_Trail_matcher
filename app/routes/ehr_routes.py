import os
import shutil
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.ai_service import extract_medical_information
from app.pdf_service import extract_text_from_pdf
from app.schemas import EHRExtractionResponse

router = APIRouter(prefix="", tags=["EHR"])


@router.post("/upload-ehr", response_model=EHRExtractionResponse)
async def upload_ehr(file: UploadFile = File(...)):
    """Upload a patient EHR PDF and get structured medical info back."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        text = extract_text_from_pdf(tmp_path)
        if not text:
            raise HTTPException(
                status_code=422,
                detail="No extractable text found in the PDF.",
            )

        extracted = extract_medical_information(text)
        return EHRExtractionResponse(
            raw_text_preview=text[:1500],
            extracted=extracted,
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
