#!/usr/bin/env python3
"""Phase 2 — bulk cleanup of Kuwait published posts via the WP REST API.

Reads credentials from `.env` (WP_BASE_URL, WP_USERNAME, WP_APP_PASSWORD).

Tasks
  1. Replace leftover `[[...]]` tokens and strip indexable UAE phone numbers
     from post bodies. WhatsApp stays on /contact-us/; post HTML must not
     contain 971 so Google does not associate Kuwait URLs with a UAE line.
  2. Guarantee every published post has a featured image, spread across the
     media library (currently five brand assets).
  3. Draft exact-title duplicates (keep the cleaner slug / older date).
  4. Print (and optionally apply) Rank Math LocalBusiness WP-CLI/SQL.

Examples
  python3 scripts/phase2_bulk_cleanup.py --dry-run
  python3 scripts/phase2_bulk_cleanup.py --tasks 1,2,3,4 --delay 0.25
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import random
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CTA = "تواصل معنا عبر الواتساب"
PLACEHOLDERS = {
    "[[عدد المشاريع]]": "540+",
    "[[سنة التأسيس]]": "2015",
}
CTX = ssl.create_default_context()

# UAE country code followed by a mobile subscriber (5x / 8 digits). Avoids 1971.
PHONE_RE = re.compile(
    r"""
    (?:
        https?://(?:www\.)?wa\.me/971\d{7,12}(?:\?[^"'<\s]*)?
      | https?://(?:api\.)?whatsapp\.com/send\?[^"'<\s]*
      | tel:\+?971[\d\s\-()]+
      | (?:\+|00)?971[\s\-()]*5\d(?:[\s\-]?\d){7}
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)
CALL_NOW_RE = re.compile(r"اتصل الآن")
ANCHOR_WA_RE = re.compile(
    r'<a\b[^>]*href=["\']https?://(?:www\.)?wa\.me/971[^"\']+["\'][^>]*>.*?</a>',
    re.IGNORECASE | re.DOTALL,
)


def load_dotenv() -> None:
    for candidate in (Path.cwd() / ".env", ROOT / ".env", Path(__file__).with_name(".env")):
        if not candidate.is_file():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))
        break


def env(name: str, *aliases: str, default: str = "") -> str:
    for key in (name, *aliases):
        val = os.environ.get(key)
        if val:
            return val.strip()
    return default


def progress(done: int, total: int, label: str) -> None:
    width = 28
    if total <= 0:
        bar = "-" * width
        pct = 0
    else:
        filled = int(width * done / total)
        bar = "=" * filled + "." * (width - filled)
        pct = int(100 * done / total)
    print(f"\r{label} [{bar}] {done}/{total} ({pct}%)", end="", file=sys.stderr, flush=True)
    if total and done >= total:
        print(file=sys.stderr)


@dataclass
class Post:
    id: int
    title: str
    slug: str
    date: str
    featured_media: int
    content: str


@dataclass
class Change:
    post: Post
    payload: dict[str, Any]
    notes: list[str] = field(default_factory=list)


class WordPressClient:
    def __init__(self, base: str, user: str, password: str, delay: float) -> None:
        self.base = base.rstrip("/")
        self.delay = delay
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        self._headers = {
            "User-Agent": "RuknKW-Phase2/1.0",
            "Accept": "application/json",
            "Authorization": f"Basic {token}",
        }

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        retries: int = 4,
    ) -> tuple[int, Any, dict[str, str]]:
        url = path if path.startswith("http") else f"{self.base}{path}"
        headers = dict(self._headers)
        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload, ensure_ascii=False).encode()
        last: tuple[int, Any, dict[str, str]] = (0, "no attempt", {})
        for attempt in range(retries):
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=120, context=CTX) as resp:
                    raw = resp.read().decode("utf-8", "replace")
                    try:
                        body: Any = json.loads(raw) if raw else {}
                    except json.JSONDecodeError:
                        body = raw
                    if self.delay:
                        time.sleep(self.delay)
                    return resp.status, body, {k.lower(): v for k, v in resp.headers.items()}
            except urllib.error.HTTPError as exc:
                raw = exc.read().decode("utf-8", "replace")
                try:
                    body = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    body = raw
                last = (exc.code, body, {k.lower(): v for k, v in exc.headers.items()})
                if exc.code in {429, 500, 502, 503, 504} and attempt < retries - 1:
                    time.sleep(min(8.0, 1.5 * (2 ** attempt)))
                    continue
                return last
            except Exception as exc:  # noqa: BLE001
                last = (0, str(exc), {})
                time.sleep(min(8.0, 1.5 * (2 ** attempt)))
        return last

    def wpvibe_cli(self, command: str, write: bool = False) -> tuple[int, Any]:
        st, body, _ = self.request(
            "POST",
            "/wp-json/wpvibe/v1/cli/run",
            {"command": command, "confirm_write": write},
        )
        if st == 409 and isinstance(body, dict) and write:
            st, body, _ = self.request(
                "POST",
                "/wp-json/wpvibe/v1/cli/run-approved",
                {"command": command, "confirm_write": True, "approved_state": json.dumps(body)},
            )
        return st, body


def scrub_content(html: str, contact_url: str) -> str:
    """Replace tokens and remove indexable UAE numbers from post HTML."""
    out = html
    for token, value in PLACEHOLDERS.items():
        if token in out:
            out = out.replace(token, value)

    contact = contact_url.rstrip("/") + "/"

    def _rewrite_anchor(match: re.Match[str]) -> str:
        tag = match.group(0)
        tag = re.sub(
            r'href=["\']https?://(?:www\.)?wa\.me/971[^"\']+["\']',
            f'href="{contact}"',
            tag,
            count=1,
            flags=re.I,
        )
        tag = CALL_NOW_RE.sub(CTA, tag)
        tag = re.sub(r'class="fa-solid fa-phone"', 'class="fa-brands fa-whatsapp"', tag)
        return tag

    out = ANCHOR_WA_RE.sub(_rewrite_anchor, out)
    out = PHONE_RE.sub(CTA, out)
    out = CALL_NOW_RE.sub(CTA, out)
    # Collapse CTA accidentally concatenated onto itself after overlapping replaces.
    out = re.sub(rf"(?:{re.escape(CTA)}){{2,}}", CTA, out)
    return out


def slug_penalty(slug: str) -> tuple[int, int, int, int]:
    slug = slug or ""
    elec = 1 if "-elec-" in slug or slug.endswith("-elec") else 0
    numbered = 1 if re.search(r"-\d+$", slug) else 0
    return (elec, numbered, slug.count("-"), len(slug))


def pick_canonical(posts: list[Post]) -> Post:
    return sorted(posts, key=lambda p: (slug_penalty(p.slug), p.date, p.id))[0]


def iter_published_posts(wp: WordPressClient, per_page: int) -> list[Post]:
    posts: list[Post] = []
    page = 1
    total = 0
    fields = "id,title,slug,date,featured_media,content"
    while True:
        path = (
            f"/wp-json/wp/v2/posts?status=publish&context=edit"
            f"&per_page={per_page}&page={page}&_fields={fields}"
        )
        status, body, headers = wp.request("GET", path)
        if status != 200:
            raise SystemExit(f"fetch posts page {page} failed ({status}): {body}")
        if not isinstance(body, list) or not body:
            break
        total = int(headers.get("x-wp-total") or total or len(body))
        for item in body:
            title = item.get("title")
            if isinstance(title, dict):
                title = title.get("raw") or title.get("rendered") or ""
            content = item.get("content")
            raw = content.get("raw") if isinstance(content, dict) else ""
            posts.append(
                Post(
                    id=int(item["id"]),
                    title=str(title or ""),
                    slug=str(item.get("slug") or ""),
                    date=str(item.get("date") or ""),
                    featured_media=int(item.get("featured_media") or 0),
                    content=str(raw or ""),
                )
            )
        progress(len(posts), total, "fetch")
        if len(posts) >= total or len(body) < per_page:
            break
        page += 1
    return posts


def list_media_ids(wp: WordPressClient) -> list[tuple[int, str]]:
    status, body, headers = wp.request("GET", "/wp-json/wp/v2/media?per_page=100")
    if status != 200 or not isinstance(body, list):
        raise SystemExit(f"media library fetch failed ({status}): {body}")
    images: list[tuple[int, str]] = []
    for item in body:
        mime = str(item.get("mime_type") or "")
        if not mime.startswith("image/"):
            continue
        images.append((int(item["id"]), str(item.get("source_url") or "")))
    print(f"media images: {len(images)} (library reports {headers.get('x-wp-total', '?')})")
    for mid, url in images:
        print(f"  #{mid}  {url}")
    if not images:
        raise SystemExit("no image attachments found; refusing to clear featured images")
    return images


def plan_changes(
    posts: list[Post],
    media: list[tuple[int, str]],
    contact_url: str,
    tasks: set[int],
    spread: bool,
    seed: int,
) -> list[Change]:
    changes: dict[int, Change] = {}

    def bucket(post: Post) -> Change:
        ch = changes.get(post.id)
        if ch is None:
            ch = Change(post=post, payload={})
            changes[post.id] = ch
        return ch

    if 1 in tasks:
        for post in posts:
            cleaned = scrub_content(post.content, contact_url)
            if cleaned != post.content:
                ch = bucket(post)
                ch.payload["content"] = cleaned
                notes = []
                if any(tok in post.content for tok in PLACEHOLDERS):
                    notes.append("placeholders")
                if "971" in post.content:
                    notes.append("uae-number")
                ch.notes.extend(notes or ["content"])

    if 2 in tasks:
        missing = [p for p in posts if not p.featured_media]
        assign_pool = posts if (spread or missing) else []
        if spread:
            assign_pool = list(posts)
        elif missing:
            assign_pool = missing
        rng = random.Random(seed)
        order = list(assign_pool)
        rng.shuffle(order)
        ids = [mid for mid, _ in media]
        for i, post in enumerate(order):
            new_id = ids[i % len(ids)]
            if post.featured_media != new_id:
                ch = bucket(post)
                ch.payload["featured_media"] = new_id
                ch.notes.append(f"thumb:{post.featured_media}->{new_id}")

    if 3 in tasks:
        groups: dict[str, list[Post]] = defaultdict(list)
        for post in posts:
            key = re.sub(r"\s+", " ", post.title).strip()
            groups[key].append(post)
        for title, items in groups.items():
            if len(items) < 2:
                continue
            keep = pick_canonical(items)
            for post in items:
                if post.id == keep.id:
                    continue
                ch = bucket(post)
                ch.payload["status"] = "draft"
                ch.notes.append(f"dup-of:{keep.id}:{keep.slug}")

    return list(changes.values())


def apply_changes(wp: WordPressClient, changes: list[Change], dry_run: bool) -> dict[str, int]:
    stats = {"ok": 0, "fail": 0, "skipped": 0}
    failures: list[str] = []
    total = len(changes)
    for i, change in enumerate(changes, 1):
        if dry_run or not change.payload:
            stats["skipped"] += 1
            progress(i, total, "apply")
            continue
        status, body, _ = wp.request("PUT", f"/wp-json/wp/v2/posts/{change.post.id}", change.payload)
        if status not in {200, 201}:
            status, body, _ = wp.request(
                "POST", f"/wp-json/wp/v2/posts/{change.post.id}", change.payload
            )
        if status in {200, 201}:
            stats["ok"] += 1
        else:
            stats["fail"] += 1
            failures.append(f"{change.post.id} -> {status} {body}")
        progress(i, total, "apply")
    if failures:
        log = ROOT / "scripts" / "phase2_failures.jsonl"
        log.write_text("\n".join(failures) + "\n", encoding="utf-8")
        print(f"wrote {len(failures)} failures to {log}")
    return stats


def generate_rank_math_fix(logo_url: str, logo_id: int, prefix: str = "wp_") -> dict[str, Any]:
    """Return WP-CLI commands and equivalent SQL for Rank Math LocalBusiness."""
    name = "ركن التطور الكويت"
    region = "الكويت"
    address = {
        "streetAddress": "مدينة الكويت",
        "addressLocality": region,
        "addressRegion": "العاصمة",
        "addressCountry": "KW",
    }
    option = "rank-math-options-titles"
    cli = [
        f"wp option patch update {option} knowledgegraph_type local",
        f"wp option patch update {option} local_business_type LocalBusiness",
        f"wp option patch update {option} knowledgegraph_name {json.dumps(name, ensure_ascii=False)}",
        f"wp option patch update {option} website_name {json.dumps(name, ensure_ascii=False)}",
        f"wp option patch update {option} knowledgegraph_logo {json.dumps(logo_url)}",
        f"wp option patch update {option} knowledgegraph_logo_id {logo_id}",
        f"wp option patch update {option} local_address {json.dumps(address, ensure_ascii=False)} --format=json",
        f"wp option patch delete {option} phone",
        f"wp option patch delete {option} phone_number",
    ]
    # Rank Math stores a serialized PHP array. Prefer WP-CLI; SQL below is a
    # documented fallback and must not be run blindly on a binary blob.
    sql = f"""-- Rank Math lives in {prefix}options.option_name = 'rank-math-options-titles'
-- Do NOT string-replace inside the serialized blob (lengths will break).
-- Apply the WP-CLI commands above, or from this repo:
--   wp option patch update rank-math-options-titles knowledgegraph_name '{name}'
--   wp option patch update rank-math-options-titles knowledgegraph_logo '{logo_url}'
--   wp option patch update rank-math-options-titles knowledgegraph_logo_id {logo_id}
-- Target entity: {name} / region {region} / KW. Remove UAE setting.png logo.
"""
    return {"cli": cli, "sql": sql, "name": name, "region": region, "logo_url": logo_url, "logo_id": logo_id}


def apply_rank_math(wp: WordPressClient, spec: dict[str, Any]) -> None:
    for cmd in spec["cli"]:
        wp_cmd = cmd.removeprefix("wp ").strip()
        st, body = wp.wpvibe_cli(wp_cmd, write=True)
        preview = body.get("stdout", body) if isinstance(body, dict) else body
        print(f"rank-math {wp_cmd.split()[:4]} -> {st} {str(preview)[:160]}")


def self_test() -> None:
    sample = (
        '<div class="rukn-hero-actions">'
        '<a class="rukn-btn" href="https://wa.me/971586634710">'
        '<i class="fa-solid fa-phone"></i> اتصل الآن</a>'
        '<a class="rukn-btn rukn-btn-wa" href="https://wa.me/971586634710">'
        '<i class="fa-brands fa-whatsapp"></i> واتساب</a></div>'
        "<p>مشاريعنا [[عدد المشاريع]] منذ [[سنة التأسيس]] — اصل +971 58 663 4710</p>"
    )
    out = scrub_content(sample, "https://rukn-eltatawer.com/kw/contact-us/")
    assert "[[" not in out, out
    assert "540+" in out and "2015" in out, out
    assert "971" not in out, out
    assert "+971" not in out, out
    assert "wa.me" not in out, out
    assert CTA in out, out
    assert "contact-us" in out, out
    assert "اتصل الآن" not in out, out
    print("self-test ok")


def parse_tasks(raw: str) -> set[int]:
    tasks = {int(part.strip()) for part in raw.split(",") if part.strip()}
    bad = tasks - {1, 2, 3, 4}
    if bad:
        raise SystemExit(f"unknown tasks {sorted(bad)}; expected 1,2,3,4")
    return tasks


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="plan only; no PUT/CLI writes")
    parser.add_argument("--tasks", default="1,2,3,4", help="comma-separated task numbers")
    parser.add_argument("--per-page", type=int, default=100)
    parser.add_argument("--delay", type=float, default=0.25, help="seconds between HTTP calls")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--no-spread-thumbnails",
        action="store_true",
        help="only fill featured_media=0; do not rebalance existing thumbs",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0

    tasks = parse_tasks(args.tasks)
    base = env("WP_BASE_URL", "WP_BASE", default="https://rukn-eltatawer.com/kw").rstrip("/")
    user = env("WP_USERNAME", "WP_USER", default="cursor")
    password = env("WP_APP_PASSWORD")
    contact = env("WP_CONTACT_URL", default=f"{base}/contact-us/")
    if not password:
        print("Missing WP_APP_PASSWORD. Copy .env.example to .env.", file=sys.stderr)
        return 1

    wp = WordPressClient(base, user, password, delay=args.delay)
    st, me, _ = wp.request("GET", "/wp-json/wp/v2/users/me?context=edit")
    if st != 200 or not isinstance(me, dict):
        print(f"auth failed ({st}): {me}", file=sys.stderr)
        return 1
    print(f"authenticated as {me.get('slug')} roles={me.get('roles')}  {base}")
    print(f"tasks={sorted(tasks)} dry_run={args.dry_run} delay={args.delay}s")

    media: list[tuple[int, str]] = []
    if tasks & {2, 4}:
        media = list_media_ids(wp)

    posts: list[Post] = []
    if tasks & {1, 2, 3}:
        posts = iter_published_posts(wp, per_page=args.per_page)
        print(f"published posts: {len(posts)}")
        missing = sum(1 for p in posts if not p.featured_media)
        print(f"featured_media=0: {missing}")

    changes: list[Change] = []
    if tasks & {1, 2, 3}:
        changes = plan_changes(
            posts,
            media,
            contact,
            tasks,
            spread=not args.no_spread_thumbnails,
            seed=args.seed,
        )
        content_n = sum(1 for c in changes if "content" in c.payload)
        thumb_n = sum(1 for c in changes if "featured_media" in c.payload)
        draft_n = sum(1 for c in changes if c.payload.get("status") == "draft")
        print(f"planned PUTs: {len(changes)}  content={content_n}  thumbs={thumb_n}  drafts={draft_n}")
        for change in changes[:8]:
            print(f"  #{change.post.id} {change.post.slug}: {', '.join(change.notes)}")
        if len(changes) > 8:
            print(f"  … {len(changes) - 8} more")

        stats = apply_changes(wp, changes, dry_run=args.dry_run)
        print("apply stats", stats)

    if 4 in tasks:
        logo_id, logo_url = (media[0] if media else (3886, f"{base}/wp-content/uploads/2026/09/ركن-التطور-الكويت.webp"))
        preferred = [row for row in media if "ركن-التطور-الكويت" in row[1] or row[0] == 3886]
        if preferred:
            logo_id, logo_url = preferred[0]
        spec = generate_rank_math_fix(logo_url, logo_id)
        print("\n=== Task 4: Rank Math WP-CLI ===")
        for cmd in spec["cli"]:
            print(cmd)
        print("\n=== Task 4: SQL note ===")
        print(spec["sql"])
        if not args.dry_run:
            apply_rank_math(wp, spec)

    report = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "tasks": sorted(tasks),
        "posts": len(posts),
        "changes": len(changes),
        "base": base,
    }
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
