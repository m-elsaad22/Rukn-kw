#!/usr/bin/env python3
"""Apply the Kuwait /kw WordPress fixes that require admin REST access.

Usage:
  WP_USER=cursor WP_APP_PASSWORD='xxxx xxxx xxxx xxxx xxxx xxxx' \\
    python3 scripts/apply_kuwait_wp_fixes.py

Optional:
  WP_BASE=https://rukn-eltatawer.com/kw
  PHONE_RUKN_KUWAIT=+971586634710
  WHATSAPP_RUKN_KUWAIT=971586634710
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

BASE = os.environ.get("WP_BASE", "https://rukn-eltatawer.com/kw").rstrip("/")
USER = os.environ.get("WP_USER", "cursor")
APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "").strip()
PHONE = os.environ.get("PHONE_RUKN_KUWAIT", "+971586634710")
WHATSAPP = os.environ.get("WHATSAPP_RUKN_KUWAIT", "971586634710")


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def request(method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
    url = path if path.startswith("http") else f"{BASE}{path}"
    headers = {
        "User-Agent": "RuknKuwaitFixer/1.0",
        "Accept": "application/json",
        "Authorization": "Basic "
        + base64.b64encode(f"{USER}:{APP_PASSWORD}".encode()).decode(),
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8", "replace")
            try:
                return resp.status, json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            body: Any = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = raw
        return exc.code, body


def wpvibe_edit_option(option_name: str, new_content: str) -> tuple[int, Any]:
    return request(
        "POST",
        "/wp-json/wpvibe/v1/content/edit",
        {
            "target_type": "option",
            "option_name": option_name,
            "field": "value",
            "old_content": "",
            "new_content": new_content,
            "replace_all": True,
        },
    )


def main() -> int:
    if not APP_PASSWORD:
        die("Set WP_APP_PASSWORD to a WordPress application password for user `cursor`.")

    status, me = request("GET", "/wp-json/wp/v2/users/me?context=edit")
    if status != 200:
        die(f"auth failed ({status}): {me}")

    print("authenticated as", me.get("slug"), me.get("name"), "roles=", me.get("roles"))
    caps = me.get("capabilities") or {}
    if not caps.get("manage_options") and "administrator" not in (me.get("roles") or []):
        print("warning: account may lack manage_options; option writes can fail")

    digits = "".join(ch for ch in PHONE if ch.isdigit())
    wa_digits = "".join(ch for ch in WHATSAPP if ch.isdigit()) or digits

    option_updates = {
        "phonenumber": PHONE,
        "contact_number": PHONE,
        "whatsapp_number": wa_digits,
        "kayan_show_call_buttons": "1",
        "kayan_seo_locale": "ar_KW",
        "kayan_seo_latitude": "29.375859",
        "kayan_seo_longitude": "47.977405",
        "kayan_seo_hreflang_enabled": "1",
    }

    for name, value in option_updates.items():
        code, body = wpvibe_edit_option(name, value)
        print(f"option {name} -> {code} {body if code != 200 else 'ok'}")

    # English home slug `en` collides with Polylang's /en/ prefix.
    code, page = request("GET", "/wp-json/wp/v2/pages/3819?context=edit")
    if code == 200 and page.get("slug") == "en":
        code, body = request("POST", "/wp-json/wp/v2/pages/3819", {"slug": "home"})
        print(f"rename EN home slug en -> home: {code} {body if code >= 400 else 'ok'}")
    else:
        print(f"EN home page 3819 status={code} slug={page.get('slug') if isinstance(page, dict) else page}")

    dni_code, dni = request("GET", "/wp-json/kayan/v1/dni")
    print("kayan dni after updates:", dni_code, dni)

    ping_code, ping = request("GET", "/wp-json/wpvibe/v1/site-info")
    if ping_code != 200:
        print("wpvibe site-info still blocked:", ping)
        print("If option writes failed, paste the numbers in Theme Options + Kayan Track manually.")
    else:
        print("wpvibe site-info reachable")

    print("done. remaining manual steps: Polylang front pages, Rank Math sitemap 404, service_categories, snippets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
