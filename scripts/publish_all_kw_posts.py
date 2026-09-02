#!/usr/bin/env python3
"""Publish every remaining future Kuwait post now.

Sets status=publish and a current Kuwait datetime so WordPress does not
keep the row as future. Concurrency stays modest to avoid 500s.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, "/workspace/scripts")
from wp_kw_client import BASE, TOKEN

TZ = ZoneInfo("Asia/Kuwait")
WORKERS = 8


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
            parsed = raw[:300]
        return e.code, parsed, {}
    except Exception as e:
        return 0, str(e), {}


def fetch_all(status: str):
    posts = []
    page = 1
    while True:
        code, data, headers = rest(
            f"/wp/v2/posts&per_page=100&page={page}&status={status}&_fields=id,slug,status,date"
        )
        if code != 200:
            raise RuntimeError(f"list {status} page {page}: {code} {data}")
        posts.extend(data)
        pages = int(headers.get("X-WP-TotalPages") or headers.get("x-wp-totalpages") or 1)
        if page >= pages:
            break
        page += 1
    return posts


def publish_one(pid: int, when: str):
    last = None
    for attempt in range(3):
        code, data, _ = rest(
            f"/wp/v2/posts/{pid}",
            method="POST",
            body={"status": "publish", "date": when},
        )
        status = data.get("status") if isinstance(data, dict) else data
        if code in (200, 201) and status == "publish":
            return pid, code, status
        last = (code, status)
        time.sleep(0.8 * (attempt + 1))
    return pid, last[0] if last else 0, last[1] if last else "error"


def main():
    if not TOKEN:
        print("Missing credentials")
        return 1

    future = fetch_all("future")
    published = fetch_all("publish")
    print(f"before publish={len(published)} future={len(future)}", flush=True)
    if not future:
        print("nothing to publish")
        return 0

    when = datetime.now(TZ).replace(second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(publish_one, p["id"], when): p for p in future}
        for n, fut in enumerate(as_completed(futs), 1):
            post = futs[fut]
            try:
                pid, code, status = fut.result()
            except Exception as e:
                fail += 1
                print("ERR", post["id"], post.get("slug"), e, flush=True)
                continue
            if status == "publish":
                ok += 1
            else:
                fail += 1
                print("FAIL", pid, post.get("slug"), code, status, flush=True)
            if n % 100 == 0 or n == len(futs):
                print(f"progress {n}/{len(futs)} ok={ok} fail={fail}", flush=True)

    after_pub = fetch_all("publish")
    after_fut = fetch_all("future")
    print(
        f"DONE ok={ok} fail={fail} publish={len(after_pub)} future={len(after_fut)}",
        flush=True,
    )
    return 0 if fail == 0 and not after_fut else 2


if __name__ == "__main__":
    raise SystemExit(main())
