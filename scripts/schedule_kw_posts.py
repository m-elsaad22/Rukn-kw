#!/usr/bin/env python3
"""Publish the highest-search Kuwait post now; schedule the rest hourly.

Priority = service search demand (Kuwait) + governorate population/intent.
Already-published posts are moved to `future` so they go live one per hour.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.insert(0, "/workspace/scripts")
from wp_kw_client import BASE, TOKEN

TZ = ZoneInfo("Asia/Kuwait")

# Higher = published sooner. Based on typical Kuwait home-service search intent.
SERVICE_SCORE = {
    "home-cleaning": 100,
    "villa-cleaning": 98,
    "apartment-cleaning": 96,
    "deep-cleaning": 94,
    "water-tank-cleaning": 93,
    "water-leak-detection": 92,
    "water-pipe-leak-detection": 91,
    "drain-unclogging": 90,
    "cockroach-control": 89,
    "termite-control": 88,
    "bed-bug-control": 87,
    "rodent-control": 86,
    "crawling-pest-control": 85,
    "ant-control": 84,
    "mosquito-fly-control": 83,
    "roof-insulation": 82,
    "waterproofing": 81,
    "bathroom-insulation": 80,
    "tank-insulation": 79,
    "thermal-insulation": 78,
    "ac-cleaning-washing": 77,
    "split-ac-maintenance": 76,
    "central-ac-maintenance": 75,
    "ac-freon-refill": 74,
    "ac-periodic-maintenance-contracts": 73,
    "split-ac-installation": 72,
    "home-plumber": 71,
    "plumbing-fault-repair": 70,
    "plumbing-maintenance": 69,
    "home-electrician": 68,
    "electrical-fault-detection": 67,
    "electrical-maintenance": 66,
    "marble-polishing": 65,
    "furniture-moving-packaging": 64,
    "general-maintenance": 63,
    "building-maintenance": 62,
    "kitchen-cleaning": 61,
    "sofa-cleaning": 60,
    "carpet-cleaning": 59,
    "bathroom-cleaning": 58,
    "pool-cleaning": 57,
    "pool-maintenance": 56,
    "painter": 55,
    "interior-painting": 54,
    "villa-painting": 53,
    "humidity-treatment": 52,
    "gas-leak-detection": 51,
    "septic-tank-emptying": 50,
    "new-central-ac-installation": 49,
    "ac-leak-detection": 48,
    "water-heater-maintenance": 47,
    "water-heater-installation": 46,
    "landscaping": 45,
    "artificial-grass": 44,
    "gypsum-board": 43,
    "kitchen-renovation": 42,
    "bathroom-renovation": 41,
}

CITY_SCORE = {
    "capital": 60,
    "hawalli": 50,
    "farwaniya": 40,
    "al-ahmadi": 30,
    "mubarak-al-kabeer": 20,
    "al-jahra": 10,
}

CITY_SUFFIXES = (
    "mubarak-al-kabeer",
    "al-ahmadi",
    "al-jahra",
    "farwaniya",
    "hawalli",
    "capital",
)


def rest(route, method="GET", body=None, timeout=120):
    url = BASE + route
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Basic {TOKEN}")
    if body is not None:
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            return resp.getcode(), json.loads(raw) if raw else {}, dict(resp.headers)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = raw[:400]
        return e.code, parsed, {}


def split_slug(slug: str):
    for city in CITY_SUFFIXES:
        tail = "-" + city
        if slug.endswith(tail):
            return slug[: -len(tail)], city
    return slug, ""


def score_post(slug: str) -> tuple:
    service, city = split_slug(slug)
    s = SERVICE_SCORE.get(service, 20)
    # keyword boosts for remaining long-tail
    for needle, add in (
        ("cleaning", 8),
        ("pest", 8),
        ("control", 4),
        ("leak", 10),
        ("insulation", 9),
        ("ac-", 7),
        ("plumb", 6),
        ("electric", 5),
        ("tank", 6),
        ("moving", 3),
        ("shipping", 1),
        ("freight", 1),
    ):
        if needle in service:
            s += add
    c = CITY_SCORE.get(city, 0)
    return (-(s + c), city != "capital", service, city, slug)


def fetch_all(status="publish"):
    posts = []
    page = 1
    while True:
        code, data, headers = rest(
            f"/wp/v2/posts&per_page=100&page={page}&status={status}&_fields=id,slug,title,status,date"
        )
        if code != 200:
            raise RuntimeError(f"list {status} page {page}: {code} {data}")
        posts.extend(data)
        pages = int(headers.get("X-WP-TotalPages") or headers.get("x-wp-totalpages") or 1)
        if page >= pages:
            break
        page += 1
    return posts


def set_future(pid: int, when: datetime):
    local = when.strftime("%Y-%m-%dT%H:%M:%S")
    code, data, _ = rest(
        f"/wp/v2/posts/{pid}",
        method="POST",
        body={"status": "future", "date": local, "date_gmt": when.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S")},
    )
    return pid, code, data.get("status") if isinstance(data, dict) else data, data.get("date") if isinstance(data, dict) else ""


def main():
    if not TOKEN:
        print("Missing credentials")
        return 1

    published = fetch_all("publish")
    drafts = []
    try:
        drafts = fetch_all("draft")
    except Exception as e:
        print("drafts fetch", e)

    pool = published + drafts
    print(f"publish={len(published)} draft={len(drafts)}")
    ranked = sorted(pool, key=lambda p: score_post(p.get("slug") or ""))
    if not ranked:
        print("no posts")
        return 1

    first = ranked[0]
    queued = ranked[1:]
    print("KEEP/PUBLISH NOW", first["id"], first["slug"], first.get("title", {}).get("rendered"))

    now = datetime.now(TZ).replace(minute=0, second=0, microsecond=0)
    code, data, _ = rest(
        f"/wp/v2/posts/{first['id']}",
        method="POST",
        body={"status": "publish", "date": now.strftime("%Y-%m-%dT%H:%M:%S")},
    )
    print("first publish", code, data.get("status") if isinstance(data, dict) else data)

    start = now + timedelta(hours=1)
    jobs = []
    for i, post in enumerate(queued):
        when = start + timedelta(hours=i)
        jobs.append((post["id"], post["slug"], when))

    print(f"scheduling {len(jobs)} posts hourly from {start.isoformat()} to {jobs[-1][2].isoformat() if jobs else '-'}")

    ok = fail = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(set_future, pid, when): (pid, slug, when) for pid, slug, when in jobs}
        for n, fut in enumerate(as_completed(futs), 1):
            pid, slug, when = futs[fut]
            try:
                pid, code, status, date = fut.result()
            except Exception as e:
                fail += 1
                print("ERR", pid, slug, e)
                continue
            if code in (200, 201) and status == "future":
                ok += 1
            else:
                fail += 1
                print("FAIL", pid, slug, code, status)
            if n % 100 == 0:
                print(f"progress {n}/{len(jobs)} ok={ok} fail={fail}")

    print(f"DONE scheduled_ok={ok} fail={fail} live={first['slug']}")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
