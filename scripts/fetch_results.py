#!/usr/bin/env python3
"""Pull NP Enduro Samobor results from my.raceresult.com and write data/results.json.

    python3 scripts/fetch_results.py
"""
import json, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

EVENT_ID = 426482
PAGE = "results"
LIST = "Results|>>Stages - ukupno / print"
N_STAGES = 5
OUT = Path(__file__).resolve().parent.parent / "data" / "results.json"


def get(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def parse_time(s):
    """'01:58,73' / '1:02:03,5' / '+9:34,87' / '-' -> seconds or None."""
    if not s:
        return None
    s = s.strip().lstrip("+").replace(",", ".")
    if not s or s == "-" or not re.fullmatch(r"[\d:.]+", s):
        return None
    total = 0.0
    for p in s.split(":"):
        total = total * 60 + float(p)
    return round(total, 2)


def flatten(data, path=()):
    if isinstance(data, list):
        for row in data:
            yield path, row
    else:
        for key, val in data.items():
            yield from flatten(val, path + (key.split("_", 1)[1] if "_" in key else key,))


def main():
    cfg = get(f"https://my.raceresult.com/{EVENT_ID}/{PAGE}/config", {"lang": "en"})
    server = "https://" + cfg.get("server", "my.raceresult.com")
    d = get(f"{server}/{EVENT_ID}/{PAGE}/list", {
        "key": cfg["key"], "page": PAGE, "r": "all", "l": 0, "listname": LIST, "contest": 0})
    riders = []
    for path, row in flatten(d["data"]):
        category = path[0] if path else ""
        stages = []
        for i in range(N_STAGES):
            cell = row[6 + i]
            m = re.match(r"\s*([\d:,]+)\s*\((\d+)\.\)", cell or "")
            stages.append({"time": parse_time(m.group(1)), "rank": int(m.group(2))} if m else None)
        status = row[11].strip()
        total = parse_time(status)
        rank = re.sub(r"\D", "", row[2])
        riders.append({
            "bib": int(row[0]),
            "name": row[4].strip(),
            "club": "" if row[5].strip() in ("", "N/A") else row[5].strip(),
            "category": category,
            "gender": "f" if "157,25,13" in row[-1] else "m",
            "rank": int(rank) if rank else None,
            "status": "" if total is not None else status,
            "total": total,
            "stages": stages,
        })
    out = {
        "event": cfg.get("eventname", "").rstrip("."),
        "eventId": EVENT_ID,
        "date": "2026-10-11",
        "source": f"https://my.raceresult.com/{EVENT_ID}/results",
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "eventOver": bool(cfg.get("EventOver")),
        "stages": N_STAGES,
        "categories": list(cfg.get("contests", {}).values()),
        "riders": sorted(riders, key=lambda r: (r["category"], r["rank"] or 9999, r["bib"])),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"wrote {OUT}: {len(riders)} riders")


if __name__ == "__main__":
    sys.exit(main())
