#!/usr/bin/env python3
"""Remove leaked article CSS from stored post_content (wpautop/kses stripped <style>)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_kw_client import rest

CATALOG = Path(__file__).resolve().parent / "kw_posts_catalog.json"

CSS_HEAD = re.compile(
    r"^\s*(?:<style[^>]*>\s*)?\.rukn-wrap\{.*?\.author-box\{[^}]*\}\s*(?:</style>)?\s*",
    re.S | re.I,
)
CSS_P = re.compile(r"<p[^>]*>\s*\.rukn-wrap\{.*?</p>\s*", re.S | re.I)


def strip_css(html: str) -> str:
    html = CSS_HEAD.sub("", html, count=1)
    html = CSS_P.sub("", html, count=1)
    return html.lstrip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    posts = json.loads(CATALOG.read_text())["results"]
    selected = [p for i, p in enumerate(posts) if i % args.shards == args.shard]
    if args.limit:
        selected = selected[: args.limit]

    ok = skip = fail = 0
    for p in selected:
        pid = int(p["ID"])
        try:
            data = rest(f"/wp/v2/posts/{pid}&context=edit&_fields=id,content", timeout=120)
            raw = (data.get("content") or {}).get("raw") or ""
            new = strip_css(raw)
            if new == raw.lstrip() and not raw.lstrip().startswith(".rukn-wrap"):
                skip += 1
                continue
            if new == raw:
                skip += 1
                continue
            rest(f"/wp/v2/posts/{pid}", method="POST", body={"content": new}, timeout=180)
            ok += 1
            print(f"STRIP {pid} {p['post_name']} -{len(raw)-len(new)}", flush=True)
        except Exception as e:
            fail += 1
            print(f"FAIL {pid} {p['post_name']}: {e}", flush=True)
            time.sleep(0.4)
        if (ok + skip) % 20 == 0:
            print(f"progress shard={args.shard} ok={ok} skip={skip} fail={fail}", flush=True)
    print(f"done shard={args.shard} ok={ok} skip={skip} fail={fail}")


if __name__ == "__main__":
    main()
