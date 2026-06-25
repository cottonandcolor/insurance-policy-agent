# Public policy specimens — sources

These files are **public regulatory filings** and **federal standard forms**, converted from PDF to plain text for the capstone comparison agent. They are for **educational and research use only** — not quotes, endorsements, or binding contracts.

| File | Type | Source |
|------|------|--------|
| `travelers_ho3_nv.txt` | Homeowners HO-3 | [Nevada Division of Insurance — Travelers HO-3 PDF](https://docs.nv.gov/doi/documents/home_policies/TravelersForms/Travelers_HO-3.pdf) |
| `statefarm_hw2136_ok.txt` | Homeowners (State Farm HW-2136) | [Oklahoma Insurance Department — State Farm PDF](https://www.oid.ok.gov/wp-content/uploads/2019/08/040218_HW-2136-2017.pdf) |
| `shelter_ho3_ok.txt` | Homeowners HO-3 | [Oklahoma Insurance Department — Shelter HO-3 PDF](https://www.oid.ok.gov/wp-content/uploads/2019/08/Shelter_HO-3Policy.pdf) |
| `fema_nfip_dwelling_2021.txt` | NFIP flood (dwelling) | [FEMA — Standard Flood Insurance Policy F-122 (2021)](https://www.fema.gov/sites/default/files/documents/fema_F-122-Dwelling-SFIP_2021.pdf) |

## Suggested comparison pairs

- **Two HO-3 homeowners forms:** `travelers_ho3_nv.txt` + `statefarm_hw2136_ok.txt` (or `shelter_ho3_ok.txt`)
- **Home + flood (flood-zone scenario):** `travelers_ho3_nv.txt` + `fema_nfip_dwelling_2021.txt`

Bundled synthetic plans (`data/synthetic/plan_a.txt`, `plan_b.txt`) remain the default for dry-run demos with a clear flood exclude vs. sublimit contrast.

## Regenerating from PDFs

```bash
# Download PDFs into data/public/raw/ (URLs above), then:
pip install pypdf
python scripts/convert_public_policies.py
```

Raw PDFs are stored under `data/public/raw/` (not required at runtime; only the `.txt` files are used by the agent).
