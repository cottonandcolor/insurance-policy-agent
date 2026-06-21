"""Chroma-backed retrieval over synthetic policy chunks."""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from src.config import CHROMA_PERSIST_DIR, POLICY_DATA_DIR
from src.schemas import RetrievedChunk
from src.tools.chunking import chunk_policy_file

COLLECTION_NAME = "policy_chunks"
_index_ready = False


def _collection():
    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=DefaultEmbeddingFunction(),
    )


def index_policy_paths(paths: list[str | Path]) -> int:
    """Index specific .txt policy files into Chroma (upsert by chunk id)."""
    global _index_ready
    col = _collection()
    all_chunks: list[RetrievedChunk] = []

    for path_str in paths:
        path = Path(path_str)
        if path.suffix.lower() != ".txt" or not path.exists():
            continue
        all_chunks.extend(chunk_policy_file(path))

    if not all_chunks:
        _index_ready = True
        return col.count()

    col.upsert(
        ids=[c.chunk_id for c in all_chunks],
        documents=[c.text for c in all_chunks],
        metadatas=[
            {
                "plan_id": c.plan_id,
                "section": c.section,
                "jurisdiction": c.jurisdiction,
                "peril_tags": ",".join(c.peril_tags),
            }
            for c in all_chunks
        ],
    )
    _index_ready = True
    return col.count()


def build_index(policy_dir: Path | None = None) -> int:
    """Index all .txt policies. Returns chunk count."""
    global _index_ready
    directory = policy_dir or POLICY_DATA_DIR
    col = _collection()

    existing = col.count()
    if existing > 0:
        _index_ready = True
        return existing

    all_chunks: list[RetrievedChunk] = []
    for path in sorted(directory.glob("*.txt")):
        all_chunks.extend(chunk_policy_file(path))

    if not all_chunks:
        _index_ready = True
        return 0

    col.add(
        ids=[c.chunk_id for c in all_chunks],
        documents=[c.text for c in all_chunks],
        metadatas=[
            {
                "plan_id": c.plan_id,
                "section": c.section,
                "jurisdiction": c.jurisdiction,
                "peril_tags": ",".join(c.peril_tags),
            }
            for c in all_chunks
        ],
    )
    _index_ready = True
    return len(all_chunks)


def retrieve_evidence(
    plan_id: str,
    peril: str,
    jurisdiction: str,
    cache: dict[str, list[dict]],
    top_k: int = 3,
) -> list[dict]:
    key = f"{plan_id}:{peril}:{jurisdiction}"
    if key in cache:
        return cache[key]

    build_index()
    col = _collection()

    query = f"{peril} coverage exclusion deductible {plan_id}"
    results = col.query(
        query_texts=[query],
        n_results=top_k,
        where={"plan_id": plan_id},
    )

    chunks: list[dict] = []
    if results["ids"] and results["ids"][0]:
        for i, chunk_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i]
            text = results["documents"][0][i]
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "plan_id": meta["plan_id"],
                    "section": meta["section"],
                    "jurisdiction": meta["jurisdiction"],
                    "text": text,
                    "peril_tags": meta.get("peril_tags", "").split(","),
                }
            )

    cache[key] = chunks
    return chunks
