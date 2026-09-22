#!/usr/bin/env python3
"""Phase 3 — inspect every published /kw/ article and rewrite only those that need it.

Does not change slugs/URLs, featured images, or Rank Math options.
Does not invent prices, ratings, guarantees, or phone numbers.
Contact CTAs point at /kw/contact-us/. Site-chrome WhatsApp is unchanged.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kw_builder import build
from kw_cities import CITIES, parse_slug
from kw_service_facts import FACTS, family_of
from phase2_bulk_cleanup import WordPressClient, env, iter_published_posts, load_dotenv, progress

ROOT = Path(__file__).resolve().parents[1]
CONTACT = "https://rukn-eltatawer.com/kw/contact-us/"
PROGRESS_PATH = Path(__file__).with_name("phase3_progress.json")
AUDIT_PATH = Path(__file__).with_name("phase3_audit.json")
FAIL_PATH = Path(__file__).with_name("phase3_failures.jsonl")

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.I | re.S)
IMG_RE = re.compile(r"(?:<figure\b[^>]*>[\s\S]*?</figure>|<img\b[^>]*>)", re.I)
WORD_RE = re.compile(r"\S+")
PLACEHOLDER_RE = re.compile(r"\[\[[^\]]+\]\]")


def strip_html(html: str) -> str:
    text = unescape(TAG_RE.sub(" ", html or ""))
    return WS_RE.sub(" ", text).strip()


def headings(html: str) -> list[str]:
    return [WS_RE.sub(" ", unescape(TAG_RE.sub("", h))).strip() for h in H2_RE.findall(html or "")]


def shingles(text: str, n: int = 5) -> set[tuple[str, ...]]:
    words = WORD_RE.findall(text)
    if len(words) < n:
        return {tuple(words)} if words else set()
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def neutralize(text: str, city_key: str) -> str:
    """Strip city/area tokens so find-replace clones still look identical."""
    city = CITIES.get(city_key) or {}
    out = text
    tokens = [
        city.get("name", ""),
        city.get("label", ""),
        city.get("prep", ""),
        city.get("in", ""),
        *(city.get("areas") or []),
    ]
    for tok in sorted({t for t in tokens if t}, key=len, reverse=True):
        out = out.replace(tok, " ")
    return WS_RE.sub(" ", out).strip()


def extract_images(html: str) -> list[str]:
    return IMG_RE.findall(html or "")


def reinsert_images(html: str, images: list[str]) -> str:
    if not images:
        return html
    block = "\n".join(images)
    if "class=\"rukn-hero\"" in html:
        return html.replace("</div>\n[post_call]", f"</div>\n{block}\n[post_call]", 1)
    return block + "\n" + html


@dataclass
class Decision:
    post_id: int
    slug: str
    title: str
    service: str
    city: str
    action: str
    reasons: list[str] = field(default_factory=list)
    words: int = 0
    sibling_sim: float = 0.0
    heading_sim: float = 0.0


def score_posts(posts) -> list[Decision]:
    by_service: dict[str, list] = defaultdict(list)
    texts: dict[int, str] = {}
    heads: dict[int, set[str]] = {}
    neut: dict[int, set[tuple[str, ...]]] = {}
    meta: dict[int, tuple[str, str]] = {}

    for p in posts:
        svc, city = parse_slug(p.slug)
        meta[p.id] = (svc, city)
        raw = strip_html(p.content)
        texts[p.id] = raw
        heads[p.id] = set(headings(p.content))
        neut[p.id] = shingles(neutralize(raw, city), 5)
        by_service[svc].append(p)

    decisions: list[Decision] = []
    for p in posts:
        svc, city = meta[p.id]
        city_info = CITIES.get(city, {})
        spec = FACTS.get(svc)
        words = len(WORD_RE.findall(texts[p.id]))
        reasons: list[str] = []

        if "971" in p.content or "+971" in p.content or "wa.me" in p.content.lower():
            reasons.append("uae-number")
        if PLACEHOLDER_RE.search(p.content):
            reasons.append("placeholder")
        if words < 800:
            reasons.append(f"thin:{words}")
        if CONTACT.rstrip("/") not in p.content and "contact-us" not in p.content:
            reasons.append("missing-contact")

        areas = city_info.get("areas") or []
        if areas and not any(a in texts[p.id] for a in areas[:4]):
            reasons.append("missing-local-areas")

        if spec:
            noun = spec["noun"]
            if noun and noun not in texts[p.id] and noun.split()[0] not in texts[p.id]:
                reasons.append("weak-service-dna")
        else:
            reasons.append("unknown-service")

        siblings = [s for s in by_service[svc] if s.id != p.id]
        max_body = 0.0
        max_h = 0.0
        for s in siblings:
            max_body = max(max_body, jaccard(neut[p.id], neut[s.id]))
            if heads[p.id] and heads[s.id]:
                max_h = max(max_h, jaccard(heads[p.id], heads[s.id]))
        if max_body >= 0.28:
            reasons.append(f"clone-body:{max_body:.2f}")
        if max_h >= 0.45:
            reasons.append(f"clone-h2:{max_h:.2f}")

        # Same opening after neutralizing city names → shared search intent.
        if siblings:
            me_open = neutralize(texts[p.id][:350], city)
            for s in siblings:
                sc, _ = meta[s.id]
                other_open = neutralize(texts[s.id][:350], meta[s.id][1])
                if me_open and other_open and jaccard(shingles(me_open, 4), shingles(other_open, 4)) >= 0.5:
                    reasons.append("shared-intent")
                    break

        action = "rewrite" if reasons else "keep"
        decisions.append(
            Decision(
                post_id=p.id,
                slug=p.slug,
                title=p.title,
                service=svc,
                city=city,
                action=action,
                reasons=reasons,
                words=words,
                sibling_sim=round(max_body, 3),
                heading_sim=round(max_h, 3),
            )
        )
    return decisions


def catalog_from_posts(posts) -> dict:
    cat: dict[str, dict[str, dict]] = defaultdict(dict)
    for p in posts:
        svc, city = parse_slug(p.slug)
        cat[svc][city] = {"id": p.id, "title": p.title, "slug": p.slug}
    return cat


def load_progress() -> dict[str, Any]:
    if PROGRESS_PATH.exists():
        return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    return {"done": [], "failed": [], "kept": []}


def save_progress(data: dict[str, Any]) -> None:
    PROGRESS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def self_test() -> None:
    fake_posts = []
    cities = list(CITIES)
    cat: dict[str, dict] = defaultdict(dict)
    for i, city in enumerate(cities):
        slug = f"home-cleaning-{city}"
        title = f"شركة تنظيف منازل {CITIES[city]['prep']}"
        item = {"id": 1000 + i, "title": title, "slug": slug, "post_name": slug, "post_title": title, "ID": 1000 + i}
        fake_posts.append(item)
        cat["home-cleaning"][city] = item
    htmls = []
    for item in fake_posts:
        art = build(item, cat)
        html = art["html"]
        assert "971" not in html, html[html.find("971") - 40 : html.find("971") + 40] if "971" in html else html
        assert "wa.me" not in html.lower()
        assert "tel:" not in html.lower()
        assert "contact-us" in html
        assert "[[" not in html
        assert art["word_count_hint"] >= 800, art["word_count_hint"]
        htmls.append(html)
        city = parse_slug(item["slug"])[1]
        intent = {"kuwait", "hawalli", "farwaniya", "mubarak-al-kabeer", "al-ahmadi", "al-jahra"}
        assert city in intent
    # Pairwise H2 overlap after neutralizing city names should stay moderate.
    for i in range(len(htmls)):
        for j in range(i + 1, len(htmls)):
            ci = parse_slug(fake_posts[i]["slug"])[1]
            cj = parse_slug(fake_posts[j]["slug"])[1]
            hi = {neutralize(h, ci) for h in headings(htmls[i])}
            hj = {neutralize(h, cj) for h in headings(htmls[j])}
            sim = jaccard(hi, hj)
            assert sim < 0.55, (fake_posts[i]["slug"], fake_posts[j]["slug"], sim)
    print("self-test ok")


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--redo-done", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0

    base = env("WP_BASE_URL", "WP_BASE", default="https://rukn-eltatawer.com/kw").rstrip("/")
    user = env("WP_USERNAME", "WP_USER", default="cursor")
    password = env("WP_APP_PASSWORD")
    if not password:
        print("Missing WP_APP_PASSWORD", file=sys.stderr)
        return 1
    wp = WordPressClient(base, user, password, delay=args.delay)
    st, me, _ = wp.request("GET", "/wp-json/wp/v2/users/me?context=edit")
    if st != 200:
        print(f"auth failed ({st}): {me}", file=sys.stderr)
        return 1
    print(f"authenticated as {me.get('slug')}  {base}")

    posts = iter_published_posts(wp, per_page=100)
    print(f"published posts: {len(posts)}")
    decisions = score_posts(posts)
    rewrite = [d for d in decisions if d.action == "rewrite"]
    keep = [d for d in decisions if d.action == "keep"]
    similar = [d for d in rewrite if any(r.startswith("clone-") or r == "shared-intent" for r in d.reasons)]
    reason_counts: dict[str, int] = defaultdict(int)
    for d in rewrite:
        for r in d.reasons:
            reason_counts[r.split(":")[0]] += 1

    audit = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "inspected": len(decisions),
        "rewrite": len(rewrite),
        "keep": len(keep),
        "similar": len(similar),
        "reason_counts": dict(sorted(reason_counts.items(), key=lambda kv: -kv[1])),
        "samples_rewrite": [
            {"id": d.post_id, "slug": d.slug, "reasons": d.reasons, "sim": d.sibling_sim}
            for d in rewrite[:12]
        ],
        "samples_keep": [{"id": d.post_id, "slug": d.slug, "words": d.words} for d in keep[:8]],
    }
    AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: audit[k] for k in ("inspected", "rewrite", "keep", "similar", "reason_counts")}, ensure_ascii=False, indent=2))

    if args.dry_run:
        print("dry-run: no PUT")
        return 0

    cat = catalog_from_posts(posts)
    by_id = {p.id: p for p in posts}
    progress_state = load_progress()
    done = set() if args.redo_done else set(progress_state.get("done") or [])
    kept_ids = set(progress_state.get("kept") or [])
    failed = list(progress_state.get("failed") or [])

    todo = rewrite
    if args.limit:
        todo = todo[: args.limit]
    total = len(todo)
    ok = 0
    for i, dec in enumerate(todo, 1):
        if dec.post_id in done:
            progress(i, total, "apply")
            continue
        post = by_id[dec.post_id]
        try:
            art = build(
                {
                    "ID": post.id,
                    "id": post.id,
                    "post_name": post.slug,
                    "post_title": post.title,
                    "title": post.title,
                    "slug": post.slug,
                },
                cat,
            )
            html = art["html"]
            html = reinsert_images(html, extract_images(post.content))
            if "971" in html or "wa.me" in html.lower():
                raise RuntimeError("generated HTML still contains UAE number")
            payload = {"content": html, "excerpt": art["excerpt"]}
            status, body, _ = wp.request("PUT", f"/wp-json/wp/v2/posts/{post.id}", payload)
            if status not in {200, 201}:
                status, body, _ = wp.request("POST", f"/wp-json/wp/v2/posts/{post.id}", payload)
            if status not in {200, 201}:
                raise RuntimeError(f"{status} {str(body)[:240]}")
            done.add(post.id)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            failed.append({"id": post.id, "slug": post.slug, "err": str(exc)[:300]})
            FAIL_PATH.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in failed) + "\n", encoding="utf-8")
        if i % 10 == 0 or i == total:
            progress_state = {"done": sorted(done), "kept": sorted(kept_ids), "failed": failed}
            save_progress(progress_state)
            progress(i, total, "apply")

    for d in keep:
        kept_ids.add(d.post_id)
    save_progress({"done": sorted(done), "kept": sorted(kept_ids), "failed": failed})

    # purge so public HTML matches
    st, body = wp.wpvibe_cli("litespeed-purge all", write=True)
    print("purge", st, str(body)[:160])

    report = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "inspected": len(decisions),
        "rewritten_ok": ok,
        "already_done": len(done),
        "kept": len(keep),
        "similar_flagged": len(similar),
        "failed": len(failed),
        "reason_counts": audit["reason_counts"],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
