#!/usr/bin/env python3
"""WordPress REST / WPVibe CLI helper for the Kuwait site.

Credentials come from the environment, never from this file:
  RUKN_WP_USER
  RUKN_WP_APP_PASSWORD
"""
from __future__ import annotations

import base64
import json
import os
import urllib.request

USER = os.environ.get("RUKN_WP_USER", "")
APP_PASS = os.environ.get("RUKN_WP_APP_PASSWORD", "")
BASE = "https://rukn-eltatawer.com/kw/index.php?rest_route="
TOKEN = base64.b64encode(f"{USER}:{APP_PASS}".encode()).decode() if USER and APP_PASS else ""


def _auth_request(url: str, data: bytes | None = None, method: str = "GET", timeout: int = 180):
    if not TOKEN:
        raise RuntimeError("Set RUKN_WP_USER and RUKN_WP_APP_PASSWORD")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Basic {TOKEN}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else {}


def cli(cmd: str, confirm: bool = True, timeout: int = 180) -> dict:
    payload = {"command": cmd, "confirm_write": confirm}
    return _auth_request(
        BASE + "/wpvibe/v1/cli/run",
        data=json.dumps(payload).encode(),
        method="POST",
        timeout=timeout,
    )


def php_dumps(value) -> str:
    """Minimal PHP serializer (UTF-8 byte lengths)."""
    if value is None:
        return "N;"
    if isinstance(value, bool):
        return "b:1;" if value else "b:0;"
    if isinstance(value, int) and not isinstance(value, bool):
        return f"i:{value};"
    if isinstance(value, float):
        return f"d:{value};"
    if isinstance(value, str):
        encoded = value.encode("utf-8")
        return f's:{len(encoded)}:"{value}";'
    if isinstance(value, list):
        inner = "".join(php_dumps(i) + php_dumps(item) for i, item in enumerate(value))
        return f"a:{len(value)}:{{{inner}}}"
    if isinstance(value, dict):
        inner = "".join(php_dumps(k) + php_dumps(item) for k, item in value.items())
        return f"a:{len(value)}:{{{inner}}}"
    raise TypeError(type(value))
