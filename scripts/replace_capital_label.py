#!/usr/bin/env python3
"""Replace visible «محافظة العاصمة» with «الكويت» on the live Kuwait site.

Post slugs are renamed separately to *-kuwait. Taxonomy term name «العاصمة»
is not renamed. WPVibe search-replace is 409-gated, so this uses REST.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "/workspace/scripts")
from deploy_kw_seo import activate_wpcode_runtime
from wp_kw_client import BASE, TOKEN, cli

OLD = "محافظة العاصمة"
NEW = "الكويت"
WORKERS = 6
META_KEYS = ("rank_math_title", "rank_math_description", "rank_math_focus_keyword")


def rest(route, method="GET", body=None, timeout=180):
    url = BASE + route
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Basic {TOKEN}")
    if body is not None:
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            return resp.getcode(), json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = raw[:2000]
        return e.code, parsed


def db_query(sql: str, limit: int = 800) -> list[dict]:
    res = cli(f'db query "{sql}" --limit={limit}', confirm=False)
    try:
        data = json.loads(res.get("stdout") or "{}")
        return data.get("results") or []
    except Exception:
        print("db parse fail", (res.get("stdout") or res.get("stderr") or "")[:400])
        return []


def dump(res: dict) -> str:
    return (res.get("stdout") or res.get("stderr") or "")[:2000]


def remaining_published() -> int:
    rows = db_query(
        "SELECT COUNT(*) c FROM iFs1ICdt_posts "
        "WHERE post_status='publish' AND post_type='post' "
        f"AND (post_title LIKE '%{OLD}%' OR post_content LIKE '%{OLD}%')"
    )
    if not rows:
        return -1
    return int(rows[0]["c"])


def update_post(pid: int) -> tuple[int, str]:
    code, post = rest(f"/wp/v2/posts/{pid}&context=edit")
    if code != 200 or not isinstance(post, dict):
        return pid, f"fetch {code} {str(post)[:180]}"
    title = (post.get("title") or {}).get("raw") or ""
    content = (post.get("content") or {}).get("raw") or ""
    slug = post.get("slug") or ""
    body = {}
    if OLD in title:
        body["title"] = title.replace(OLD, NEW)
    if OLD in content:
        body["content"] = content.replace(OLD, NEW)
    if not body:
        return pid, "no-op"
    code2, data2 = rest(f"/wp/v2/posts/{pid}", method="POST", body=body)
    new_slug = data2.get("slug") if isinstance(data2, dict) else ""
    if new_slug and new_slug != slug:
        return pid, f"SLUG CHANGED {slug} -> {new_slug}"
    if code2 != 200:
        return pid, f"update {code2} {str(data2)[:180]}"
    return pid, "ok"


def update_meta_row(post_id: str, key: str, value: str) -> str:
    if OLD not in value:
        return "skip"
    new_val = value.replace(OLD, NEW)
    # Values are Arabic SEO strings; they do not contain single quotes.
    res = cli(f"post meta update {post_id} {key} '{new_val}' --force", confirm=True)
    if res.get("exit_code") not in (0, None):
        return dump(res)[:200]
    return "ok"


def main() -> int:
    if not TOKEN:
        print("Missing credentials")
        return 1

    print("=== published posts still using old phrase ===")
    ids = [
        int(r["ID"])
        for r in db_query(
            "SELECT ID FROM iFs1ICdt_posts WHERE post_status='publish' "
            f"AND post_type='post' AND (post_title LIKE '%{OLD}%' OR post_content LIKE '%{OLD}%')"
        )
    ]
    print("count", len(ids))
    if ids:
        ok = fail = 0
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futs = [pool.submit(update_post, pid) for pid in ids]
            for i, fut in enumerate(as_completed(futs), 1):
                pid, msg = fut.result()
                if msg == "ok" or msg == "no-op":
                    ok += 1
                else:
                    fail += 1
                    print("FAIL", pid, msg)
                if i % 25 == 0 or i == len(ids):
                    print(f"progress {i}/{len(ids)} ok={ok} fail={fail}")
        print("post updates ok", ok, "fail", fail)
        if fail:
            return 1

    print("=== rank math meta ===")
    meta_rows = db_query(
        "SELECT post_id, meta_key, meta_value FROM iFs1ICdt_postmeta "
        f"WHERE meta_value LIKE '%{OLD}%' AND meta_key IN "
        "('rank_math_title','rank_math_description','rank_math_focus_keyword')"
    )
    print("meta rows", len(meta_rows))
    meta_fail = 0
    for row in meta_rows:
        msg = update_meta_row(row["post_id"], row["meta_key"], row["meta_value"])
        if msg not in ("ok", "skip"):
            meta_fail += 1
            print("META FAIL", row["post_id"], row["meta_key"], msg)
    print("meta fail", meta_fail)
    if meta_fail:
        return 1

    print("=== cities term description ===")
    term = cli(
        "term update cities 2 --by=id "
        "--description='خدمات ركن التطور في الكويت: تسربات وعزل وتكييف وتنظيف بعد معاينة.'",
        confirm=True,
    )
    print(dump(term)[:500])

    print("=== snippet runtime ===")
    with open("/workspace/scripts/rukn-kw-snippet.php", encoding="utf-8") as f:
        code_src = f.read()
    if code_src.startswith("<?php"):
        code_src = code_src.split("\n", 1)[-1]
    activate_wpcode_runtime(code_src)

    print("=== purge cache ===")
    for cmd in ("litespeed-purge all", "cache flush"):
        res = cli(cmd, confirm=True)
        print(cmd, res.get("exit_code"), dump(res)[:200])

    left = remaining_published()
    print("published posts still containing old phrase:", left)

    sample = cli("post get 31 --fields=ID,post_title,post_name", confirm=False)
    print("sample post 31", dump(sample)[:500])

    time.sleep(2)
    req = urllib.request.Request(
        "https://rukn-eltatawer.com/kw/home-cleaning-capital/",
        headers={"User-Agent": "RuknKW-verify/1.0", "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", "replace")
    title = html.split("<title>", 1)[-1].split("</title>", 1)[0] if "<title>" in html else ""
    print("live title:", title)
    print("live still has old phrase:", OLD in html)

    return 0 if left == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
