#!/usr/bin/env python3
"""Inject the chart dataset into the HTML template and write index.html."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "build" / "template.html"
DATA = ROOT / "data" / "chart_data.json"
OUT = ROOT / "index.html"

template = TEMPLATE.read_text(encoding="utf-8")
data = DATA.read_text(encoding="utf-8")
if "__DATA_JSON__" not in template:
    raise SystemExit("template is missing the __DATA_JSON__ placeholder")
OUT.write_text(template.replace("__DATA_JSON__", data), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")
