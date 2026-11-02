#!/usr/bin/env python3
"""Create missing Kuwait service posts (6 cities each) with exclusive copy."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kw_builder import build
from kw_cities import CITIES
from kw_service_facts import FACTS
from rewrite_kw_articles import apply_meta_batch, load_catalog, update_content
from wp_kw_client import rest

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "kw_posts_catalog.json"

MISSING = [
    ("intercom", "شركة"),
    ("locksmith", "فني"),
    ("fire-alarm", "شركة"),
    ("generator-installation", "شركة"),
    ("ups-installation", "شركة"),
    ("smart-home", "شركة"),
    ("home-network", "شركة"),
    ("water-tanker-delivery", "خدمة"),
    ("manhole-cleaning", "شركة"),
    ("car-parking-shades", "شركة"),
    ("tent-diwaniya", "شركة"),
    ("furniture-upholstery", "فني"),
    ("curtain-installation", "شركة"),
    ("pool-construction", "شركة"),
    ("elevator-installation", "شركة"),
    ("office-relocation", "شركة"),
    ("epoxy-flooring", "شركة"),
    ("roller-shutters", "شركة"),
    ("garage-doors", "شركة"),
    ("water-softener", "شركة"),
]


def title_for(prefix: str, noun: str, city: dict) -> str:
    if prefix == "فني":
        return f"فني {noun} {city['prep']}"
    if prefix == "خدمة":
        return f"{noun} {city['prep']}"
    return f"شركة {noun} {city['prep']}"


def main():
    posts, cat = load_catalog()
    existing = {(p["post_name"]) for p in posts}
    created = []
    skipped = []
    failed = []
    for slug, prefix in MISSING:
        spec = FACTS.get(slug)
        if not spec:
            failed.append({"slug": slug, "err": "no facts"})
            continue
        for city_key, city in CITIES.items():
            post_name = f"{slug}-{city_key}"
            if post_name in existing:
                skipped.append(post_name)
                continue
            title = title_for(prefix, spec["noun"], city)
            stub = {"ID": "0", "post_title": title, "post_name": post_name}
            # related links work better after catalog has siblings; first pass still unique
            art = build(stub, cat)
            try:
                data = rest(
                    "/wp/v2/posts",
                    method="POST",
                    body={
                        "title": title,
                        "slug": post_name,
                        "status": "publish",
                        "content": art["html"],
                        "excerpt": art["excerpt"],
                        "comment_status": "closed",
                        "lang": "ar",
                    },
                    timeout=180,
                )
                pid = int(data["id"])
                item = {
                    "id": pid,
                    "excerpt": art["excerpt"],
                    "tags": art["tags"],
                    "rank_math_description": art["rank_math_description"],
                    "rank_math_focus_keyword": art["rank_math_focus_keyword"],
                    "meta": art["meta"],
                }
                apply_meta_batch([item])
                cat[slug][city_key] = {"id": pid, "title": title, "slug": post_name}
                created.append({"id": pid, "slug": post_name, "title": title, "words": art["word_count_hint"]})
                print(f"NEW {pid} {post_name} words={art['word_count_hint']}", flush=True)
            except Exception as e:
                failed.append({"slug": post_name, "err": str(e)[:400]})
                print(f"FAIL {post_name}: {e}", flush=True)
                time.sleep(0.5)

    # refresh catalog from created+existing
    if created:
        rows = json.loads(CATALOG_PATH.read_text())["results"]
        have = {r["post_name"] for r in rows}
        for c in created:
            if c["slug"] not in have:
                rows.append({"ID": str(c["id"]), "post_title": c["title"], "post_name": c["slug"]})
        CATALOG_PATH.write_text(json.dumps({"results": rows}, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"created": len(created), "skipped": len(skipped), "failed": failed[:8], "n_failed": len(failed)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
