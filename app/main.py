from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import ehr_routes, match_routes, report_routes, trial_routes
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Clinical Trial and EHR Matcher",
    description=(
        "AI + RAG powered service that ingests patient EHRs, indexes clinical "
        "trials in a vector database, and uses Gemini to recommend matches."
    ),
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ehr_routes.router)
app.include_router(trial_routes.router)
app.include_router(match_routes.router)
app.include_router(report_routes.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "name": "Clinical Trial and EHR Matcher",
        "docs": "/docs",
        "status": "ok",
    }
