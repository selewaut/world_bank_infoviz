"""Empirically check latest available observation period.

Metadata `time_periods.end` is nominal and can include forecasts (e.g. WEO to 2031).
This script queries actual data for:
  1. every granular (Monthly/Quarterly/Weekly/Daily) indicator
  2. up to 2 representative indicators per database (highest coverage)

Outputs:
    data/derived/granular_freshness.csv
    data/derived/database_actual_freshness.csv
"""

from __future__ import annotations

import csv
import gzip
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

import requests

API = "https://data360api.worldbank.org/data360/data"
ROOT = Path(__file__).resolve().parent.parent
DERIVED = ROOT / "data" / "derived"
RAW = ROOT / "data" / "raw"
REFERENCE_YEAR = 2026
GRANULAR = {"Monthly", "Quarterly", "Weekly", "Daily"}
AGGREGATES = {
    "AFE", "AFW", "EAS", "ECS", "LCN", "MEA", "NAC", "SAS", "SSF",
    "ARB", "WLD", "EUU", "EMU", "OED", "HIC", "LIC", "LMC", "MIC", "UMC",
}
SESSION = requests.Session()
SESSION.headers.update(
    {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) world-bank-infoviz/0.1",
    }
)


def get(params: dict) -> dict:
    for attempt in range(4):
        try:
            resp = SESSION.get(API, params=params, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError):
            if attempt == 3:
                return {}
    return {}


def parse_period(value: str) -> date | None:
    value = str(value or "").strip()
    try:
        if "-Q" in value:
            y, q = value.split("-Q")
            return date(int(y), int(q) * 3, 1)
        parts = value.split("-")
        if len(parts) == 1:
            return date(int(parts[0]), 12, 31)
        if len(parts) == 2:
            return date(int(parts[0]), int(parts[1]), 1)
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def latest_for(db: str, ind: str, country: str) -> tuple[date | None, str | None, int]:
    payload = get(
        {
            "DATABASE_ID": db,
            "INDICATOR": ind,
            "REF_AREA": country,
            "timePeriodFrom": 2010,
            "timePeriodTo": REFERENCE_YEAR,
        }
    )
    rows = payload.get("value") or []
    best = None
    best_raw = None
    for row in rows:
        d = parse_period(row.get("TIME_PERIOD"))
        if d and (best is None or d > best):
            best, best_raw = d, row.get("TIME_PERIOD")
    return best, best_raw, len(rows)


def main() -> None:
    with gzip.open(RAW / "data360_indicators.jsonl.gz", "rt", encoding="utf-8") as f:
        raw = [json.loads(line) for line in f]
    by_id = {r["idno"]: r for r in raw if r.get("idno")}

    with (DERIVED / "indicators.csv").open(encoding="utf-8") as f:
        indicators = list(csv.DictReader(f))

    jobs = []

    granular = [r for r in indicators if r["periodicity"] in GRANULAR]
    for row in granular:
        meta = by_id.get(row["idno"], {})
        countries = [
            c["code"] for c in (meta.get("ref_country") or [])
            if c.get("code") and c["code"] not in AGGREGATES
        ]
        jobs.append(("granular", row, countries[:3]))

    by_db: dict[str, list[dict]] = {}
    for row in indicators:
        if row["periodicity"] == "Annual":
            by_db.setdefault(row["database_id"], []).append(row)
    for db, rows in by_db.items():
        rows.sort(key=lambda r: -int(r["coverage_economies"] or 0))
        for row in rows[:2]:
            meta = by_id.get(row["idno"], {})
            countries = [
                c["code"] for c in (meta.get("ref_country") or [])
                if c.get("code") and c["code"] not in AGGREGATES
            ]
            jobs.append(("annual", row, countries[:3]))

    results: dict[tuple[str, str, str], tuple] = {}

    def run(job):
        kind, row, countries = job
        for country in countries:
            d, raw_period, n = latest_for(row["database_id"], row["idno"], country)
            if d:
                return (kind, row, country, d, raw_period, n)
        return (kind, row, None, None, None, 0)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(run, j) for j in jobs]
        for i, fut in enumerate(as_completed(futures), 1):
            kind, row, country, d, raw_period, n = fut.result()
            results[(kind, row["database_id"], row["idno"])] = (country, d, raw_period, n)
            if i % 50 == 0:
                print(f"checked {i}/{len(jobs)}", flush=True)

    granular_rows = []
    for row in granular:
        country, d, raw_period, n = results.get(
            ("granular", row["database_id"], row["idno"]), (None, None, None, 0)
        )
        granular_rows.append(
            {
                "database_id": row["database_id"],
                "idno": row["idno"],
                "name": row["name"],
                "periodicity": row["periodicity"],
                "nominal_end": row["period_end"],
                "actual_latest": raw_period or "",
                "actual_latest_date": d.isoformat() if d else "",
                "probe_country": country or "",
                "rows_returned": n,
            }
        )

    actual_by_db: dict[str, list[dict]] = {}
    for row in indicators:
        if row["periodicity"] != "Annual":
            continue
        country, d, raw_period, n = results.get(
            ("annual", row["database_id"], row["idno"]), (None, None, None, 0)
        )
        if d:
            actual_by_db.setdefault(row["database_id"], []).append(
                {
                    "idno": row["idno"],
                    "country": country,
                    "latest": raw_period,
                    "latest_date": d,
                    "nominal_end": row["period_end"],
                }
            )

    db_rows = []
    for db, vals in sorted(actual_by_db.items()):
        vals.sort(key=lambda v: v["latest_date"], reverse=True)
        best = vals[0]
        db_rows.append(
            {
                "database_id": db,
                "probe_indicator": best["idno"],
                "probe_country": best["country"],
                "actual_latest_period": best["latest"],
                "actual_latest_year": best["latest_date"].year,
                "nominal_end": best["nominal_end"],
                "is_projection_year": int(str(best["nominal_end"])[:4]) > REFERENCE_YEAR,
                "probes": len(vals),
            }
        )

    write_csv(DERIVED / "granular_freshness.csv", list(granular_rows[0].keys()), granular_rows)
    if db_rows:
        write_csv(DERIVED / "database_actual_freshness.csv", list(db_rows[0].keys()), db_rows)

    print(f"\ngranular indicators checked: {len(granular_rows)}")
    for r in granular_rows:
        print(f"  {r['database_id']:<14} {r['periodicity']:<10} nominal={r['nominal_end']:<8} actual={r['actual_latest']}")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
