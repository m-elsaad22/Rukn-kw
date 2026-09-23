#!/usr/bin/env python3
"""WordPress REST + WPVibe CLI client for rukn-eltatawer.com/kw."""
from __future__ import annotations

import base64
import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BASE = "https://rukn-eltatawer.com/kw/index.php?rest_route="
USER = os.environ.get("RUKN_WP_USER", "cursor")
APP_PASS = os.environ.get("RUKN_WP_APP_PASSWORD", "")
TOKEN = base64.b64encode(f"{USER}:{APP_PASS}".encode()).decode()
CTX = ssl.create_default_context()


def rest(route: str, method: str = "GET", body: Any = None, timeout: int = 180) -> Any:
    url = BASE + route
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Basic {TOKEN}")
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {route} -> {e.code}: {err[:800]}") from e


def cli(command: str, confirm: bool = True, timeout: int = 180) -> Any:
    return rest(
        "/wpvibe/v1/cli/run",
        method="POST",
        body={"command": command, "confirm_write": confirm},
        timeout=timeout,
    )
