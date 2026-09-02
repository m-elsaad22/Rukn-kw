#!/usr/bin/env python3
"""Rename the English hub from /kw/english/ to /kw/en/ and refresh the SEO layer."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/workspace/scripts")
from deploy_kw_seo import activate_wpcode_runtime, rest
from wp_kw_client import TOKEN, cli


def main():
    if not TOKEN:
        print("Missing credentials")
        return 1

    code, pages = rest("/wp/v2/pages&slug=english&parent=0&per_page=5")
    parent = None
    if code == 200 and isinstance(pages, list) and pages:
        parent = pages[0]
    if not parent:
        code, pages = rest("/wp/v2/pages&slug=en&parent=0&per_page=5")
        if code == 200 and isinstance(pages, list) and pages:
            parent = pages[0]
    if not parent:
        print("English hub page not found")
        return 2

    pid = parent["id"]
    slug = parent.get("slug")
    print("HUB", pid, slug, parent.get("link"))
    if slug != "en":
        c, d = rest(f"/wp/v2/pages/{pid}", method="POST", body={"slug": "en"})
        print("rename", c, d.get("slug") if isinstance(d, dict) else d, d.get("link") if isinstance(d, dict) else "")

    # Rewrite leftover /english/ links in published pages (Arabic + English).
    page = 1
    changed = 0
    while True:
        c, data = rest(f"/wp/v2/pages&per_page=100&page={page}&context=edit&status=publish")
        if c != 200 or not isinstance(data, list) or not data:
            break
        for p in data:
            raw = ((p.get("content") or {}).get("raw")) or ""
            if "/kw/english/" not in raw and "/english/" not in raw:
                continue
            new = raw.replace("/kw/english/", "/kw/en/").replace("/english/", "/en/")
            c2, d2 = rest(f"/wp/v2/pages/{p['id']}", method="POST", body={"content": new})
            print("content", p["id"], p.get("slug"), c2, d2.get("link") if isinstance(d2, dict) else "")
            changed += 1
        if len(data) < 100:
            break
        page += 1
    print("pages_rewritten", changed)

    print("=== snippet runtime ===")
    with open("/workspace/scripts/rukn-kw-snippet.php", encoding="utf-8") as f:
        src = f.read()
    if src.startswith("<?php"):
        src = src.split("\n", 1)[-1]
    activate_wpcode_runtime(src)

    print("=== menu ===")
    try:
        items = cli("menu item list 40 --format=json", confirm=False)
        stdout = items.get("stdout") or "[]"
        print("menu items", stdout[:1500])
        parsed = json.loads(stdout) if stdout.strip().startswith("[") else []
        for item in parsed:
            url = str(item.get("url") or item.get("link") or "")
            dbid = item.get("db_id") or item.get("ID") or item.get("id")
            if "english" in url or url.rstrip("/").endswith("/en") or "English" in str(item.get("title") or ""):
                if dbid and "english" in url:
                    print("update menu", dbid, url)
                    print(cli(f"menu item update {dbid} --url=https://rukn-eltatawer.com/kw/en/"))
        print(cli("menu item add-custom 40 English https://rukn-eltatawer.com/kw/en/", confirm=True))
    except Exception as e:
        print("menu err", e)

    print("=== flush ===")
    print(cli("rewrite flush", confirm=True))
    print(cli("litespeed-purge all", confirm=True))
    print(cli("cache flush", confirm=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
