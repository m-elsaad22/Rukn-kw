#!/usr/bin/env python3
"""Rename *-capital slugs to *-kuwait and drop «شركة» from technician titles.

Customers search Kuwait, not Capital, and they search for a plumber/electrician
not a company. Old /kw/*-capital/ URLs 301 to /kw/*-kuwait/ via the SEO snippet.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "/workspace/scripts")
from deploy_kw_seo import activate_wpcode_runtime
from wp_kw_client import BASE, TOKEN, cli

WORKERS = 6
TECH_PREFIXES = (
    "شركة سباك%",
    "شركة كهربائي%",
    "شركة نجار%",
    "شركة فني%",
    "شركة حداد%",
    "شركة عامل%",
)
REPLACEMENTS = (
    ("شركة فني", "فني"),
    ("شركة كهربائي", "كهربائي"),
    ("شركة سباك", "سباك"),
    ("شركة نجار", "نجار"),
    ("شركة حداد", "حداد"),
    ("شركة عامل دهانات", "عامل دهانات"),
    ("ما هي سباك", "من هو سباك"),
    ("ما هي كهربائي", "من هو كهربائي"),
    ("ما هي نجار", "من هو نجار"),
    ("ما هي فني", "من هو فني"),
    ("ما هي حداد", "من هو حداد"),
    ("ما هي عامل", "من هو عامل"),
)
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


def rewrite_text(text: str) -> str:
    if not text:
        return text
    out = text
    for old, new in REPLACEMENTS:
        out = out.replace(old, new)
    return out


def dump(res: dict) -> str:
    return (res.get("stdout") or res.get("stderr") or "")[:800]


def rename_slug(pid: int, old_slug: str) -> tuple[int, str]:
    if not old_slug.endswith("-capital"):
        return pid, "skip"
    new_slug = old_slug[: -len("-capital")] + "-kuwait"
    code, data = rest(f"/wp/v2/posts/{pid}", method="POST", body={"slug": new_slug})
    got = data.get("slug") if isinstance(data, dict) else ""
    if code != 200 or got != new_slug:
        return pid, f"slug {old_slug} -> {got or data} http={code}"
    return pid, "ok"


def rewrite_post(pid: int) -> tuple[int, str]:
    code, post = rest(f"/wp/v2/posts/{pid}&context=edit")
    if code != 200 or not isinstance(post, dict):
        return pid, f"fetch {code} {str(post)[:180]}"
    title = (post.get("title") or {}).get("raw") or ""
    content = (post.get("content") or {}).get("raw") or ""
    body = {}
    new_title = rewrite_text(title)
    new_content = rewrite_text(content)
    if new_title != title:
        body["title"] = new_title
    if new_content != content:
        body["content"] = new_content
    if not body:
        return pid, "no-op"
    code2, data2 = rest(f"/wp/v2/posts/{pid}", method="POST", body=body)
    if code2 != 200:
        return pid, f"update {code2} {str(data2)[:180]}"
    return pid, "ok"


def update_meta_row(post_id: str, key: str, value: str) -> str:
    new_val = rewrite_text(value)
    if new_val == value:
        return "skip"
    res = cli(f"post meta update {post_id} {key} '{new_val}' --force", confirm=True)
    if res.get("exit_code") not in (0, None):
        return dump(res)
    return "ok"


def run_pool(func, items, label: str) -> int:
    if not items:
        print(label, "nothing to do")
        return 0
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = [pool.submit(func, *item) if isinstance(item, tuple) else pool.submit(func, item) for item in items]
        for i, fut in enumerate(as_completed(futs), 1):
            pid, msg = fut.result()
            if msg in ("ok", "no-op", "skip"):
                ok += 1
            else:
                fail += 1
                print("FAIL", pid, msg)
            if i % 25 == 0 or i == len(items):
                print(f"{label} {i}/{len(items)} ok={ok} fail={fail}")
    return fail


def main() -> int:
    if not TOKEN:
        print("Missing credentials")
        return 1

    print("=== rename *-capital slugs to *-kuwait ===")
    slug_rows = db_query(
        "SELECT ID, post_name FROM iFs1ICdt_posts "
        "WHERE post_type='post' AND post_status='publish' AND post_name LIKE '%-capital'"
    )
    print("capital slugs", len(slug_rows))
    fail = run_pool(
        rename_slug,
        [(int(r["ID"]), r["post_name"]) for r in slug_rows],
        "slugs",
    )
    if fail:
        return 1

    print("=== technician titles and content ===")
    like = " OR ".join(f"post_title LIKE '{p}'" for p in TECH_PREFIXES)
    tech_rows = db_query(
        "SELECT ID FROM iFs1ICdt_posts "
        f"WHERE post_type='post' AND post_status='publish' AND ({like})"
    )
    tech_ids = [int(r["ID"]) for r in tech_rows]
    print("technician posts", len(tech_ids))
    fail = run_pool(rewrite_post, tech_ids, "tech posts")
    if fail:
        return 1

    print("=== technician Rank Math meta ===")
    meta_like = " OR ".join(f"meta_value LIKE '%{old}%'" for old, _new in REPLACEMENTS[:6])
    meta_rows = db_query(
        "SELECT post_id, meta_key, meta_value FROM iFs1ICdt_postmeta "
        f"WHERE meta_key IN ('rank_math_title','rank_math_description','rank_math_focus_keyword') "
        f"AND ({meta_like})"
    )
    print("meta rows", len(meta_rows))
    meta_fail = 0
    for row in meta_rows:
        msg = update_meta_row(row["post_id"], row["meta_key"], row["meta_value"])
        if msg not in ("ok", "skip"):
            meta_fail += 1
            print("META FAIL", row["post_id"], row["meta_key"], msg)
    if meta_fail:
        return 1

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

    left_slugs = db_query(
        "SELECT COUNT(*) c FROM iFs1ICdt_posts "
        "WHERE post_type='post' AND post_status='publish' AND post_name LIKE '%-capital'"
    )
    left_tech = db_query(
        "SELECT COUNT(*) c FROM iFs1ICdt_posts "
        f"WHERE post_type='post' AND post_status='publish' AND ({like})"
    )
    print("remaining -capital slugs", left_slugs[0]["c"] if left_slugs else "?")
    print("remaining شركة technician titles", left_tech[0]["c"] if left_tech else "?")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
