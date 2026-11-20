"""Compute per-database regional coverage from indicator ref_country lists.

Outputs:
    data/derived/database_region_coverage.csv
    data/derived/region_overall.csv
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DERIVED = ROOT / "data" / "derived"
RAW = ROOT / "data" / "raw"
HIERARCHY = "https://data360api.worldbank.org/data360/portal/v1/hierarchy"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) world-bank-infoviz/0.1"
NON_COUNTRY = {
    "AFE", "AFW", "EAS", "ECS", "LCN", "MEA", "NAC", "SAS", "SSF",
    "ARB", "WLD", "EUU", "EMU", "OED", "HIC", "LIC", "LMC", "MIC", "UMC",
    "INX", "IBD", "IDA", "IDB", "IDA", "OED",
}

SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json", "User-Agent": UA})


def fetch_hierarchy() -> dict:
    resp = SESSION.get(HIERARCHY, params={"type": "country"}, timeout=60)
    resp.raise_for_status()
    return resp.json()["data"]


def main() -> None:
    data = fetch_hierarchy()
    regions = data["HCL_WB_REGIONS"]
    country_region: dict[str, set[str]] = defaultdict(set)
    region_size: dict[str, int] = {}
    region_name: dict[str, str] = {}
    for region in regions:
        rid = region["id"]
        region_name[rid] = region["name"]
        region_size[rid] = len(region["countries"])
        for country in region["countries"]:
            country_region[country["id"]].add(rid)

    indicators = []
    with gzip.open(RAW / "data360_indicators.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            indicators.append(json.loads(line))

    db_region: dict[tuple[str, str], list[float]] = defaultdict(list)
    for rec in indicators:
        db = rec.get("database_id") or "UNKNOWN"
        codes = {
            c.get("code")
            for c in (rec.get("ref_country") or [])
            if c.get("code") and c.get("code") not in NON_COUNTRY
        }
        for rid, size in region_size.items():
            if size == 0:
                continue
            covered = sum(1 for c, rids in country_region.items() if rid in rids and c in codes)
            db_region[(db, rid)].append(covered / size)

    rows = []
    for (db, rid), values in sorted(db_region.items()):
        rows.append(
            {
                "database_id": db,
                "region": rid,
                "region_name": region_name[rid],
                "region_countries": region_size[rid],
                "indicators": len(values),
                "mean_coverage": round(sum(values) / len(values), 3),
                "median_coverage": round(sorted(values)[len(values) // 2], 3),
                "full_coverage_indicators": sum(1 for v in values if v >= 0.99),
            }
        )
    write_csv(DERIVED / "database_region_coverage.csv", list(rows[0].keys()), rows)

    overall = []
    for rid in region_size:
        db_values = [r for r in rows if r["region"] == rid]
        overall.append(
            {
                "region": rid,
                "region_name": region_name[rid],
                "countries": region_size[rid],
                "databases": len(db_values),
                "mean_db_coverage": round(
                    sum(r["mean_coverage"] for r in db_values) / len(db_values), 3
                )
                if db_values
                else 0,
                "databases_over_50pct": sum(1 for r in db_values if r["mean_coverage"] >= 0.5),
            }
        )
    write_csv(DERIVED / "region_overall.csv", list(overall[0].keys()), overall)
    for r in overall:
        print(
            f"  {r['region']:<4} {r['region_name'][:38]:<38} dbs={r['databases']:>3} "
            f"mean_cov={r['mean_db_coverage']:<5} dbs>50%={r['databases_over_50pct']}"
        )


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
