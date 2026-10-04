#!/usr/bin/env python3
"""Apply Kuwait site fixes EXCEPT SEO titles (rental listing titles stay).

Requires RUKN_WP_USER + RUKN_WP_APP_PASSWORD.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_kw_client import cli, rest

ROOT = Path(__file__).resolve().parent
SNIPPET = ROOT / "rukn-kw-head-min.php"
ORIGIN = "https://www.rukn-eltatawer.com/kw"


def out(cmd, confirm=True):
    r = cli(cmd, confirm=confirm)
    print(cmd[:120], "->", (r.get("stdout") or r.get("stderr") or "")[:300])
    return r


def deploy_head_snippet():
    """WPVibe CLI blocks ';' so the snippet must be semicolon-free PHP."""
    code = SNIPPET.read_text(encoding="utf-8")
    if code.startswith("<?php"):
        code = code.split("\n", 1)[-1]
    code = code.strip()
    if ";" in code:
        raise SystemExit("head snippet contains ';' — WPVibe option update would reject it")
    item = {
        "id": 3811,
        "title": "Rukn KW fixpack",
        "code": code,
        "code_type": "php",
        "location": "everywhere",
        "auto_insert": 1,
        "insert_number": 1,
        "use_rules": False,
        "rules": {},
        "priority": 5,
        "active": True,
        "device_type": "any",
    }
    raw = json.dumps({"everywhere": [item]}, ensure_ascii=False, separators=(",", ":"))
    if ";" in raw or "'" in raw:
        raise SystemExit("serialized snippet JSON is not CLI-safe")
    out(f"option update wpcode_snippets '{raw}' --format=json")


def patch_pages():
    for pid, body in ((3825, {"parent": 0}),):
        try:
            r = rest(f"/wp/v2/pages/{pid}", method="POST", body=body)
            print("PAGE", pid, r.get("slug"), r.get("link"))
        except Exception as e:
            print("PAGE FAIL", pid, e)
    cnew = (
        "<h2>تواصل عبر واتساب</h2>"
        "<p>فريق ركن التطور يخدم محافظات الكويت. راسلنا واتساب على الخط الإقليمي الحالي أو عبر البريد.</p>"
        '<p><a href="https://wa.me/971586634710">واتساب ركن التطور الكويت</a></p>'
        '<p>البريد: <a href="mailto:m@rukn-eltatawer.com">m@rukn-eltatawer.com</a></p>'
        "<p>التغطية: العاصمة، حولي، الفروانية، الأحمدي، الجهراء، مبارك الكبير.</p>"
    )
    rest("/wp/v2/pages/1279", method="POST", body={"content": cnew})
    print("contact page updated")


def patch_menus():
    try:
        out("menu item update 3874 --link=https://www.rukn-eltatawer.com/kw/en/ --parent-id=0 --position=5")
    except Exception as e:
        print("menu 3874", e)
    existing = out("menu item list 74 --format=json", confirm=False)
    have = set()
    try:
        have = {str(x.get("title")) for x in json.loads(existing.get("stdout") or "[]")}
    except Exception:
        have = set()
    for title, url in (
        ("Home", f"{ORIGIN}/en/"),
        ("About", f"{ORIGIN}/en/about/"),
        ("Services", f"{ORIGIN}/en/services/"),
        ("Contact", f"{ORIGIN}/en/contact/"),
        ("العربية", f"{ORIGIN}/"),
    ):
        if title in have:
            continue
        try:
            out(f"menu item add-custom 74 {title} {url}")
        except Exception as e:
            print("menu add", title, e)


def main():
    print("=== snippet ===")
    deploy_head_snippet()
    print("=== pages ===")
    patch_pages()
    print("=== menus ===")
    patch_menus()
    try:
        out("rewrite flush")
    except Exception as e:
        print("rewrite", e)
    try:
        out("litespeed-purge all")
    except Exception as e:
        print("purge", e)
    print("done")


if __name__ == "__main__":
    raise SystemExit(main() or 0)
