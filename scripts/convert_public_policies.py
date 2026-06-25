#!/usr/bin/env python3
"""Convert downloaded public policy PDFs to .txt for the comparison agent."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "public" / "raw"
OUT_DIR = ROOT / "data" / "public"

POLICIES = [
    {
        "pdf": "travelers_ho3_nv.pdf",
        "out": "travelers_ho3_nv.txt",
        "title": "PUBLIC SPECIMEN HOMEOWNERS POLICY — TRAVELERS HO-3",
        "jurisdiction": "NV",
        "carrier": "Travelers (HO-3 Special Form, specimen filed with Nevada DOI)",
        "source_url": "https://docs.nv.gov/doi/documents/home_policies/TravelersForms/Travelers_HO-3.pdf",
    },
    {
        "pdf": "statefarm_ok.pdf",
        "out": "statefarm_hw2136_ok.txt",
        "title": "PUBLIC SPECIMEN HOMEOWNERS POLICY — STATE FARM HW-2136",
        "jurisdiction": "OK",
        "carrier": "State Farm Fire and Casualty Company (HW-2136, filed with Oklahoma OID)",
        "source_url": "https://www.oid.ok.gov/wp-content/uploads/2019/08/040218_HW-2136-2017.pdf",
    },
    {
        "pdf": "shelter_ho3_ok.pdf",
        "out": "shelter_ho3_ok.txt",
        "title": "PUBLIC SPECIMEN HOMEOWNERS POLICY — SHELTER HO-3",
        "jurisdiction": "OK",
        "carrier": "Shelter Mutual Insurance Company (HO-3, filed with Oklahoma OID)",
        "source_url": "https://www.oid.ok.gov/wp-content/uploads/2019/08/Shelter_HO-3Policy.pdf",
    },
    {
        "pdf": "fema_nfip_dwelling_2021.pdf",
        "out": "fema_nfip_dwelling_2021.txt",
        "title": "PUBLIC SPECIMEN FLOOD POLICY — FEMA NFIP DWELLING FORM",
        "jurisdiction": "US",
        "carrier": "FEMA National Flood Insurance Program (Standard Flood Insurance Policy F-122)",
        "source_url": "https://www.fema.gov/sites/default/files/documents/fema_F-122-Dwelling-SFIP_2021.pdf",
    },
]

DISCLAIMER = (
    "Educational use only. Public regulatory specimen — not a quote, endorsement, or binding contract. "
    "Coverage terms vary by state, endorsements, and declarations page."
)

SECTION_NORMALIZERS = [
    (
        re.compile(r"\nSECTION\s+([IVXLC]+)\s*[–—\-]\s*([^\n]+)", re.IGNORECASE),
        r"\n\nSection \1 — \2\n",
    ),
    (
        re.compile(r"\nSection\s+([IVXLC]+)\s*[–—\-]\s*([^\n]+)", re.IGNORECASE),
        r"\n\nSection \1 — \2\n",
    ),
    (
        re.compile(r"\n([IVXLC]+)\.\s+(AGREEMENT|DEFINITIONS|PROPERTY COVERAGES|LIABILITY COVERAGES|EXCLUSIONS|CONDITIONS|ENDORSEMENTS)\b", re.IGNORECASE),
        r"\n\nSection \1 — \2\n",
    ),
]


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def normalize_sections(text: str) -> str:
    for pattern, repl in SECTION_NORMALIZERS:
        text = pattern.sub(repl, text)
    return re.sub(r"\n{3,}", "\n\n", text)


def build_header(meta: dict) -> str:
    lines = [
        meta["title"],
        f"Jurisdiction: {meta['jurisdiction']}",
        f"Carrier: {meta['carrier']}",
        f"Source URL: {meta['source_url']}",
        f"Disclaimer: {DISCLAIMER}",
        "",
    ]
    return "\n".join(lines)


def convert_one(meta: dict) -> Path:
    pdf_path = RAW_DIR / meta["pdf"]
    if not pdf_path.is_file():
        raise FileNotFoundError(f"Missing PDF: {pdf_path}")

    body = normalize_sections(extract_pdf_text(pdf_path).strip())
    out_path = OUT_DIR / meta["out"]
    out_path.write_text(build_header(meta) + body + "\n", encoding="utf-8")
    return out_path


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for meta in POLICIES:
        out = convert_one(meta)
        size_kb = out.stat().st_size // 1024
        print(f"Wrote {out.relative_to(ROOT)} ({size_kb} KB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
