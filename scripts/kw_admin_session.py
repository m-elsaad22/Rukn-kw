#!/usr/bin/env python3
"""Cookie login + WPCode snippet save for rukn-eltatawer.com/kw."""
from __future__ import annotations

import http.cookiejar
import json
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ORIGIN = "https://www.rukn-eltatawer.com"
LOGIN = f"{ORIGIN}/kw/wp-login.php"
ADMIN = f"{ORIGIN}/kw/wp-admin/"
USER = "cursor"
PASSWORD = "Cursor@curso12"
CTX = ssl.create_default_context()
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36"


def opener():
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar),
        urllib.request.HTTPSHandler(context=CTX),
    ), jar


def fetch(op, url, data=None, headers=None, method=None):
    body = None
    hdrs = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"}
    if headers:
        hdrs.update(headers)
    if data is not None:
        if isinstance(data, dict):
            body = urllib.parse.urlencode(data, doseq=True).encode()
            hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
        elif isinstance(data, (bytes, bytearray)):
            body = data
        else:
            body = str(data).encode()
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with op.open(req, timeout=90) as r:
            raw = r.read()
            return r.status, r.geturl(), dict(r.headers), raw
    except urllib.error.HTTPError as e:
        raw = e.read()
        return e.code, e.geturl(), dict(e.headers), raw


def login(op):
    fetch(op, LOGIN)
    status, url, hdrs, raw = fetch(
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
    html = raw.decode("utf-8", "replace")
    ok = "wp-admin" in url and "wp-login.php" not in url
    print("LOGIN", status, url, "ok" if ok else "FAIL", "html", len(html))
    if not ok:
        print(html[:500])
    return ok


def main():
    import urllib.error

    op, jar = opener()
    if not login(op):
        return 1
    # Discover WPCode editor
    candidates = [
        f"{ADMIN}admin.php?page=wpcode-snippet-manager&snippet_id=3811",
        f"{ADMIN}admin.php?page=wpcode&view=editor&snippet_id=3811",
        f"{ADMIN}admin.php?page=wpcode-snippet-manager&id=3811",
        f"{ADMIN}admin.php?page=wpcode",
    ]
    editor_html = ""
    editor_url = ""
    for url in candidates:
        status, final, hdrs, raw = fetch(op, url, headers={"Referer": ADMIN})
        html = raw.decode("utf-8", "replace")
        print("GET", status, final, "len", len(html), "has_code", "wpcode" in html.lower())
        Path(f"/tmp/wpcode-{url.split('page=')[-1].replace('&','_').replace('=','-')[:60]}.html").write_text(html[:200000], encoding="utf-8")
        if status == 200 and ("snippet" in html.lower() or "wpcode-code" in html or "wpcode_code" in html):
            editor_html = html
            editor_url = final
            if "wpcode-save-snippet-nonce" in html or "name=\"code\"" in html or "wpcode-code" in html:
                break
    if not editor_html:
        print("NO EDITOR")
        return 2
    print("EDITOR", editor_url)
    # Extract nonce and fields
    for pat in (
        r'name="wpcode-save-snippet-nonce"\s+value="([^"]+)"',
        r'id="wpcode-save-snippet-nonce"\s+value="([^"]+)"',
        r'name="_wpnonce"\s+value="([^"]+)"',
        r'"nonce":"([^"]+)"',
        r'wpcode_admin[^"]*"\s*,\s*"([^"]+)"',
    ):
        m = re.search(pat, editor_html)
        print("NONCE", pat, "->", m.group(1) if m else None)
    # print input names
    names = sorted(set(re.findall(r'name="([^"]+)"', editor_html)))
    print("FIELDS", names[:80])
    # WPCode localized
    m = re.search(r"var wpcode(?:_admin|_vars)?\s*=\s*(\{.*?\});", editor_html, re.S)
    if m:
        print("JSVAR", m.group(1)[:800])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
