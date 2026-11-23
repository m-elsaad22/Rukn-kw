#!/usr/bin/env python3
"""Save WPCode snippet 3811 via wp-admin so location=everywhere actually runs."""
from __future__ import annotations

import http.cookiejar
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

ORIGIN = "https://www.rukn-eltatawer.com"
LOGIN = f"{ORIGIN}/kw/wp-login.php"
ADMIN = f"{ORIGIN}/kw/wp-admin/"
EDITOR = f"{ADMIN}admin.php?page=wpcode-snippet-manager&snippet_id=3811"
USER = "cursor"
PASSWORD = "Cursor@curso12"
CTX = ssl.create_default_context()
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36"
CODE = (Path(__file__).resolve().parent / "rukn-kw-runtime.php").read_text(encoding="utf-8")


def opener():
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar),
        urllib.request.HTTPSHandler(context=CTX),
    )


def fetch(op, url, data=None, headers=None):
    hdrs = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"}
    if headers:
        hdrs.update(headers)
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data, doseq=True).encode()
        hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
    req = urllib.request.Request(url, data=body, headers=hdrs)
    try:
        with op.open(req, timeout=120) as r:
            return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.geturl(), e.read()


def main():
    op = opener()
    fetch(op, LOGIN)
    status, url, raw = fetch(
        op,
        LOGIN,
        data={
            "log": USER,
            "pwd": PASSWORD,
            "wp-submit": "Log In",
            "redirect_to": ADMIN,
            "testcookie": "1",
        },
        headers={"Referer": LOGIN},
    )
    if "wp-admin" not in url or "wp-login.php" in url:
        print("LOGIN FAIL", status, url)
        return 1
    status, url, raw = fetch(op, EDITOR, headers={"Referer": ADMIN})
    html = raw.decode("utf-8", "replace")
    m = re.search(r'name="wpcode-save-snippet-nonce"\s+value="([^"]+)"', html)
    if not m:
        print("NO NONCE", status, url, len(html))
        return 2
    nonce = m.group(1)
    print("nonce", nonce, "editor", len(html), "code", len(CODE))
    payload = {
        "wpcode-save-snippet-nonce": nonce,
        "_wp_http_referer": "/kw/wp-admin/admin.php?page=wpcode-snippet-manager&snippet_id=3811",
        "id": "3811",
        "wpcode_snippet_title": "Rukn KW fixpack",
        "wpcode_snippet_type": "php",
        "wpcode_snippet_code": CODE,
        "wpcode_active": "1",
        "wpcode_auto_insert": "1",
        "wpcode_auto_insert_location": "everywhere",
        "wpcode_auto_insert_number": "1",
        "wpcode_auto_insert_location_extra": "",
        "wpcode_priority": "5",
        "wpcode_note": "titles passthrough + meta/og + /english to /en + EN routes",
        "wpcode_tags": "",
        "wpcode_cl_rules": "",
        "wpcode_snippet_text": "",
    }
    status, url, raw = fetch(op, EDITOR, data=payload, headers={"Referer": EDITOR})
    html = raw.decode("utf-8", "replace")
    print("SAVE", status, url, "len", len(html))
    print("message", unescape(re.search(r"message=([^&#]+)", url).group(1)) if "message=" in url else "")
    print("error_in_url", "error" in url)
    print("has_title_field", "Rukn KW fixpack" in html)
    err = re.search(r"notice-error.*?>(.*?)</div>", html, re.S)
    if err:
        print("NOTICE", re.sub(r"<[^>]+>", " ", err.group(1))[:400])
    Path("/tmp/wpcode-save-result.html").write_text(html[:80000], encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
