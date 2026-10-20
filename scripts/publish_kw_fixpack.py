#!/usr/bin/env python3
"""Publish scripts/rukn-kw-fixpack.php into WPCode snippet 3811.

WPVibe now blocks `option update wpcode_snippets`. The supported write path is
POST /wp-json/wpvibe/v1/code-snippet, which requires a current WPVibe-signed
approval in the connected browser panel.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_kuwait_full_fixes import APP_PASSWORD, cli, request  # noqa: E402


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
    if "20261020a" not in src:
        raise SystemExit("refusing to publish fixpack without GSC marker 20261020a")

    st, body = request(
        "POST",
        "/wp-json/wpvibe/v1/code-snippet",
        {
            "action": "update",
            "id": 3811,
            "code": src,
            "title": "Rukn KW fixpack",
            "code_type": "php",
            "location": "everywhere",
            "insert_method": "auto",
        },
        timeout=180,
    )
    print("code-snippet", st, str(body)[:500])
    if st not in (200, 201):
        print(
            "WPCode 3811 was not updated. Keep WPVibe connected and approve the "
            "code_snippet operation, then re-run this script."
        )
        return 1

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
    print("wpcode_snippets fallback", st, str(body)[:300])

    print("flush", cli("cache flush", write=True)[1])
    print("purge", cli("litespeed-purge all", write=True)[1])
    print("rewrite", cli("rewrite flush", write=True)[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
