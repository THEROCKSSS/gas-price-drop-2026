#!/usr/bin/env python3
"""Build the embedded chart dataset for the gas-price report.

Reads the EIA weekly retail CSV, computes monthly averages and the
largest 28-day declines since 1990, and writes data/chart_data.json.
"""
import csv
import datetime as dt
import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "eia_weekly_retail.csv"
HTML_PATH = ROOT / "data" / "eia_weekly_gasoline.html"
OUT = ROOT / "data" / "chart_data.json"

# --- full weekly series from the saved EIA page (1990-2026) ---
src = HTML_PATH.read_text(encoding="utf-8", errors="ignore")
rows = re.findall(r"<tr[^>]*>(.*?)</tr>", src, re.S)
full = []
for row in rows:
    cells = [
        html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
        for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
    ]
    if not cells or not re.match(r"^(\d{4})-([A-Z][a-z]{2})$", cells[0]):
        continue
    year = cells[0][:4]
    i = 1
    while i + 1 < len(cells):
        d, v = cells[i], cells[i + 1]
        if re.match(r"^\d{2}/\d{2}$", d) and re.match(r"^\d+\.\d+$", v):
            full.append((dt.date(int(year), int(d[:2]), int(d[3:])), float(v)))
            i += 2
        else:
            i += 1
full.sort()
by_date = dict(full)

# --- recent series with diesel ---
recent = []
with CSV_PATH.open(encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if r["week_ending"] >= "2024-01-01":
            recent.append(
                [
                    r["week_ending"],
                    float(r["gasoline_regular_usd_gal"]),
                    float(r["diesel_usd_gal"]) if r["diesel_usd_gal"] else None,
                ]
            )

# --- monthly averages, 2026 ---
monthly = []
buckets = defaultdict(list)
for r in recent:
    if r[0].startswith("2026"):
        buckets[r[0][:7]].append(r)
for month in sorted(buckets):
    vals = buckets[month]
    gas = [v[1] for v in vals]
    diesel = [v[2] for v in vals if v[2] is not None]
    monthly.append(
        {
            "m": month,
            "gas": round(sum(gas) / len(gas), 3),
            "diesel": round(sum(diesel) / len(diesel), 3) if diesel else None,
            "weeks": len(vals),
        }
    )

# --- ten largest four-week declines since 1990 ---
changes = []
for d, v in full:
    prev = by_date.get(d - dt.timedelta(days=28))
    if prev is not None:
        changes.append({"date": d.isoformat(), "change": round(v - prev, 3), "from": prev, "to": v})
changes.sort(key=lambda x: x["change"])
ranked = changes[:18]

# --- key numbers ---
key = {
    "aaa_current": 3.6366,
    "aaa_yesterday": 3.6448,
    "aaa_week": 3.8118,
    "aaa_month": 4.2926,
    "aaa_year": 3.0717,
    "aaa_peak": 4.56,
    "aaa_peak_date": "2026-05-21",
    "aaa_autumn": 4.48,
    "aaa_autumn_date": "2026-09-24",
    "diesel_current": 5.8182,
    "diesel_month": 6.3172,
    "diesel_year": 3.7928,
    "diesel_record": 6.5276,
    "diesel_record_date": "2026-09-22",
    "eia_current": 3.805,
    "eia_current_date": "2026-11-16",
    "eia_month": 4.269,
    "eia_month_date": "2026-10-26",
    "eia_sep": 4.478,
    "eia_sep_date": "2026-09-21",
    "eia_year": 3.062,
    "eia_year_date": "2025-11-17",
    "brent_now": 89.37,
    "brent_peak": 136.0,
    "brent_peak_date": "2026-10-08",
    "wti_now": 80.17,
    "generated": "2026-11-23T19:25:00-07:00",
}

payload = {
    "weekly": recent,
    "monthly": monthly,
    "ranked": ranked,
    "key": key,
}
OUT.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes); weekly={len(recent)} monthly={len(monthly)} ranked={len(ranked)}")
