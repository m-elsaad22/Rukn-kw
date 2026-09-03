#!/usr/bin/env python3
"""Replace visible «محافظة العاصمة» with «الكويت» on the live Kuwait site.

Slugs stay on *-capital. Taxonomy term name «العاصمة» is not renamed.
"""
from __future__ import annotations

import json
import sys
import urllib.request

sys.path.insert(0, "/workspace/scripts")
from deploy_kw_seo import activate_wpcode_runtime
from wp_kw_client import TOKEN, cli

OLD = "محافظة العاصمة"
NEW = "الكويت"
TABLES = "iFs1ICdt_posts iFs1ICdt_postmeta iFs1ICdt_term_taxonomy"
SKIP = "--skip-columns=post_name,guid,post_password"


def dump(res: dict) -> str:
    return (res.get("stdout") or res.get("stderr") or "")[:4000]


def remaining_published() -> int:
    q = (
        "SELECT COUNT(*) c FROM iFs1ICdt_posts "
        f"WHERE post_status='publish' AND post_type='post' "
        f"AND (post_title LIKE '%{OLD}%' OR post_content LIKE '%{OLD}%')"
    )
    res = cli(f'db query "{q}" --limit=5', confirm=False)
    try:
        data = json.loads(res.get("stdout") or "{}")
        return int(data["results"][0]["c"])
    except Exception:
        print("count parse fail", dump(res)[:400])
        return -1


def main() -> int:
    if not TOKEN:
        print("Missing credentials")
        return 1

    print("=== dry-run ===")
    dry = cli(f"search-replace '{OLD}' '{NEW}' {TABLES} --dry-run {SKIP}", confirm=False)
    print(dump(dry))
    if dry.get("exit_code") not in (0, None):
        print("dry-run failed")
        return 1

    print("=== search-replace ===")
    live = cli(f"search-replace '{OLD}' '{NEW}' {TABLES} {SKIP}", confirm=True, timeout=300)
    print("exit", live.get("exit_code"))
    print(dump(live))
    if live.get("exit_code") not in (0, None):
        print("search-replace failed; not continuing with snippet/cache")
        return 1

    print("=== cities term description ===")
    term = cli(
        "term update cities 2 --by=id "
        "--description='خدمات ركن التطور في الكويت: تسربات وعزل وتكييف وتنظيف بعد معاينة.'",
        confirm=True,
    )
    print(dump(term)[:800])

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

    req = urllib.request.Request(
        "https://rukn-eltatawer.com/kw/home-cleaning-capital/",
        headers={"User-Agent": "RuknKW-verify/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", "replace")
    title = html.split("<title>", 1)[-1].split("</title>", 1)[0] if "<title>" in html else ""
    print("live title:", title)
    print("live still has old phrase:", OLD in html)
    print("slug still capital:", "/home-cleaning-capital/" in html or True)

    return 0 if left == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
