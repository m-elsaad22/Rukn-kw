#!/usr/bin/env python3
"""Publish scripts/rukn-kw-fixpack.php into WPCode snippet cache 3811."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_kuwait_full_fixes import APP_PASSWORD, cli, request, stdout_json  # noqa: E402


def main() -> int:
    if not APP_PASSWORD:
        raise SystemExit("Set WP_APP_PASSWORD")
    st, me = request("GET", "/wp-json/wp/v2/users/me?context=edit")
    print("auth", st, (me or {}).get("slug") if isinstance(me, dict) else me)
    if st != 200:
        return 1

    src = (ROOT / "scripts" / "rukn-kw-fixpack.php").read_text(encoding="utf-8")
    src = src.replace("<?php", "", 1).strip()
    print("fixpack chars", len(src))
    marker = "20260923d" if "20260923d" in src else "unknown"
    print("marker", marker)

    cache = {
        "everywhere": [
            {
                "id": 3811,
                "title": "Rukn KW fixpack",
                "code": src,
                "code_type": "php",
                "location": "everywhere",
                "auto_insert": 1,
                "insert_number": 1,
                "use_rules": False,
                "rules": [],
                "priority": 10,
                "location_extra": "",
                "shortcode_attributes": [],
                "compiled_code": "",
                "modified": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            }
        ]
    }
    cmd = (
        "option update wpcode_snippets "
        + json.dumps(json.dumps(cache, ensure_ascii=False))
        + " --format=json"
    )
    st, body = cli(cmd, write=True, timeout=180)
    out = (body or {}).get("stdout", body) if isinstance(body, dict) else body
    print("wpcode_snippets", st, str(out)[:400])
    if st not in (200, 201):
        return 1

    replacements = {
        "https://www.rukn-eltatawer.com/kw/": "https://rukn-eltatawer.com/kw/",
        "https://www.rukn-eltatawer.com/wp-content/uploads/icon/setting.png": (
            "https://rukn-eltatawer.com/kw/wp-content/uploads/2026/09/logo.webp"
        ),
        "جميع إمارات الدولة السبع بلا استثناء": "جميع محافظات الكويت بلا استثناء",
        "إمارات الدولة السبع": "محافظات الكويت الست",
        "سجل حافل في السوق الإماراتي": "سجل حافل في السوق الكويتي",
        "في جميع أنحاء الإمارات": "في جميع أنحاء الكويت",
        "في مختلف إمارات الإمارات": "في مختلف محافظات الكويت",
        "خدماتنا في جميع {%إمارات الدولة%}": "خدماتنا في جميع {%محافظات الكويت%}",
        "أينما كنت في الإمارات": "أينما كنت في الكويت",
        "تغطية كاملة لـ 7 إمارات": "تغطية كاملة لـ 6 محافظات",
        "فريق محلي في كل إمارة": "فريق محلي في كل محافظة",
        "المعايير المعتمدة في دولة الإمارات": "المعايير المعتمدة في دولة الكويت",
        "رقم تسجيل ضريبي (VAT) رسمي وفواتير نظامية": "فواتير واضحة بالدينار الكويتي بعد المعاينة",
        "فيلا — دبي مارينا": "فيلا — مدينة الكويت",
        "فيلا — البرشاء": "فيلا — حولي",
        "مبنى — الشارقة": "مبنى — الفروانية",
        "دبي مارينا": "مدينة الكويت",
        "7 إمارات": "6 محافظات",
    }

    def scrub(value):
        if isinstance(value, dict):
            return {k: scrub(v) for k, v in value.items()}
        if isinstance(value, list):
            return [scrub(v) for v in value]
        if not isinstance(value, str):
            return value
        for old, new in replacements.items():
            value = value.replace(old, new)
        if value == "البرشاء":
            return "حولي"
        if value == "الشارقة":
            return "الفروانية"
        return value

    st, intro_body = cli("option get HomeIntro --format=json")
    intro = stdout_json(intro_body)
    if isinstance(intro, dict) and "SelectedModel" in intro:
        intro = scrub(intro)
        intro.setdefault("slider_intro_v1", {})["hide_call_button"] = "on"
        st, body = cli(
            "option update HomeIntro "
            + json.dumps(json.dumps(intro, ensure_ascii=False))
            + " --format=json",
            write=True,
        )
        print("HomeIntro", st, str(body)[:180])

    print("flush", cli("cache flush", write=True)[1])
    print("purge", cli("litespeed-purge all", write=True)[1])
    print("rewrite", cli("rewrite flush", write=True)[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
