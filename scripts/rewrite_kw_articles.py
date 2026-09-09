#!/usr/bin/env python3
"""Rewrite Kuwait service posts with unique HTML and fill Kayan metaboxes."""
from __future__ import annotations

import argparse
import base64
import json
import ssl
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kw_builder import build
from kw_cities import parse_slug
from wp_kw_client import rest, cli

CTX = ssl.create_default_context()
FRONT = "https://rukn-eltatawer.com/kw/index.php"

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "kw_posts_catalog.json"
PROGRESS = ROOT / "rewrite_progress.json"


def load_catalog():
    rows = json.loads(CATALOG_PATH.read_text())["results"]
    cat = defaultdict(dict)
    posts = []
    for r in rows:
        svc, city = parse_slug(r["post_name"])
        item = {"id": int(r["ID"]), "title": r["post_title"], "slug": r["post_name"]}
        cat[svc][city] = item
        posts.append({"ID": r["ID"], "post_title": r["post_title"], "post_name": r["post_name"]})
    return posts, cat


def load_progress(path: Path = None):
    path = path or PROGRESS
    if path.exists():
        return json.loads(path.read_text())
    return {"done": [], "failed": []}


def save_progress(p, path: Path = None):
    (path or PROGRESS).write_text(json.dumps(p, ensure_ascii=False, indent=2))


def update_content(post_id: int, html: str, excerpt: str):
    return rest(
        f"/wp/v2/posts/{post_id}",
        method="POST",
        body={"content": html, "excerpt": excerpt},
        timeout=180,
    )


def _safe_b64(payload: dict) -> str:
    """Pad JSON so standard base64 has no + or / (WP-CLI / PHP decode safety)."""
    n = 0
    while True:
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        if n:
            payload2 = dict(payload)
            payload2["_pad"] = "x" * n
            raw = json.dumps(payload2, ensure_ascii=False, separators=(",", ":"))
        b64 = base64.b64encode(raw.encode("utf-8")).decode()
        if "+" not in b64 and "/" not in b64:
            return b64
        n += 1
        if n > 80:
            return b64


def trigger_frontend_apply(post_id: int = 0):
    """WPCode 'everywhere' does not run on REST. Search URLs are uncached and run PHP."""
    url = f"{FRONT}?s=rukn{int(post_id)}x{int(time.time() * 1000)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 RuknMeta/1.0", "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
        r.read(256)
    try:
        cli("option update rukn_kw_meta_apply 0")
    except Exception:
        pass


def apply_meta_batch(items: list):
    """One post per option write — large batches time out before delete_option."""
    if not items:
        return
    last_err = None
    for item in items:
        payload = {"items": [item]}
        b64 = _safe_b64(payload)
        r = cli(f"option update rukn_kw_meta_apply {b64}")
        if isinstance(r, dict) and r.get("exit_code", 0) not in (0, None, "0"):
            last_err = RuntimeError(str(r)[:500])
            continue
        trigger_frontend_apply(int(item.get("id") or 0))
    if last_err:
        raise last_err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--batch-meta", type=int, default=4)
    ap.add_argument("--only-slug-prefix", default="")
    ap.add_argument("--redo-done", action="store_true")
    ap.add_argument("--min-words", type=int, default=1500)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--progress-file", default="")
    ap.add_argument("--skip-meta", action="store_true")
    ap.add_argument("--meta-only", action="store_true")
    args = ap.parse_args()

    posts, cat = load_catalog()
    progress_path = Path(args.progress_file) if args.progress_file else PROGRESS
    progress = load_progress(progress_path)
    done = set() if args.redo_done else set(progress.get("done") or [])
    selected = posts[args.offset :]
    if args.shards > 1:
        selected = [p for i, p in enumerate(selected) if i % args.shards == args.shard]
    if args.only_slug_prefix:
        selected = [p for p in selected if p["post_name"].startswith(args.only_slug_prefix)]
    if args.limit:
        selected = selected[: args.limit]

    pending_meta = []
    ok = 0
    for p in selected:
        pid = int(p["ID"])
        if pid in done:
            continue
        try:
            art = build(p, cat)
            if art["word_count_hint"] < args.min_words:
                raise RuntimeError(f"short article {art['word_count_hint']}")
            if not args.meta_only:
                update_content(pid, art["html"], art["excerpt"])
            if not args.skip_meta:
                pending_meta.append(
                    {
                        "id": pid,
                        "excerpt": art["excerpt"],
                        "tags": art["tags"],
                        "rank_math_title": art["rank_math_title"],
                        "rank_math_description": art["rank_math_description"],
                        "rank_math_focus_keyword": art["rank_math_focus_keyword"],
                        "meta": art["meta"],
                    }
                )
            if args.skip_meta:
                done.add(pid)
            ok += 1
            print(f"OK {pid} {p['post_name']} words={art['word_count_hint']}", flush=True)
            if pending_meta and len(pending_meta) >= args.batch_meta:
                apply_meta_batch(pending_meta)
                for it in pending_meta:
                    done.add(int(it["id"]))
                pending_meta = []
                progress["done"] = sorted(done)
                save_progress(progress, progress_path)
            elif args.skip_meta and ok % 5 == 0:
                progress["done"] = sorted(done)
                save_progress(progress, progress_path)
        except Exception as e:
            progress.setdefault("failed", []).append({"id": pid, "slug": p["post_name"], "err": str(e)[:300]})
            save_progress(progress, progress_path)
            print(f"FAIL {pid} {p['post_name']}: {e}", flush=True)
            time.sleep(0.4)
    if pending_meta:
        apply_meta_batch(pending_meta)
        for it in pending_meta:
            done.add(int(it["id"]))
        pending_meta = []
    progress["done"] = sorted(done)
    save_progress(progress, progress_path)
    print(f"updated {ok} posts; done={len(done)} failed={len(progress.get('failed') or [])}")


if __name__ == "__main__":
    main()
