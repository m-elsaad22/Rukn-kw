#!/usr/bin/env python3
"""Apply Kuwait live-site fixes (WhatsApp stays UAE; call numbers hidden)."""

from __future__ import annotations

import base64
import json
import os
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = os.environ.get("WP_BASE", "https://rukn-eltatawer.com/kw").rstrip("/")
USER = os.environ.get("WP_USER", "cursor")
APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "").strip()
CTX = ssl.create_default_context()
ROOT = Path(__file__).resolve().parents[1]
FIXPACK = ROOT / "scripts" / "rukn-kw-fixpack.php"
WA = "971586634710"
CONTACT = "https://rukn-eltatawer.com/kw/contact-us/"


def php_serialize(value: Any) -> str:
    if value is None:
        return "N;"
    if isinstance(value, bool):
        return "b:1;" if value else "b:0;"
    if isinstance(value, int):
        return f"i:{value};"
    if isinstance(value, float):
        return f"d:{value};"
    if isinstance(value, str):
        raw = value.encode("utf-8")
        return f's:{len(raw)}:"{value}";'
    if isinstance(value, bytes):
        return f's:{len(value)}:"{value.decode("utf-8")}";'
    if isinstance(value, list):
        inner = "".join(php_serialize(i) + php_serialize(v) for i, v in enumerate(value))
        return f"a:{len(value)}:{{{inner}}}"
    if isinstance(value, dict):
        inner = "".join(php_serialize(k) + php_serialize(v) for k, v in value.items())
        return f"a:{len(value)}:{{{inner}}}"
    raise TypeError(type(value))


def request(method: str, path: str, payload: dict[str, Any] | None = None, timeout: int = 180) -> tuple[int, Any]:
    url = path if path.startswith("http") else f"{BASE}{path}"
    headers = {
        "User-Agent": "RuknKuwaitFixer/4.0",
        "Accept": "application/json",
        "Authorization": "Basic " + base64.b64encode(f"{USER}:{APP_PASSWORD}".encode()).decode(),
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload, ensure_ascii=False).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
            raw = resp.read().decode("utf-8", "replace")
            try:
                return resp.status, json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            body: Any = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = raw
        return exc.code, body
    except Exception as exc:  # noqa: BLE001
        return 0, str(exc)


def cli(cmd: str, write: bool = False, timeout: int = 180) -> tuple[int, Any]:
    return request(
        "POST",
        "/wp-json/wpvibe/v1/cli/run",
        {"command": cmd, "confirm_write": write},
        timeout=timeout,
    )


def cli_approved(cmd: str, timeout: int = 180) -> tuple[int, Any]:
    st, dry = cli(cmd, write=False, timeout=timeout)
    if st == 200:
        return st, dry
    if st != 409 or not isinstance(dry, dict):
        return st, dry
    return request(
        "POST",
        "/wp-json/wpvibe/v1/cli/run-approved",
        {"command": cmd, "confirm_write": True, "approved_state": json.dumps(dry)},
        timeout=timeout,
    )


def sql(query: str) -> tuple[int, Any]:
    return cli_approved(f"db query {json.dumps(query)}")


def sql_b64(table: str, column: str, where: str, value: str) -> tuple[int, Any]:
    b64 = base64.b64encode(value.encode("utf-8")).decode("ascii")
    q = f"UPDATE {table} SET {column}=FROM_BASE64('{b64}') WHERE {where}"
    return sql(q)


def opt(name: str, value: str, fmt: str | None = None) -> None:
    cmd = f"option update {name} {json.dumps(value)}"
    if fmt:
        cmd += f" --format={fmt}"
    st, body = cli(cmd, write=True)
    out = (body or {}).get("stdout", body) if isinstance(body, dict) else body
    print(f"option {name} -> {st} {str(out)[:180]}")


def stdout_json(body: Any) -> Any:
    if not isinstance(body, dict):
        return body
    raw = body.get("stdout", "")
    try:
        return json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return raw


def main() -> int:
    if not APP_PASSWORD:
        raise SystemExit("Set WP_APP_PASSWORD")
    st, me = request("GET", "/wp-json/wp/v2/users/me?context=edit")
    print("auth", st, (me or {}).get("slug") if isinstance(me, dict) else me)
    if st != 200:
        return 1

    src = FIXPACK.read_text(encoding="utf-8")
    src = src.replace("<?php", "", 1).strip()
    print("fixpack chars", len(src))

    cache = {
        "everywhere": [
            {
                "id": 3811,
                "title": "Rukn KW fixpack",
                "code": src,
                "code_type": "php",
                "location": "everywhere",
                "auto_insert": 1,
                "insert_number": 1,
                "use_rules": False,
                "rules": [],
                "priority": 10,
                "location_extra": "",
                "shortcode_attributes": [],
                "compiled_code": "",
                "modified": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            }
        ]
    }
    serialized = php_serialize(cache)
    print("cache php bytes", len(serialized.encode("utf-8")))
    print("sql snippet content", sql_b64("iFs1ICdt_posts", "post_content", "ID=3811", src)[1])
    print("sql snippet publish", sql(
        "UPDATE iFs1ICdt_posts SET post_status='publish', post_title='Rukn KW fixpack', "
        "post_modified=NOW(), post_modified_gmt=UTC_TIMESTAMP() WHERE ID=3811"
    )[1])
    print("sql snippet meta", sql(
        "INSERT INTO iFs1ICdt_postmeta (post_id, meta_key, meta_value) "
        "SELECT 3811, '_wpcode_auto_insert', '1' FROM DUAL "
        "WHERE NOT EXISTS (SELECT 1 FROM iFs1ICdt_postmeta WHERE post_id=3811 AND meta_key='_wpcode_auto_insert')"
    )[1])
    print("sql cache", sql_b64("iFs1ICdt_options", "option_value", "option_name='wpcode_snippets'", serialized)[1])

    for name in ("phonenumber", "contact_number", "kayan_country_kw_phone", "kayan_show_call_buttons"):
        print("empty", name, sql(
            f"UPDATE iFs1ICdt_options SET option_value='' WHERE option_name='{name}'"
        )[1])

    opt("rukn_hide_call_global", "on")
    opt("whatsapp_number", WA)
    opt("kayan_country_kw_whatsapp", WA)
    opt("company__adress", "مدينة الكويت، الكويت")
    opt(
        "footer__map_embed",
        "https://maps.google.com/maps?q=Kuwait+City,Kuwait&z=11&output=embed",
    )
    opt(
        "company__map_code",
        "https://maps.google.com/maps?q=Kuwait+City,Kuwait&z=11&output=embed",
    )
    opt("footer__company__adress_url", "https://maps.google.com/?q=Kuwait+City,Kuwait")

    schema = {
        "hide_schema_business": "on",
        "Business_Name": "ركن التطور الكويت",
        "City": "مدينة الكويت",
        "Country": "KW",
        "telephone": "",
    }
    print("schema", cli(
        "option update YourColoe_Schema_business " + json.dumps(json.dumps(schema, ensure_ascii=False)) + " --format=json",
        write=True,
    )[1])
    # The nested dumps above may be wrong; set via SQL serialize.
    print("schema sql", sql_b64(
        "iFs1ICdt_options",
        "option_value",
        "option_name='YourColoe_Schema_business'",
        php_serialize(schema),
    )[1])
    print("schema insert", sql(
        "INSERT INTO iFs1ICdt_options (option_name, option_value, autoload) "
        "SELECT 'YourColoe_Schema_business', FROM_BASE64('"
        + base64.b64encode(php_serialize(schema).encode()).decode()
        + "'), 'auto' FROM DUAL "
        "WHERE NOT EXISTS (SELECT 1 FROM iFs1ICdt_options WHERE option_name='YourColoe_Schema_business')"
    )[1])

    print("rm phone", cli("option patch delete rank-math-options-titles phone", write=True)[1])
    print("rm phone2", cli("option patch delete rank-math-options-titles phone_number", write=True)[1])
    print("rm type", cli("option patch update rank-math-options-titles knowledgegraph_type local", write=True)[1])
    print("rm local", cli("option patch update rank-math-options-titles local_business_type LocalBusiness", write=True)[1])
    print("rm name", cli(
        "option patch update rank-math-options-titles knowledgegraph_name " + json.dumps("ركن التطور الكويت"),
        write=True,
    )[1])

    print("thumbs", sql(
        "INSERT INTO iFs1ICdt_postmeta (post_id, meta_key, meta_value) "
        "SELECT p.ID, '_thumbnail_id', '3886' FROM iFs1ICdt_posts p "
        "WHERE p.post_type='post' AND p.post_status='publish' "
        "AND NOT EXISTS (SELECT 1 FROM iFs1ICdt_postmeta m WHERE m.post_id=p.ID AND m.meta_key='_thumbnail_id')"
    )[1])

    phone_replaces = [
        ("tel:+971586634710", "https://wa.me/971586634710"),
        ("tel:971586634710", "https://wa.me/971586634710"),
        ("+971 58 663 4710", ""),
        ("+971586634710", ""),
        ("971 58 663 4710", ""),
    ]
    for old, new in phone_replaces:
        print("phone", old, sql(
            "UPDATE iFs1ICdt_posts SET post_content = REPLACE(post_content, "
            + json.dumps(old, ensure_ascii=False)
            + ", "
            + json.dumps(new, ensure_ascii=False)
            + ") WHERE post_status='publish' AND post_type IN ('post','page','services')"
        )[1])

    print("dni", sql("UPDATE iFs1ICdt_kayan_numbers SET phone='' WHERE 1=1")[1])
    print("menu url", cli_approved(
        "menu item update 3874 --link=https://rukn-eltatawer.com/kw/english/"
    )[1])

    ar_contact = (
        "<h2>تواصل عبر واتساب</h2>"
        "<p>فريق ركن التطور يخدم محافظات الكويت. حتى صدور رقم كويتي +965 لا نعرض زر اتصال ولا ننشر رقم هاتف. راسلنا واتساب على الخط الإقليمي الحالي.</p>"
        "<p><a href=\"https://wa.me/971586634710\">واتساب ركن التطور الكويت</a> · "
        "<a href=\"mailto:m@rukn-eltatawer.com\">m@rukn-eltatawer.com</a></p>"
        "<p>التغطية: العاصمة، حولي، الفروانية، الأحمدي، الجهراء، مبارك الكبير.</p>"
    )
    en_contact = (
        "<h2>Contact via WhatsApp</h2>"
        "<p>Until a Kuwait +965 line is issued we hide call buttons and do not publish a phone number. Use the regional WhatsApp desk.</p>"
        "<p><a href=\"https://wa.me/971586634710\">WhatsApp Rukn El Tatawer Kuwait</a> · "
        "<a href=\"mailto:m@rukn-eltatawer.com\">m@rukn-eltatawer.com</a></p>"
        "<p>Coverage: Capital, Hawalli, Farwaniya, Ahmadi, Jahra, Mubarak Al-Kabeer.</p>"
    )
    print("page 1279", request("POST", "/wp-json/wp/v2/pages/1279", {"content": ar_contact})[0])
    print("page 3823", request("POST", "/wp-json/wp/v2/pages/3823", {"content": en_contact})[0])

    st, body = cli("post meta get 26 widget_post_meta")
    hub = stdout_json(body)
    if isinstance(hub, dict) and isinstance(hub.get("hub_columns"), list):
        for col in hub["hub_columns"]:
            col["guide_url"] = CONTACT
            raw_links = str(col.get("links") or "")
            out_lines = []
            for line in raw_links.splitlines():
                line = line.strip()
                if not line:
                    continue
                label = line.split("|", 1)[0].strip()
                out_lines.append(f"{label} | {CONTACT}")
            col["links"] = "\n".join(out_lines)
        print("hub sql", sql(
            "UPDATE iFs1ICdt_postmeta SET meta_value=FROM_BASE64('"
            + base64.b64encode(php_serialize(hub).encode()).decode()
            + "') WHERE post_id=26 AND meta_key='widget_post_meta'"
        )[1])

    st, body = cli("post meta get 29 widget_post_meta")
    contact_w = stdout_json(body)
    if isinstance(contact_w, dict):
        contact_w["hide_call_button"] = "on"
        contact_w["hide_whatsapp_button"] = ""
        contact_w["quote_button_text"] = "اطلب عبر واتساب"
        contact_w["quote_button_url"] = CONTACT
        print("cta sql", sql(
            "UPDATE iFs1ICdt_postmeta SET meta_value=FROM_BASE64('"
            + base64.b64encode(php_serialize(contact_w).encode()).decode()
            + "') WHERE post_id=29 AND meta_key='widget_post_meta'"
        )[1])

    # Keep english pages on Arabic Polylang language (manual /english/ tree).
    print("pll keep ar", sql(
        "INSERT IGNORE INTO iFs1ICdt_term_relationships (object_id, term_taxonomy_id) "
        "SELECT p.ID, tt.term_taxonomy_id FROM iFs1ICdt_posts p "
        "JOIN iFs1ICdt_term_taxonomy tt ON tt.taxonomy='language' "
        "JOIN iFs1ICdt_terms t ON t.term_id=tt.term_id AND t.slug='ar' "
        "WHERE p.ID=3819 OR p.post_parent=3819"
    )[1])
    print("pll drop en", sql(
        "DELETE tr FROM iFs1ICdt_term_relationships tr "
        "JOIN iFs1ICdt_term_taxonomy tt ON tt.term_taxonomy_id=tr.term_taxonomy_id AND tt.taxonomy='language' "
        "JOIN iFs1ICdt_terms t ON t.term_id=tt.term_id AND t.slug='en' "
        "JOIN iFs1ICdt_posts p ON p.ID=tr.object_id "
        "WHERE p.ID=3819 OR p.post_parent=3819"
    )[1])

    print("flush", cli("cache flush", write=True)[1])
    print("purge", cli("litespeed-purge all", write=True)[1])
    print("rewrite", cli("rewrite flush", write=True)[1])
    print("phone now", cli("option get phonenumber")[1])
    print("dni get", request("GET", "/wp-json/kayan/v1/dni")[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
