#!/usr/bin/env python3
"""Local uniqueness smoke test — no WordPress needed."""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kw_builder import build
from kw_cities import CITIES, parse_slug
from kw_service_facts import FACTS
from rewrite_kw_articles import load_catalog

WATER_RE = re.compile(r"مضخات العمائر|ضغط المياه يختلف|خزانات سطحية شائعة|المضخات المنزلية شائعة")
TEL_RE = re.compile(r"tel:\+971|NameError|\{TEL\}")
WA_RE = re.compile(r"wa\.me/971586634710")


def tokens(html: str) -> set[str]:
    text = re.sub(r"<[^>]+>", " ", html)
    return {t for t in re.findall(r"[\u0600-\u06FF]{3,}", text)}


def shingles(html: str, n: int = 5) -> set:
    text = re.sub(r"<[^>]+>", " ", html)
    toks = re.findall(r"[\u0600-\u06FF]{2,}", text)
    return set(tuple(toks[i : i + n]) for i in range(max(0, len(toks) - n + 1)))


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    posts, cat = load_catalog()
    samples = [
        ("crawling-pest-control-hawalli", "شركة مكافحة حشرات زاحفة بحولي"),
        ("split-ac-maintenance-hawalli", "شركة صيانة مكيفات سبليت بحولي"),
        ("water-leak-detection-kuwait", "شركة كشف تسربات المياه بالكويت"),
        ("interior-painting-hawalli", "شركة دهانات داخلية بحولي"),
        ("landscaping-al-jahra", "شركة تنسيق حدائق بالجهراء"),
        ("indoor-moving-farwaniya", "شركة نقل أثاث داخلي بالفروانية"),
        ("locksmith-kuwait", "فني فتح الأبواب وتغيير الأقفال بالكويت"),
        ("home-cleaning-hawalli", "شركة تنظيف منازل بحولي"),
    ]
    by_slug = {p["post_name"]: p for p in posts}
    built = {}
    errors = []
    for slug, title in samples:
        p = by_slug.get(slug) or {
            "ID": "90000",
            "post_title": title,
            "post_name": slug,
        }
        art = build(p, cat)
        html = art["html"]
        built[slug] = art
        svc, city = parse_slug(slug)
        if TEL_RE.search(html):
            errors.append(f"{slug}: tel leftover")
        if not WA_RE.search(html):
            errors.append(f"{slug}: missing WhatsApp")
        if "أسئلة شائعة" not in html:
            errors.append(f"{slug}: missing FAQ")
        if art["word_count_hint"] < 2300:
            errors.append(f"{slug}: short {art['word_count_hint']}")
        wet_hits = WATER_RE.findall(html)
        waterish = any(x in slug for x in ("water", "leak", "plumb", "tank", "heater", "pump", "drain"))
        if wet_hits and not waterish:
            errors.append(f"{slug}: water leftover {wet_hits}")
        print(f"OK {slug} fam={FACTS.get(svc,{}).get('family')} words={art['word_count_hint']} city={city}")

    pairs = [
        ("crawling-pest-control-hawalli", "split-ac-maintenance-hawalli"),
        ("crawling-pest-control-hawalli", "interior-painting-hawalli"),
        ("split-ac-maintenance-hawalli", "home-cleaning-hawalli"),
        ("landscaping-al-jahra", "indoor-moving-farwaniya"),
        ("locksmith-kuwait", "water-leak-detection-kuwait"),
    ]
    for a, b in pairs:
        j = jaccard(shingles(built[a]["html"]), shingles(built[b]["html"]))
        print(f"5gram Jaccard {a} vs {b} = {j:.3f}")
        if j > 0.45:
            errors.append(f"high jaccard {a}/{b}={j:.3f}")

    same = [
        ("crawling-pest-control-hawalli", "crawling-pest-control-kuwait"),
    ]
    # kuwait pest may not be in samples built
    pest_kw = by_slug.get("crawling-pest-control-kuwait")
    if pest_kw:
        built["crawling-pest-control-kuwait"] = build(pest_kw, cat)
        j = jaccard(
            shingles(built["crawling-pest-control-hawalli"]["html"]),
            shingles(built["crawling-pest-control-kuwait"]["html"]),
        )
        print(f"5gram Jaccard same-service cities = {j:.3f}")
        if j > 0.55:
            errors.append(f"same-service cities too similar {j:.3f}")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("SMOKE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
