"""FastAPI backend for React demo UI."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src.config import (
    LLM_PROVIDER,
    MAX_UPLOAD_BYTES,
    MAX_UPLOAD_FILES,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_MODEL,
    ROOT,
    UPLOAD_DIR,
    get_llm_mode_label,
)
from src.runner import build_user_messages, format_response, run_agent

app = FastAPI(title="Insurance Policy Comparison Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_POLICIES = [
    str(ROOT / "data" / "synthetic" / "plan_a.txt"),
    str(ROOT / "data" / "synthetic" / "plan_b.txt"),
]

PUBLIC_POLICY_PRESETS: dict[str, list[str]] = {
    "public_ho3": [
        str(ROOT / "data" / "public" / "travelers_ho3_nv.txt"),
        str(ROOT / "data" / "public" / "statefarm_hw2136_ok.txt"),
    ],
    "public_flood": [
        str(ROOT / "data" / "public" / "travelers_ho3_nv.txt"),
        str(ROOT / "data" / "public" / "fema_nfip_dwelling_2021.txt"),
    ],
}

SAMPLE_POLICIES: dict[str, Path] = {
    "plan_a.txt": ROOT / "data" / "synthetic" / "plan_a.txt",
    "plan_b.txt": ROOT / "data" / "synthetic" / "plan_b.txt",
    "travelers_ho3_nv.txt": ROOT / "data" / "public" / "travelers_ho3_nv.txt",
    "statefarm_hw2136_ok.txt": ROOT / "data" / "public" / "statefarm_hw2136_ok.txt",
    "shelter_ho3_ok.txt": ROOT / "data" / "public" / "shelter_ho3_ok.txt",
    "fema_nfip_dwelling_2021.txt": ROOT / "data" / "public" / "fema_nfip_dwelling_2021.txt",
}


async def _ollama_reachable() -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False


@app.get("/api/health")
async def health():
    ollama_ok = await _ollama_reachable()
    return {
        "status": "ok",
        "llm_provider": LLM_PROVIDER,
        "ollama_reachable": ollama_ok,
        "configured_model": get_llm_mode_label(),
    }


@app.get("/api/models")
async def models():
    return {
        "provider": LLM_PROVIDER,
        "ollama_model": OLLAMA_MODEL,
        "openai_model": OPENAI_MODEL,
        "label": get_llm_mode_label(),
    }


@app.get("/api/samples/{filename}")
async def sample_policy(filename: str):
    """Download synthetic or public specimen policies."""
    path = SAMPLE_POLICIES.get(filename)
    if path is None or not path.is_file():
        raise HTTPException(status_code=404, detail="Sample not found")
    return FileResponse(path, media_type="text/plain", filename=filename)


@app.post("/api/analyze")
async def analyze(
    age: int = Form(35),
    location: str = Form("Cedar Park, TX"),
    flood_zone: bool = Form(True),
    home_value: int = Form(350000),
    coverage_breadth: float = Form(0.4),
    low_cost: float = Form(0.3),
    few_exclusions: float = Form(0.3),
    dry_run: bool = Query(False),
    quick: bool = Query(False),
    use_defaults: bool = Form(True),
    policy_preset: str = Form("synthetic"),
    policies: list[UploadFile] = File(default=[]),
):
    if not dry_run and LLM_PROVIDER == "ollama":
        if not await _ollama_reachable():
            raise HTTPException(
                status_code=503,
                detail="Ollama is not running. Start with: ollama serve",
            )

    session_id = uuid.uuid4().hex[:12]
    session_dir = UPLOAD_DIR / session_id
    policy_paths: list[str] = []

    try:
        if policies:
            if len(policies) > MAX_UPLOAD_FILES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Maximum {MAX_UPLOAD_FILES} policy files allowed.",
                )
            session_dir.mkdir(parents=True, exist_ok=True)
            for upload in policies:
                if not upload.filename or not upload.filename.lower().endswith(".txt"):
                    raise HTTPException(
                        status_code=400,
                        detail="Only .txt policy files are supported.",
                    )
                content = await upload.read()
                if len(content) > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File {upload.filename} exceeds 500KB limit.",
                    )
                safe_name = Path(upload.filename).name
                dest = session_dir / safe_name
                dest.write_bytes(content)
                policy_paths.append(str(dest))
        elif policy_preset in PUBLIC_POLICY_PRESETS:
            policy_paths = PUBLIC_POLICY_PRESETS[policy_preset].copy()
        elif use_defaults or policy_preset == "synthetic":
            policy_paths = DEFAULT_POLICIES.copy()
        else:
            raise HTTPException(
                status_code=400,
                detail="Upload .txt policy files or choose a bundled preset.",
            )

        user_messages = build_user_messages(
            age=age,
            location=location,
            flood_zone=flood_zone,
            coverage_breadth=coverage_breadth,
            low_cost=low_cost,
            few_exclusions=few_exclusions,
            home_value=home_value,
        )

        beam_width = 2 if quick else 3
        max_depth = 2 if quick else 4

        result = run_agent(
            policy_paths=policy_paths,
            user_messages=user_messages,
            dry_run=dry_run,
            beam_width=beam_width,
            max_depth=max_depth,
        )
        return format_response(result)

    finally:
        if session_dir.exists():
            shutil.rmtree(session_dir, ignore_errors=True)
