"""Pull Data360 indicator metadata and derive exploration summaries.

Usage:
    python scripts/explore_api.py

Outputs:
    data/raw/data360_indicators.jsonl.gz
    data/derived/database_summary.csv
    data/derived/periodicity_summary.csv
    data/derived/freshness_summary.csv
    data/derived/topic_summary.csv
    data/derived/database_topics.csv
    data/derived/region_summary.csv
"""

from __future__ import annotations

import csv
import gzip
import json
import statistics
import time
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

import requests

API = "https://data360api.worldbank.org/data360/metadata"
PAGE = 1000
REFERENCE_DATE = date(2026, 11, 20)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"

SELECT = ",".join(
    [
        "tags",
        "series_description/idno",
        "series_description/name",
        "series_description/database_id",
        "series_description/database_name",
        "series_description/periodicity",
        "series_description/time_periods",
        "series_description/topics",
        "series_description/ref_country",
        "series_description/measurement_unit",
        "series_description/date_last_update",
        "series_description/date_released",
    ]
)
QUERY = (
    f"&$top={PAGE}&$filter=type eq 'indicator'&$select={SELECT}"
    "&$orderby=series_description%2Fdatabase_id%20asc,series_description%2Fidno%20asc"
)

TOPIC_VOCAB = {
    "WB Practice Groups": "L0",
    "Data360 Topic L1": "L1",
    "Data360 Topic L2": "L2",
}

SESSION = requests.Session()
SESSION.headers.update(
    {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) world-bank-infoviz/0.1",
    }
)


def fetch_page(skip: int) -> dict:
    for attempt in range(5):
        try:
            resp = SESSION.post(
                API, json={"query": f"{QUERY}&$skip={skip}"}, timeout=180
            )
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError):
            if attempt == 4:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("unreachable")


def parse_period_end(value: str) -> date | None:
    if not value:
        return None
    value = value.strip()
    try:
        if "-Q" in value:
            year, q = value.split("-Q")
            month = int(q) * 3
            last_day = [31, 30, 30, 31][int(q) - 1]
            return date(int(year), month, last_day)
        parts = value.split("-")
        if len(parts) == 1:
            return date(int(parts[0]), 12, 31)
        if len(parts) == 2:
            year, month = int(parts[0]), int(parts[1])
            if month == 12:
                return date(year, 12, 31)
            return date(year, month + 1, 1).fromordinal(
                date(year, month + 1, 1).toordinal() - 1
            )
        return datetime.fromisoformat(value).date()
    except (ValueError, TypeError):
        return None


def normalize_periodicity(value: str | None) -> str:
    if not value:
        return "Unknown"
    v = value.lower()
    if "annual" in v or "year" in v or v == "ad hoc [adhoc]":
        return "Annual" if "annual" in v else value
    if "quarter" in v:
        return "Quarterly"
    if "month" in v:
        return "Monthly"
    if "week" in v:
        return "Weekly"
    if "daily" in v or "day" in v:
        return "Daily"
    if "triennial" in v:
        return "Triennial"
    if "biennial" in v or "two years" in v:
        return "Biennial"
    return value


def freshness_bucket(period_end: date | None, periodicity: str) -> str:
    if period_end is None:
        return "unknown"
    days = (REFERENCE_DATE - period_end).days
    if days <= 45:
        return "current"
    if days <= 366:
        return "last_12m"
    if days <= 731:
        return "last_24m"
    return "older"


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    seen: set[tuple[str, str]] = set()
    skip = 0
    total = None
    with gzip.open(RAW / "data360_indicators.jsonl.gz", "wt", encoding="utf-8") as raw_out:
        while True:
            payload = fetch_page(skip)
            if total is None:
                total = payload.get("@odata.count")
            page = payload.get("value") or []
            if not page:
                break
            for doc in page:
                sd = doc.get("series_description") or {}
                key = (sd.get("database_id"), sd.get("idno"))
                if key in seen:
                    continue
                seen.add(key)
                rec = {
                    "idno": sd.get("idno"),
                    "name": sd.get("name"),
                    "database_id": sd.get("database_id"),
                    "database_name": sd.get("database_name"),
                    "periodicity": sd.get("periodicity"),
                    "time_periods": sd.get("time_periods"),
                    "topics": sd.get("topics"),
                    "ref_country": sd.get("ref_country"),
                    "measurement_unit": sd.get("measurement_unit"),
                    "date_last_update": sd.get("date_last_update"),
                    "date_released": sd.get("date_released"),
                    "tags": doc.get("tags"),
                }
                records.append(rec)
                raw_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"fetched {len(records)}/{total}", flush=True)
            if len(page) < PAGE:
                break
            skip += PAGE

    db_indicators: Counter[str] = Counter()
    db_names: dict[str, str] = {}
    db_periodicity: dict[str, Counter[str]] = defaultdict(Counter)
    db_coverage: dict[str, list[int]] = defaultdict(list)
    db_span_start: dict[str, date] = {}
    db_span_end: dict[str, date] = {}
    db_topics: Counter[tuple[str, str, str]] = Counter()
    db_regions: dict[str, set[str]] = defaultdict(set)
    db_dates: Counter[str] = Counter()

    per_rows: list[dict] = []
    period_rows: list[dict] = []
    topic_counter: Counter[tuple[str, str, str]] = Counter()
    topic_dbs: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    region_indicators: Counter[str] = Counter()
    region_dbs: dict[str, set[str]] = defaultdict(set)
    region_topics: Counter[tuple[str, str]] = Counter()
    freshness_rows: list[dict] = []

    for rec in records:
        db = rec["database_id"] or "UNKNOWN"
        db_indicators[db] += 1
        if rec.get("database_name") and rec["database_name"] != db:
            db_names[db] = rec["database_name"]

        periods = rec.get("time_periods") or []
        starts = [p.get("start") for p in periods if p.get("start")]
        ends = [p.get("end") for p in periods if p.get("end")]
        start = min(starts) if starts else None
        end = max(ends) if ends else None
        start_d = parse_period_end(start)
        end_d = parse_period_end(end)

        norm_per = normalize_periodicity(rec.get("periodicity"))
        db_periodicity[db][norm_per] += 1

        coverage = len(rec.get("ref_country") or [])
        db_coverage[db].append(coverage)

        if start_d and (db not in db_span_start or start_d < db_span_start[db]):
            db_span_start[db] = start_d
        if end_d and (db not in db_span_end or end_d > db_span_end[db]):
            db_span_end[db] = end_d

        if rec.get("date_last_update"):
            db_dates[db] += 1

        topic_names: dict[str, list[str]] = defaultdict(list)
        for t in rec.get("topics") or []:
            level = TOPIC_VOCAB.get(t.get("vocabulary"), "other")
            name = t.get("name") or t.get("id") or ""
            if name:
                topic_names[level].append(name)
                topic_counter[(level, name, t.get("vocabulary"))] += 1
                topic_dbs[(level, name, t.get("vocabulary"))].add(db)
                db_topics[(db, level, name)] += 1

        rec_regions: set[str] = set()
        for tag in rec.get("tags") or []:
            if tag.get("tag_group") == "overview-region-profile-region":
                rec_regions.add(tag.get("tag"))
                db_regions[db].add(tag.get("tag"))

        for region in rec_regions:
            region_indicators[region] += 1
            region_dbs[region].add(db)
            for l1 in topic_names.get("L1", [])[:1]:
                region_topics[(region, l1)] += 1

        per_rows.append(
            {
                "database_id": db,
                "idno": rec.get("idno"),
                "name": rec.get("name"),
                "periodicity": norm_per,
                "period_start": start,
                "period_end": end,
                "period_end_date": end_d.isoformat() if end_d else "",
                "coverage_economies": coverage,
                "regions": "|".join(sorted(rec_regions)),
                "topic_l0": "|".join(sorted(set(topic_names.get("L0", [])))),
                "topic_l1": "|".join(sorted(set(topic_names.get("L1", [])))),
                "topic_l2": "|".join(sorted(set(topic_names.get("L2", [])))),
                "measurement_unit": rec.get("measurement_unit"),
            }
        )

        if end_d:
            bucket = freshness_bucket(end_d, norm_per)
            freshness_rows.append(
                {
                    "database_id": db,
                    "periodicity": norm_per,
                    "period_end_date": end_d.isoformat(),
                    "bucket": bucket,
                    "coverage_economies": coverage,
                }
            )

    write_csv(
        DERIVED / "indicators.csv",
        [
            "database_id",
            "idno",
            "name",
            "periodicity",
            "period_start",
            "period_end",
            "period_end_date",
            "coverage_economies",
            "regions",
            "topic_l0",
            "topic_l1",
            "topic_l2",
            "measurement_unit",
        ],
        per_rows,
    )

    db_rows = []
    for db, count in sorted(db_indicators.items(), key=lambda kv: (-kv[1], kv[0])):
        cov = db_coverage[db]
        top_topics = db_topics_l1(db_topics, db, limit=3)
        db_rows.append(
            {
                "database_id": db,
                "database_name": db_names.get(db, db),
                "indicators": count,
                "periodicities": "|".join(
                    f"{k}:{v}" for k, v in db_periodicity[db].most_common()
                ),
                "coverage_min": min(cov) if cov else "",
                "coverage_median": statistics.median(cov) if cov else "",
                "coverage_max": max(cov) if cov else "",
                "span_start": db_span_start[db].isoformat() if db in db_span_start else "",
                "span_end": db_span_end[db].isoformat() if db in db_span_end else "",
                "top_l1_topics": " | ".join(top_topics),
                "regions": "|".join(sorted(db_regions[db])),
                "with_last_update": db_dates[db],
            }
        )
    write_csv(DERIVED / "database_summary.csv", list(db_rows[0].keys()), db_rows)

    per_summary = defaultdict(lambda: {"n": 0, "latest": None, "buckets": Counter(), "db": set()})
    for row in freshness_rows:
        key = (row["database_id"], row["periodicity"])
        agg = per_summary[key]
        agg["n"] += 1
        agg["db"].add(row["database_id"])
        agg["buckets"][row["bucket"]] += 1
        d = date.fromisoformat(row["period_end_date"])
        if agg["latest"] is None or d > agg["latest"]:
            agg["latest"] = d
    per_rows_out = []
    for (db, per), agg in sorted(per_summary.items()):
        per_rows_out.append(
            {
                "database_id": db,
                "periodicity": per,
                "indicators": agg["n"],
                "latest_period_end": agg["latest"].isoformat(),
                "current": agg["buckets"]["current"],
                "last_12m": agg["buckets"]["last_12m"],
                "last_24m": agg["buckets"]["last_24m"],
                "older": agg["buckets"]["older"],
            }
        )
    write_csv(DERIVED / "freshness_summary.csv", list(per_rows_out[0].keys()), per_rows_out)

    topic_rows = [
        {
            "level": level,
            "vocabulary": vocab,
            "topic": name,
            "indicators": count,
            "databases": len(topic_dbs[(level, name, vocab)]),
            "database_ids": "|".join(sorted(topic_dbs[(level, name, vocab)]))[:2000],
        }
        for (level, name, vocab), count in topic_counter.most_common()
    ]
    write_csv(DERIVED / "topic_summary.csv", list(topic_rows[0].keys()), topic_rows)

    db_topic_rows = [
        {"database_id": db, "level": level, "topic": name, "indicators": count}
        for (db, level, name), count in db_topics.most_common()
    ]
    write_csv(DERIVED / "database_topics.csv", list(db_topic_rows[0].keys()), db_topic_rows)

    region_rows = []
    for region, count in region_indicators.most_common():
        top = [
            f"{topic}:{n}"
            for (r, topic), n in region_topics.items()
            if r == region
        ]
        top.sort(key=lambda s: -int(s.rsplit(":", 1)[1]))
        region_rows.append(
            {
                "region": region,
                "indicators": count,
                "databases": len(region_dbs[region]),
                "database_ids": "|".join(sorted(region_dbs[region])),
                "top_l1_topics": " | ".join(top[:5]),
            }
        )
    write_csv(DERIVED / "region_summary.csv", list(region_rows[0].keys()), region_rows)

    print(f"\nindicators: {len(records)}  databases with indicators: {len(db_indicators)}")
    print("top databases:")
    for row in db_rows[:15]:
        print(f"  {row['database_id']:<24} {row['indicators']:>5}  {row['top_l1_topics']}")


def db_topics_l1(db_topics: Counter, db: str, limit: int) -> list[str]:
    items = [
        (name, count)
        for (d, level, name), count in db_topics.items()
        if d == db and level == "L1"
    ]
    items.sort(key=lambda kv: (-kv[1], kv[0]))
    return [f"{name}:{count}" for name, count in items[:limit]]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
