import os
from typing import Any, Dict, List

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
COLLECTION_NAME = "clinical_trials"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

_client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIR,
    settings=Settings(anonymized_telemetry=False),
)
_collection = _client.get_or_create_collection(name=COLLECTION_NAME)
_model = SentenceTransformer(EMBED_MODEL_NAME)


def _trial_to_document(trial: Dict[str, Any]) -> str:
    parts = [
        f"Title: {trial.get('title', '')}",
        f"Disease: {trial.get('disease', '')}",
        f"Description: {trial.get('description', '') or ''}",
        f"Inclusion Criteria: {trial.get('inclusion_criteria', '') or ''}",
        f"Exclusion Criteria: {trial.get('exclusion_criteria', '') or ''}",
        f"Age Range: {trial.get('min_age', 'NA')} - {trial.get('max_age', 'NA')}",
    ]
    return "\n".join(parts)


def add_trial_to_vector_db(trial: Dict[str, Any]) -> None:
    """Insert/upsert one trial into the ChromaDB collection."""
    doc = _trial_to_document(trial)
    embedding = _model.encode(doc).tolist()
    metadata = {
        "trial_id": int(trial["id"]),
        "title": trial.get("title", ""),
        "disease": trial.get("disease", ""),
        "min_age": int(trial.get("min_age") or 0),
        "max_age": int(trial.get("max_age") or 200),
        "status": trial.get("status", ""),
    }
    _collection.upsert(
        ids=[f"trial-{trial['id']}"],
        embeddings=[embedding],
        documents=[doc],
        metadatas=[metadata],
    )


def search_trials(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Semantic search across stored trials."""
    if _collection.count() == 0:
        return []
    embedding = _model.encode(query_text).tolist()
    n_results = min(top_k, _collection.count())
    results = _collection.query(query_embeddings=[embedding], n_results=n_results)

    hits: List[Dict[str, Any]] = []
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for i, _id in enumerate(ids):
        hits.append({
            "chroma_id": _id,
            "document": documents[i] if i < len(documents) else "",
            "metadata": metadatas[i] if i < len(metadatas) else {},
            "distance": distances[i] if i < len(distances) else None,
        })
    return hits
