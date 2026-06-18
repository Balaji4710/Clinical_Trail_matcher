# Clinical Trial and EHR Matcher

An AI + RAG based healthcare backend that ingests patient EHR PDFs, indexes
clinical trials in a vector database, and uses **Google Gemini** to score
patient eligibility and generate PDF matching reports.

## Tech Stack

- **FastAPI** + Uvicorn
- **SQLite** + SQLAlchemy
- **Google Gemini** (`google-generativeai`)
- **ChromaDB** + **Sentence Transformers** (`all-MiniLM-L6-v2`)
- **pdfplumber** for PDF text extraction
- **ReportLab** for PDF report generation

## Project Structure

```
clinical_trial_matcher/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── ai_service.py
│   ├── pdf_service.py
│   ├── chroma_service.py
│   ├── matcher_service.py
│   ├── report_service.py
│   └── routes/
│       ├── ehr_routes.py
│       ├── trial_routes.py
│       ├── match_routes.py
│       └── report_routes.py
├── sample_data/
│   ├── sample_trials.json
│   ├── sample_ehr.txt
│   └── seed_trials.py
├── reports/
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### 1. Clone & enter the project

```bash
cd clinical_trial_matcher
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> The first install pulls **torch** and a **SentenceTransformer** model
> (~90 MB on first run).

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free key from <https://aistudio.google.com/app/apikey>.

## Running the API

```bash
uvicorn app.main:app --reload
```

Open Swagger UI at **<http://127.0.0.1:8000/docs>**.

## Seed sample clinical trials (optional)

```bash
python sample_data/seed_trials.py
```

This inserts 3 sample trials into SQLite and indexes them into ChromaDB.

## API Reference

| Method | Endpoint            | Description                                       |
|--------|---------------------|---------------------------------------------------|
| POST   | `/upload-ehr`       | Upload an EHR PDF, get structured medical info    |
| POST   | `/trials`           | Create a clinical trial (also indexes in Chroma)  |
| GET    | `/trials`           | List clinical trials                              |
| GET    | `/trials/{id}`      | Get a specific clinical trial                     |
| POST   | `/match-patient`    | RAG retrieval + Gemini eligibility evaluation     |
| POST   | `/generate-report`  | Generate a PDF report of patient + matches        |
| GET    | `/download-report`  | Download a previously generated report            |

## RAG Workflow

```
Patient EHR (PDF)
    │
    ▼
pdfplumber  ──► raw text
    │
    ▼
Gemini      ──► structured patient JSON
    │
    ▼
Embed patient query with all-MiniLM-L6-v2
    │
    ▼
ChromaDB top-k search over indexed trials
    │
    ▼
For each retrieved trial → Gemini eligibility check
    │
    ▼
Ranked matches + best recommendation
    │
    ▼
ReportLab PDF report
```

## Sample Requests

### Create a trial

```bash
curl -X POST http://127.0.0.1:8000/trials \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Phase III Trial of Novel SGLT2 Inhibitor in Type 2 Diabetes",
    "disease": "Type 2 Diabetes",
    "description": "Glycemic control + CV outcomes",
    "inclusion_criteria": "Adults 30-70, HbA1c 7-10.5%, stable metformin >=3 months",
    "exclusion_criteria": "Type 1 diabetes, eGFR < 45, pregnancy",
    "min_age": 30,
    "max_age": 70,
    "status": "recruiting"
  }'
```

### Match a patient

```bash
curl -X POST http://127.0.0.1:8000/match-patient \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Jane Doe",
    "age": 58,
    "gender": "Female",
    "disease": "Type 2 Diabetes",
    "medication": "Metformin 1000 mg BID, Lisinopril",
    "medical_history": "HbA1c 8.4%, hypertension, hyperlipidemia",
    "top_k": 3
  }'
```

### Upload an EHR PDF

```bash
curl -X POST http://127.0.0.1:8000/upload-ehr \
  -F "file=@/path/to/patient.pdf"
```

### Generate a report

POST `/generate-report` with the body:

```json
{
  "patient": { "patient_name": "Jane Doe", "age": 58, "gender": "Female",
               "disease": "Type 2 Diabetes",
               "medication": "Metformin 1000 mg BID",
               "medical_history": "HbA1c 8.4%" },
  "match_result": { ... output of /match-patient ... }
}
```

Returns: `{ "report_path": "reports/report_JaneDoe_YYYYMMDD_HHMMSS.pdf" }`.

## Disclaimer

This project is for educational and decision-support purposes only. It is
**not** a medical device and must not be used as the sole basis for any
clinical decision.
