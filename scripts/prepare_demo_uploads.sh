#!/usr/bin/env bash
# Copy policy .txt files into demo-uploads/ for manual UI upload demos.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/demo-uploads"

mkdir -p "$DEST/synthetic" "$DEST/ho3-compare" "$DEST/flood-zone"

cp "$ROOT/data/synthetic/plan_a.txt" "$ROOT/data/synthetic/plan_b.txt" "$DEST/synthetic/"
cp "$ROOT/data/public/travelers_ho3_nv.txt" "$ROOT/data/public/statefarm_hw2136_ok.txt" "$DEST/ho3-compare/"
cp "$ROOT/data/public/travelers_ho3_nv.txt" "$ROOT/data/public/fema_nfip_dwelling_2021.txt" "$DEST/flood-zone/"

echo "Demo upload files ready in: $DEST"
ls -la "$DEST"/*/
