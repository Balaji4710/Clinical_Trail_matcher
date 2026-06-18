import json
import os
import re
from pathlib import Path
from typing import Any, Dict
import google.generativeai as genai
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
def _get_model():
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )

    return genai.GenerativeModel(GEMINI_MODEL)
def _strip_code_fences(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()

        if text.endswith("```"):
            text = text[:-3].strip()

    return text


def _safe_json_loads(text: str) -> Dict[str, Any]:
    cleaned = _strip_code_fences(text)

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)

        if match:
            return json.loads(match.group(0))

        raise


def extract_medical_information(text: str) -> Dict[str, Any]:
    """Extract structured medical information from EHR text."""

    model = _get_model()

    prompt = f"""
You are a clinical NLP assistant.

Extract structured medical information from the following Electronic Health Record (EHR).

Return STRICT JSON with this schema:

{{
  "patient_name": string | null,
  "age": integer | null,
  "gender": string | null,
  "diseases": [string],
  "medications": [string],
  "allergies": [string],
  "symptoms": [string]
}}

EHR TEXT:
\"\"\"
{text}
\"\"\"

Respond with ONLY the JSON object.
""".strip()

    response = model.generate_content(prompt)

    raw = (response.text or "").strip()

    try:
        return _safe_json_loads(raw)

    except Exception:
        return {
            "patient_name": None,
            "age": None,
            "gender": None,
            "diseases": [],
            "medications": [],
            "allergies": [],
            "symptoms": [],
            "_raw_model_output": raw,
        }


def evaluate_eligibility(
    patient: Dict[str, Any],
    trial: Dict[str, Any]
) -> Dict[str, Any]:
    """Evaluate eligibility of patient for a clinical trial."""

    model = _get_model()

    prompt = f"""
You are a clinical trial eligibility evaluator.

PATIENT:
{json.dumps(patient, indent=2)}

CLINICAL TRIAL:
{json.dumps(trial, indent=2)}

Determine whether the patient is eligible.

Consider:
- age range
- disease match
- inclusion criteria
- exclusion criteria

Return STRICT JSON:

{{
  "eligible": boolean,
  "match_score": integer,
  "reason": string,
  "recommendation": string
}}

Respond with ONLY the JSON object.
""".strip()

    response = model.generate_content(prompt)

    raw = (response.text or "").strip()

    try:
        data = _safe_json_loads(raw)

    except Exception:
        return {
            "eligible": False,
            "match_score": 0,
            "reason": "Could not parse model response.",
            "recommendation": "Manual review required."
        }

    data["eligible"] = bool(data.get("eligible", False))

    try:
        data["match_score"] = int(data.get("match_score", 0))
    except (TypeError, ValueError):
        data["match_score"] = 0

    data["reason"] = str(data.get("reason", ""))
    data["recommendation"] = str(data.get("recommendation", ""))

    return data