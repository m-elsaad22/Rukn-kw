#!/usr/bin/env python3
"""Live GSC cleanup for Rukn KW: spam titles, sitemap flags, footer number, cache.

WPCode snippet writes are gated by WPVibe approval (code_snippet). Title and
Rank Math option changes go through option/meta-apply which the live snippet
already executes on init.
"""

from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_kuwait_full_fixes import APP_PASSWORD, cli, request  # noqa: E402

TEMPLATE = "%title% %sep% ركن التطور الكويت"
SITEMAP_URLS = [
    "https://www.rukn-eltatawer.com/kw/sitemap_index.xml",
    "https://www.rukn-eltatawer.com/kw/page-sitemap.xml",
    "https://www.rukn-eltatawer.com/kw/post-sitemap1.xml",
    "https://www.rukn-eltatawer.com/kw/robots.txt",
]


def cli_out(cmd: str, write: bool = False, timeout: int = 180):
    st, body = cli(cmd, write=write, timeout=timeout)
    out = (body or {}).get("stdout", body) if isinstance(body, dict) else body
    return st, out, body


def queue_meta(items: list[dict]) -> None:
    if not items:
        return
    payload = {"items": items}
    raw = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode()).decode()
    st, out, body = cli_out("option update rukn_kw_meta_apply " + json.dumps(raw), write=True)
    if isinstance(body, dict) and body.get("exit_code", 0) != 0:
        raise SystemExit(f"meta queue failed: {body}")
    cli_out("option get rukn_kw_meta_apply")  # triggers live snippet init


def spam_rows() -> list[dict]:
    st, out, _ = cli_out(
        'db query "SELECT post_id, meta_value FROM iFs1ICdt_postmeta '
        "WHERE meta_key='rank_math_title' AND ("
        "meta_value LIKE '%01151481000%' OR meta_value LIKE '%الإعلان للإيجار%' "
        "OR meta_value LIKE '%0541673020%')\" --limit=2000"
    )
    data = json.loads(out) if isinstance(out, str) else out
    return (data or {}).get("results") or []


def clean_titles() -> int:
    rows = spam_rows()
    items = []
    for row in rows:
        pid = int(row["post_id"])
        val = row.get("meta_value") or ""
        if "01151481000" in val or "الإعلان للإيجار" in val:
            items.append({"id": pid, "meta": {"rank_math_title": TEMPLATE}})
            continue
        clean = val
        for junk in ("📞", "📢", "01151481000", "0541673020", "الإعلان للإيجار"):
            clean = clean.replace(junk, " ")
        clean = re.sub(r"\s+", " ", clean).strip(" |-–—")
        items.append({"id": pid, "meta": {"rank_math_title": clean or TEMPLATE}})
    for i in range(0, len(items), 80):
        queue_meta(items[i : i + 80])
        print(f"titles {i}-{min(i + 80, len(items)) - 1}")
    return len(items)


def main() -> int:
    if not APP_PASSWORD:
        raise SystemExit("Set WP_APP_PASSWORD")
    st, me = request("GET", "/wp-json/wp/v2/users/me?context=edit")
    print("auth", st, (me or {}).get("slug") if isinstance(me, dict) else me)
    if st != 200:
        return 1

    n = clean_titles()
    print("cleaned titles", n)

    for patch in (
        "option patch update rank-math-options-sitemap pt_services_sitemap off",
        "option patch update rank-math-options-sitemap pt_reviews_sitemap off",
        "option patch update rank-math-options-sitemap pt_faqs_sitemap off",
        "option patch update rank-math-options-sitemap pt_pricing_sitemap off",
        "option patch update rank-math-options-sitemap pt_portfolio_sitemap off",
        "option patch update rank-math-options-sitemap pt_before_after_sitemap off",
        "option patch update rank-math-options-sitemap include_featured_image on",
    ):
        st, out, _ = cli_out(patch, write=True)
        print(patch.split()[-2], st)

    st, out, _ = cli_out("post list --post_type=services --post_status=publish --format=ids")
    ids = [int(x) for x in re.findall(r"\d+", str(out))]
    queue_meta([{"id": i, "meta": {"rank_math_robots": ["noindex", "nofollow"]}} for i in ids])
    print("noindex services", ids)

    new_copy = 'حقوق النشر {%YEAR%} © جميع الحقوق محفوظة لصالح "شركة ركن التطور - الكويت"'
    cli_out("option update Copyrights " + json.dumps(new_copy), write=True)

    print("purge", cli("cache purge --url=" + ",".join(SITEMAP_URLS), write=True)[1])
    print("flush", cli("cache flush", write=True)[1])
    print("litespeed", cli("litespeed-purge all", write=True)[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
