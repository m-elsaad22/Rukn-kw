#!/usr/bin/env python3
"""Publish draft KW posts after replacing phone tokens and broken image src."""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "/workspace/scripts")
from wp_kw_client import BASE, TOKEN

PHONE = "+971586634710"
WA = "971586634710"
ICON = "https://www.rukn-eltatawer.com/wp-content/uploads/icon/cleaning-services.png"
IMG_RE = re.compile(r'src="service-[^"]+\.webp"', re.I)


def rest_json(route, method="GET", body=None, timeout=120):
    url = BASE + route
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Basic {TOKEN}")
    if body is not None:
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            headers = dict(resp.headers)
            raw = resp.read().decode()
            return resp.getcode(), json.loads(raw) if raw else {}, headers
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = raw
        return e.code, parsed, {}


def fix_content(content: str) -> str:
    content = content.replace("{PHONE_RUKN_KUWAIT}", PHONE)
    content = content.replace("{WHATSAPP_RUKN_KUWAIT}", WA)
    content = content.replace("[[رقم الهاتف/واتساب]]", "+971 58 663 4710")
    content = IMG_RE.sub(f'src="{ICON}"', content)
    return content


def fetch_page(page: int, per_page: int = 50):
    route = f"/wp/v2/posts&per_page={per_page}&page={page}&status=draft&context=edit"
    return rest_json(route)


def publish_one(post: dict):
    pid = post["id"]
    raw = (post.get("content") or {}).get("raw") or ""
    new = fix_content(raw)
    body = {
        "status": "publish",
        "content": new,
        "comment_status": "closed",
        "ping_status": "closed",
    }
    code, data, _ = rest_json(f"/wp/v2/posts/{pid}", method="POST", body=body)
    return pid, code, data.get("status") if isinstance(data, dict) else data


def main():
    per_page = 50
    code, data, headers = fetch_page(1, per_page)
    if code != 200:
        print("FAIL page1", code, data)
        return 1
    total = int(headers.get("X-WP-Total") or headers.get("x-wp-total") or 0)
    pages = int(headers.get("X-WP-TotalPages") or headers.get("x-wp-totalpages") or 1)
    print(f"total drafts {total} pages {pages}")
    posts = list(data) if isinstance(data, list) else []
    for p in range(2, pages + 1):
        c, d, _ = fetch_page(p, per_page)
        print(f"fetched page {p} code {c} n={len(d) if isinstance(d, list) else d}")
        if c == 200 and isinstance(d, list):
            posts.extend(d)
        else:
            time.sleep(1)
            c, d, _ = fetch_page(p, per_page)
            if c == 200 and isinstance(d, list):
                posts.extend(d)
    print("loaded", len(posts))

    ok = fail = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(publish_one, p) for p in posts]
        for i, fut in enumerate(as_completed(futs), 1):
            pid, code, status = fut.result()
            if code == 200 and status == "publish":
                ok += 1
            else:
                fail += 1
                if fail <= 8:
                    print("fail", pid, code, status)
            if i % 100 == 0:
                print(f"  {i}/{len(posts)} ok={ok} fail={fail}")
    print("DONE publish", ok, fail, "in", round(time.time() - t0, 1), "s")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
