#!/usr/bin/env python3
"""Fill Kayan metaboxes on all Kuwait posts (one post per uncached frontend trigger)."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kw_builder import build
from rewrite_kw_articles import apply_meta_batch, load_catalog, load_progress, save_progress
from wp_kw_client import cli


def has_faq(post_id: int) -> bool:
    try:
        r = cli(f"post meta get {post_id} yourcolor__faqs", confirm=False)
        return "question" in (r.get("stdout") or "")
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--progress-file", default="/tmp/kw-progress-meta2.json")
    ap.add_argument("--redo-done", action="store_true")
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--verify-every", type=int, default=25)
    args = ap.parse_args()

    posts, cat = load_catalog()
    selected = posts[args.offset :]
    if args.limit:
        selected = selected[: args.limit]

    progress_path = Path(args.progress_file)
    progress = load_progress(progress_path)
    done = set() if args.redo_done else set(progress.get("done") or [])
    failed = list(progress.get("failed") or [])

    ok = 0
    for p in selected:
        pid = int(p["ID"])
        if pid in done:
            continue
        if args.skip_existing and has_faq(pid):
            done.add(pid)
            print(f"SKIP {pid} {p['post_name']} already has FAQ", flush=True)
            continue
        try:
            art = build(p, cat)
            item = {
                "id": pid,
                "excerpt": art["excerpt"],
                "tags": art["tags"],
                "rank_math_title": art["rank_math_title"],
                "rank_math_description": art["rank_math_description"],
                "rank_math_focus_keyword": art["rank_math_focus_keyword"],
                "meta": art["meta"],
            }
            apply_meta_batch([item])
            if args.verify_every and ok % args.verify_every == 0:
                if not has_faq(pid):
                    apply_meta_batch([item])
                    if not has_faq(pid):
                        raise RuntimeError("FAQ missing after retry")
            done.add(pid)
            ok += 1
            print(f"META {ok} {pid} {p['post_name']}", flush=True)
            if ok % 5 == 0:
                progress["done"] = sorted(done)
                progress["failed"] = failed
                save_progress(progress, progress_path)
        except Exception as e:
            failed.append({"id": pid, "slug": p["post_name"], "err": str(e)[:300]})
            progress["done"] = sorted(done)
            progress["failed"] = failed
            save_progress(progress, progress_path)
            print(f"FAIL {pid} {p['post_name']}: {e}", flush=True)
            time.sleep(0.8)

    try:
        cli("option update rukn_kw_meta_apply 0")
    except Exception:
        pass
    progress["done"] = sorted(done)
    progress["failed"] = failed
    save_progress(progress, progress_path)
    print(f"meta done ok={ok} done={len(done)} failed={len(failed)}")


if __name__ == "__main__":
    main()
