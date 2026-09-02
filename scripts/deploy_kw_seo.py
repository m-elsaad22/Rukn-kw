#!/usr/bin/env python3
"""Deploy Kuwait SEO snippet, English hub pages, and disable junk WPCode snippets."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, "/workspace/scripts")
from wp_kw_client import BASE, TOKEN, cli

PHONE = "+971586634710"
PHONE_DISP = "+971 58 663 4710"
EMAIL = "m@rukn-eltatawer.com"
ICON = "https://www.rukn-eltatawer.com/wp-content/uploads/icon/setting.png"


def rest(route, method="GET", body=None, timeout=180):
    url = BASE + route
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Basic {TOKEN}")
    if body is not None:
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            return resp.getcode(), json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = raw[:4000]
        return e.code, parsed


def snippet(payload):
    return rest("/wpvibe/v1/code-snippet", method="POST", body=payload, timeout=180)


def page_html(h1, lede, sections):
    parts = [f"<h2>{h1}</h2>", f"<p>{lede}</p>"]
    for heading, body in sections:
        parts.append(f"<h3>{heading}</h3>")
        if isinstance(body, list):
            parts.append("<ul>" + "".join(f"<li>{x}</li>" for x in body) + "</ul>")
        else:
            parts.append(f"<p>{body}</p>")
    parts.append(
        "<p>Call or WhatsApp "
        f'<a href="tel:{PHONE}">{PHONE_DISP}</a> · '
        f'<a href="mailto:{EMAIL}">{EMAIL}</a>. Quotes are issued in Kuwaiti dinar after an on-site visit.</p>'
    )
    return "\n".join(parts)


SERVICES = [
    (
        "water-leak-detection",
        "Water Leak Detection in Kuwait",
        "Thermal leak detection without breaking tiles. We locate roof, bathroom and pipe leaks in Kuwait villas and apartments before any demolition.",
        [
            (
                "Why leaks spread fast in Kuwait",
                "Roof tanks, strong AC condensate and coastal humidity in Hawalli and Ahmadi hide moisture inside walls. We map the source with thermal cameras and moisture meters, then hand you a photo report in Arabic or English.",
            ),
            (
                "What you receive",
                [
                    "Non-destructive inspection of roofs, bathrooms, kitchens and wet walls",
                    "Marked leak points and a written scope before tiling is opened",
                    "Repair options priced in KWD after diagnosis — not a phone guess",
                ],
            ),
        ],
    ),
    (
        "roof-insulation",
        "Roof Insulation in Kuwait",
        "Polyurethane foam and membrane roof insulation built for Kuwait summers above 45°C and winter rain on flat villa roofs.",
        [
            (
                "Heat, tanks and flat roofs",
                "Most Kuwait homes store water on the roof. Poor insulation cooks the top floor and lets tank overflow seep into rooms. We inspect slope, existing foam and tank bases before specifying foam, torch-on membrane or a hybrid system.",
            ),
            (
                "Coverage",
                "Capital, Hawalli, Farwaniya, Ahmadi, Jahra and Mubarak Al-Kabeer — including chalets and industrial sheds in Ahmadi.",
            ),
        ],
    ),
    (
        "waterproofing",
        "Waterproofing and Thermal Insulation",
        "Waterproofing for bathrooms, tanks, basements and facades, plus thermal coats that cut indoor heat load in Kuwait.",
        [
            (
                "Where water actually enters",
                "Expansion joints, tank rooms, balcony doors and poorly sloped roofs. We treat the wet layer, not only the paint, and we do not start until moisture readings drop.",
            ),
        ],
    ),
    (
        "general-maintenance",
        "General Home Maintenance in Kuwait",
        "One crew for plumbing, electrics, doors, gypsum and minor civil repairs so you are not coordinating three contractors.",
        [
            (
                "How we work",
                "A technician visits, lists defects with photos, and sends a KWD quote. Recurring contracts are available for villas and small buildings.",
            ),
        ],
    ),
    (
        "building-maintenance",
        "Building Maintenance",
        "Crack repair, facade touch-ups, wet-area restoration and planned maintenance for residential buildings in Kuwait.",
        [
            (
                "Typical Kuwait building issues",
                "Hairline cracks from thermal movement, spalling around AC sleeves, and leaking expansion joints. We document each elevation before scaffolding or cradles go up.",
            ),
        ],
    ),
    (
        "plumbing",
        "Plumbing Services in Kuwait",
        "Pipe repair, mixer replacement, water-heater work and pressure tests for villas and apartments.",
        [
            (
                "Hard water and roof tanks",
                "Kuwait water leaves scale in heaters and mixers. We check the roof tank, downpipes and wet walls together so a ‘small drip’ is not actually a tank overflow.",
            ),
        ],
    ),
    (
        "drain-cleaning",
        "Drain Unblocking",
        "High-pressure jetting and camera inspection for kitchen, bathroom and main stacks — without flooding the neighbour below.",
        [
            (
                "When to call",
                "Slow floor drains, bad odour from the stack, or backups after a sandstorm. We jet, camera-check and only open floors if the line is collapsed.",
            ),
        ],
    ),
    (
        "electrical",
        "Electrical Works",
        "DB checks, lighting, extra sockets and fault finding to Kuwait load — especially summer AC circuits.",
        [
            (
                "Safety first",
                "We isolate the circuit, test residual current devices, and will not add load on an undersized breaker just to finish the same day.",
            ),
        ],
    ),
    (
        "ac-maintenance",
        "AC Installation and Maintenance",
        "Split and central AC cleaning, gas charge, coil wash and seasonal contracts before Kuwait’s May–September peak.",
        [
            (
                "Dust, salt and 50°C condensers",
                "Outdoor units on Ahmadi and Salmiya roofs take salt and dust. A proper service is coil wash, drain flush, electrical check and a written reading — not perfume in the vents.",
            ),
        ],
    ),
    (
        "cleaning",
        "Home Cleaning and Disinfection",
        "Deep cleaning for villas, apartments and offices: kitchens, bathrooms, floors and roof-tank rooms with materials safe around children.",
        [
            (
                "Move-in and post-renovation",
                "We schedule around your building’s quiet hours and leave wet areas dry. Tank cleaning is quoted separately after a roof inspection.",
            ),
        ],
    ),
    (
        "pest-control",
        "Pest Control in Kuwait",
        "Licensed treatment for cockroaches, ants, rodents and stored-product insects in kitchens, stores and villa gardens.",
        [
            (
                "What we treat",
                "German cockroaches in cabinets, ants from irrigation, and rodents around waste rooms. You get the product name, waiting time and a follow-up visit if activity returns.",
            ),
        ],
    ),
    (
        "landscaping",
        "Garden Landscaping",
        "Irrigation, shade, artificial or natural turf and planting that survives Kuwait heat and saline irrigation water.",
        [
            (
                "Design that lasts summer",
                "We plan drip lines, timer zones and soil replacement so the garden does not die in July. Chalets and rooftop planters in coastal areas get salt-tolerant specs.",
            ),
        ],
    ),
    (
        "swimming-pools",
        "Swimming Pool Construction and Maintenance",
        "Leak checks, tiling, pumps, sand filters and seasonal commissioning for villa and chalet pools.",
        [
            (
                "Common pool failures",
                "Emptying a pool in August without covering it can crack finishes. We test structure and plumbing before recommending a refill, retile or liner.",
            ),
        ],
    ),
    (
        "painting",
        "Painting and Decorating",
        "Interior and exterior painting with primers suited to dusty facades and humid bathrooms.",
        [
            (
                "Prep matters more than colour",
                "We wash, fill and spot-prime. Exterior coats are scheduled for early morning so they do not flash-dry at midday.",
            ),
        ],
    ),
    (
        "gypsum-board",
        "Gypsum Board Installation",
        "Ceilings, bulkheads and AC pelmets in moisture-resistant boards for Kuwait bathrooms and kitchens.",
        [
            (
                "AC and gypsum",
                "We leave access panels at valves and never trap a leak behind a sealed ceiling. Joints are taped and sanded before paint.",
            ),
        ],
    ),
    (
        "interior-design",
        "Interior Fit-out",
        "Practical interior works: partitions, lighting layouts, built-ins and finishing coordinated with plumbing and AC.",
        [
            (
                "One sequence",
                "Design drawings, a KWD bill of quantities, then site works in order — MEP first, finishes last — so you are not ripping new paint for a pipe.",
            ),
        ],
    ),
]

GOVS = [
    (
        "kuwait-city",
        "Home Services in Kuwait City (Capital)",
        "Rukn El Tatawer serves Kuwait City and the Capital Governorate: Sharq, Mirqab, Dasma, Daiya and nearby blocks. Parking and building access are agreed before the visit.",
        "Capital apartments often hide AC condensate leaks in false ceilings. We diagnose first, then quote in KWD.",
    ),
    (
        "hawalli",
        "Home Services in Hawalli",
        "Hawalli, Salmiya, Jabriya, Shaab and nearby coastal blocks — humidity and older stacks need careful leak and AC work.",
        "We work around tight parking and building quiet hours. Written access notes go on the job sheet.",
    ),
    (
        "farwaniya",
        "Home Services in Farwaniya",
        "Farwaniya, Khaitan, Riggae and surrounding areas: family villas and apartment buildings with roof tanks and shared stacks.",
        "Same-day visits depend on access. Diagnosis is still on site — we do not price unseen leaks.",
    ),
    (
        "ahmadi",
        "Home Services in Ahmadi",
        "Ahmadi, Fahaheel, Mahboula, Fintas and coastal chalets. Salt air attacks AC coils, steel and pool plant.",
        "We specify coastal-grade materials for outdoor units, roof coatings and pool equipment.",
    ),
    (
        "jahra",
        "Home Services in Jahra",
        "Jahra and west Kuwait: larger plots, longer pipe runs and dusty outdoor units that need real coil washing, not perfume.",
        "Travel time is included in the appointment window you receive on WhatsApp.",
    ),
    (
        "mubarak-al-kabeer",
        "Home Services in Mubarak Al-Kabeer",
        "Mubarak Al-Kabeer, Qurain, Adan and nearby villas — typical issues are roof foam, bathroom leaks and summer AC load.",
        "We send a photo report after inspection so you can approve the scope before tiling is opened.",
    ),
]


def build_pages():
    pages = []
    pages.append(
        {
            "slug": "english",
            "parent": 0,
            "title": "Home Services in Kuwait",
            "rank_title": "Home Services Company in Kuwait | Rukn El Tatawer",
            "rank_desc": "Leak detection, roof insulation, AC, plumbing, cleaning and pest control across Kuwait’s six governorates. On-site diagnosis, then a written quote in KWD.",
            "content": page_html(
                "Home services across Kuwait — diagnosis before repair",
                "Rukn El Tatawer is the Kuwait branch of a regional home-services company. We work in the Capital, Hawalli, Farwaniya, Ahmadi, Jahra and Mubarak Al-Kabeer. Quotes are in Kuwaiti dinar after a technician sees the site — not after a phone description.",
                [
                    (
                        "What we handle",
                        "Water leak detection without breaking tiles, roof and tank waterproofing, general and building maintenance, plumbing and drain clearing, electrics, AC installation and seasonal service, deep cleaning, licensed pest control, gardens, pools, painting, gypsum and interior finishing.",
                    ),
                    (
                        "Kuwait, not the UAE",
                        "This site is for the State of Kuwait only. We schedule around local building rules, roof-tank layouts and Friday–Saturday weekends. The operating number currently listed is a regional line; WhatsApp and calls reach the Kuwait coordination desk.",
                    ),
                    (
                        "Governorates we cover",
                        [
                            '<a href="/kw/english/kuwait-city/">Kuwait City (Capital)</a>',
                            '<a href="/kw/english/hawalli/">Hawalli</a>',
                            '<a href="/kw/english/farwaniya/">Farwaniya</a>',
                            '<a href="/kw/english/ahmadi/">Ahmadi</a>',
                            '<a href="/kw/english/jahra/">Jahra</a>',
                            '<a href="/kw/english/mubarak-al-kabeer/">Mubarak Al-Kabeer</a>',
                        ],
                    ),
                    (
                        "How a job starts",
                        "Send the area and a photo on WhatsApp. We book an inspection, issue a written scope and price, then execute. You keep one contractor for leak, insulation, AC and finishing instead of three separate crews.",
                    ),
                ],
            ),
        }
    )
    pages.append(
        {
            "slug": "about-us",
            "parent_slug": "english",
            "title": "About Rukn El Tatawer Kuwait",
            "rank_title": "About Us | Rukn El Tatawer Kuwait Home Services",
            "rank_desc": "Who we are in Kuwait: one crew for leak detection, insulation, AC, plumbing, cleaning and pest control, with written quotes after on-site diagnosis.",
            "content": page_html(
                "About Rukn El Tatawer in Kuwait",
                "We are a home and building services team operating in the State of Kuwait. The company also serves neighbouring markets; this website and these pages are written only for Kuwait governorates, Kuwaiti dinar pricing and local building conditions.",
                [
                    (
                        "How we differ from a typical ‘send a plumber’ call",
                        "A technician inspects with tools (thermal camera, moisture meter, AC gauges as needed), you receive photos, then a scope of work. We do not break tiles to ‘find’ a leak that could have been mapped first.",
                    ),
                    (
                        "Team and coverage",
                        "Work is dispatched across the six governorates. Coastal jobs in Hawalli and Ahmadi get materials specified for salt and humidity. Inland Jahra jobs allow for dust load on condensers and longer pipe runs.",
                    ),
                    (
                        "Languages",
                        "Supervisors coordinate in Arabic and English. Reports can be issued in either language on request.",
                    ),
                ],
            ),
        }
    )
    pages.append(
        {
            "slug": "contact-us",
            "parent_slug": "english",
            "title": "Contact Rukn El Tatawer Kuwait",
            "rank_title": "Contact Us | Rukn El Tatawer Kuwait",
            "rank_desc": f"Call or WhatsApp {PHONE_DISP} for home services in Kuwait. Email {EMAIL}. We cover all six governorates, 24/7 coordination.",
            "content": page_html(
                "Contact the Kuwait team",
                "Tell us the governorate, the service and a photo of the issue. We reply with an inspection window. There is no desk quote for hidden leaks or AC gas — those need a visit.",
                [
                    (
                        "Direct lines",
                        [
                            f'Phone / WhatsApp: <a href="tel:{PHONE}">{PHONE_DISP}</a>',
                            f'Email: <a href="mailto:{EMAIL}">{EMAIL}</a>',
                            "Coverage: Capital, Hawalli, Farwaniya, Ahmadi, Jahra, Mubarak Al-Kabeer",
                            "Hours: coordination 24/7 — site visits by appointment",
                            "Currency: KWD",
                        ],
                    ),
                    (
                        "Note on the phone code",
                        "The published number uses a regional +971 line until a dedicated +965 number is issued. WhatsApp messages still reach the Kuwait jobs desk. Do not confuse this site with the UAE or Saudi branches.",
                    ),
                ],
            ),
        }
    )
    pages.append(
        {
            "slug": "privacy-policy",
            "parent_slug": "english",
            "title": "Privacy Policy",
            "rank_title": "Privacy Policy | Rukn El Tatawer Kuwait",
            "rank_desc": "How Rukn El Tatawer Kuwait handles contact details, job photos and messages sent through this website or WhatsApp.",
            "content": page_html(
                "Privacy policy — Kuwait website",
                "This policy applies to rukn-eltatawer.com/kw/ and English pages under /kw/english/. We collect only what is needed to schedule and deliver a home-service job in Kuwait.",
                [
                    (
                        "What we collect",
                        "Name, phone, area, message contents, photos you send, and technical logs (IP, browser) needed to keep the site secure.",
                    ),
                    (
                        "Use",
                        "We use this data to reply, visit the site, issue a quote and perform the work. We do not sell personal data. Job photos stay in the job file.",
                    ),
                    (
                        "Contact for privacy requests",
                        f'Email {EMAIL}. You may ask for correction or deletion of contact records that are not required for accounting or warranty.',
                    ),
                ],
            ),
        }
    )
    pages.append(
        {
            "slug": "services",
            "parent_slug": "english",
            "title": "Home Services in Kuwait",
            "rank_title": "All Home Services in Kuwait | Rukn El Tatawer",
            "rank_desc": "16 home services in Kuwait: leaks, insulation, AC, plumbing, cleaning, pest control, gardens, pools, painting and interiors. Written KWD quotes after inspection.",
            "content": page_html(
                "All services — one contractor in Kuwait",
                "Pick the trade you need. Each English service page explains how the work is done under Kuwait climate and building conditions. Arabic location pages remain the detailed local guides.",
                [
                    (
                        "Service list",
                        [f'<a href="/kw/english/services/{s[0]}/">{s[1]}</a>' for s in SERVICES],
                    ),
                ],
            ),
        }
    )
    for slug, title, lede, sections in SERVICES:
        pages.append(
            {
                "slug": slug,
                "parent_slug": "services",
                "title": title,
                "rank_title": f"{title} | Rukn El Tatawer",
                "rank_desc": lede[:160],
                "content": page_html(title, lede, sections),
            }
        )
    for slug, title, lede, extra in GOVS:
        pages.append(
            {
                "slug": slug,
                "parent_slug": "english",
                "title": title,
                "rank_title": f"{title} | Rukn El Tatawer",
                "rank_desc": lede[:160],
                "content": page_html(
                    title,
                    lede,
                    [
                        ("Local conditions", extra),
                        (
                            "Services available here",
                            'See the full list on <a href="/kw/english/services/">English services</a> or browse the Arabic city pages for neighbourhood-level guides.',
                        ),
                    ],
                ),
            }
        )
    return pages


def find_page(slug, parent=0):
    code, data = rest(f"/wp/v2/pages&slug={slug}&parent={parent}&per_page=20")
    if code != 200 or not isinstance(data, list):
        return None
    for p in data:
        if p.get("slug") == slug:
            return p
    return None


def upsert_page(spec, parent_id=0):
    existing = find_page(spec["slug"], parent_id)
    body = {
        "title": spec["title"],
        "slug": spec["slug"],
        "status": "publish",
        "parent": parent_id,
        "content": spec["content"],
        "comment_status": "closed",
        "ping_status": "closed",
    }
    if existing:
        code, data = rest(f"/wp/v2/pages/{existing['id']}", method="POST", body=body)
        pid = existing["id"]
        action = "update"
    else:
        code, data = rest("/wp/v2/pages", method="POST", body=body)
        pid = data.get("id") if isinstance(data, dict) else None
        action = "create"
    print(f"PAGE {action} {spec['slug']} parent={parent_id} http={code} id={pid}")
    if pid and code in (200, 201):
        rest(
            f"/wp/v2/pages/{pid}",
            method="POST",
            body={
                "meta": {
                    "rank_math_title": spec.get("rank_title") or spec["title"],
                    "rank_math_description": spec.get("rank_desc") or "",
                    "rank_math_focus_keyword": spec["title"],
                }
            },
        )
    return pid


def deactivate_junk_snippets():
    dummy = "if (!defined('ABSPATH')) { return; }\n"
    for sid, title in [
        (2539, "Rukn KW completeness (unused duplicate)"),
        (2540, "Rukn KW completeness (unused duplicate)"),
        (2541, "Rukn KW completeness (unused duplicate)"),
        (3810, "DISABLED subscribe blurb"),
    ]:
        code, data = snippet(
            {
                "id": sid,
                "title": title,
                "code": dummy,
                "code_type": "php",
                "location": "everywhere",
            }
        )
        active = data.get("active") if isinstance(data, dict) else None
        print(f"SNIPPET {sid} http={code} active={active} msg={str(data)[:180]}")


def deploy_main_snippet():
    with open("/workspace/scripts/rukn-kw-snippet.php", "r", encoding="utf-8") as f:
        code_src = f.read()
    if code_src.startswith("<?php"):
        code_src = code_src.split("\n", 1)[-1]
    payload = {
        "id": 2538,
        "title": "Rukn KW completeness",
        "code": code_src,
        "code_type": "php",
        "location": "everywhere",
    }
    code, data = snippet(payload)
    print("MAIN SNIPPET", code)
    if isinstance(data, dict):
        print("id", data.get("id"), "active", data.get("active"))
        print("enable_url", data.get("enable_url"))
        print("next_step", data.get("next_step"))
        print("stored_len", len(data.get("stored_code") or ""))
    else:
        print(data)
    activate_wpcode_runtime(code_src)
    return data


def activate_wpcode_runtime(code_src: str):
    """WPCode executes option wpcode_snippets, not the draft CPT row.

    Keep disable-comments plus the Kuwait SEO layer in the live everywhere slot.
    """
    import base64 as b64

    comments = """add_action("admin_init", function () {
    global $pagenow;
    if ($pagenow === "edit-comments.php") {
        wp_safe_redirect(admin_url());
        exit;
    }
    remove_meta_box("dashboard_recent_comments", "dashboard", "normal");
    foreach (get_post_types() as $post_type) {
        if (post_type_supports($post_type, "comments")) {
            remove_post_type_support($post_type, "comments");
            remove_post_type_support($post_type, "trackbacks");
        }
    }
});
add_filter("comments_open", "__return_false", 20, 2);
add_filter("pings_open", "__return_false", 20, 2);
add_filter("comments_array", "__return_empty_array", 10, 2);
add_action("admin_menu", function () { remove_menu_page("edit-comments.php"); });
add_action("init", function () {
    if (is_admin_bar_showing()) {
        remove_action("admin_bar_menu", "wp_admin_bar_comments_menu", 60);
    }
});
"""
    encoded = b64.b64encode((comments + "\n" + code_src).encode("utf-8")).decode("ascii")
    php = 'eval(base64_decode("' + encoded + '"));'
    cmd = "option patch update wpcode_snippets everywhere 0 code '" + php + "'"
    res = cli(cmd, confirm=True)
    print("wpcode_snippets runtime", res.get("exit_code"), (res.get("stdout") or res.get("stderr") or "")[:240])
    cli("plugin activate insert-headers-and-footers", confirm=True)


def main():
    if not TOKEN:
        print("Missing credentials")
        return 1

    print("=== Arabic pages: h1 to h2, Kuwait copy ===")
    ar_about = """
<section>
<h2>من نحن — ركن التطور الكويت</h2>
<p>ركن التطور شركة خدمات منزلية تعمل داخل دولة الكويت فقط: كشف تسربات المياه بدون تكسير، عزل الأسطح والخزانات، الصيانة العامة، التكييف، السباكة والكهرباء، التنظيف والتعقيم، مكافحة الحشرات، تنسيق الحدائق والمسابح، والصبغ والديكورات.</p>
<p>لست في الإمارات أو السعودية — هذه الصفحات مكتوبة لمحافظات الكويت الست، والتسعير بعد المعاينة بالدينار الكويتي. الفريق يعاين الموقع قبل التسعير، ويسلّم تقريرًا مصورًا يوضح المشكلة ومصدرها، ثم ينفّذ وفق عرض سعر مكتوب.</p>
<h3>لماذا ركن التطور في الكويت؟</h3>
<ul>
<li>تشخيص بالأجهزة قبل التكسير أو الإصلاح.</li>
<li>عرض سعر ومدة مكتوبة بالدينار الكويتي قبل البدء.</li>
<li>تغطية: العاصمة، حولي، الفروانية، الأحمدي، الجهراء، مبارك الكبير، مع السالمية والفنطاس.</li>
<li>خدمات متعددة من جهة واحدة بدل التعامل مع عدة مقاولين.</li>
<li>متابعة بعد التسليم، وتنسيق بالعربي والإنجليزي.</li>
</ul>
<h3>نطاق الخدمة</h3>
<p>مناخ الكويت (حرارة الصيف، رطوبة الساحل، خزانات الأسطح) يختلف عن أي سوق آخر. مواصفات العزل والتكييف والمواد تُختار لهذا الواقع، لا بنسخ عقد من دولة أخرى.</p>
<p>English: <a href="/kw/english/about-us/">About Rukn El Tatawer in Kuwait</a>.</p>
</section>
"""
    for pid in (1279, 1280, 1281):
        code, data = rest(f"/wp/v2/pages/{pid}&context=edit")
        raw = ((data.get("content") or {}).get("raw") if isinstance(data, dict) else "") or ""
        new = ar_about if pid == 1280 else raw.replace("<h1>", "<h2>").replace("</h1>", "</h2>")
        if new.strip() != raw.strip():
            c2, d2 = rest(f"/wp/v2/pages/{pid}", method="POST", body={"content": new.strip()})
            print("AR page", pid, c2, d2.get("slug") if isinstance(d2, dict) else str(d2)[:200])
        else:
            print("AR page", pid, "unchanged")

    print("=== deactivate junk snippets ===")
    deactivate_junk_snippets()

    print("=== upsert English pages ===")
    pages = build_pages()
    ids = {}
    # parent order: en, then children of en, then children of services
    for spec in pages:
        parent_slug = spec.get("parent_slug")
        parent_id = 0 if not parent_slug else ids.get(parent_slug, 0)
        if spec.get("parent_slug") and not parent_id:
            print("SKIP missing parent", spec["slug"], spec["parent_slug"])
            continue
        pid = upsert_page(spec, parent_id)
        ids[spec["slug"]] = pid

    print("=== main snippet ===")
    deploy_main_snippet()

    print("=== menu English link ===")
    try:
        res = cli("menu item add-custom 40 English https://rukn-eltatawer.com/kw/english/", confirm=True)
        print("menu", res.get("exit_code"), (res.get("stdout") or res.get("stderr") or "")[:300])
    except Exception as e:
        print("menu fail", e)

    print("=== options ===")
    for cmd in [
        "option update blogdescription 'شركة ركن التطور للخدمات المنزلية في الكويت: كشف تسربات، عزل، تكييف، سباكة، تنظيف ومكافحة حشرات في كل المحافظات. أسعار بالدينار الكويتي بعد المعاينة.'",
        "litespeed-purge all",
        "cache flush",
    ]:
        try:
            res = cli(cmd, confirm=True)
            print(cmd[:50], res.get("exit_code"), (res.get("stderr") or res.get("stdout") or "")[:200])
        except Exception as e:
            print("opt fail", cmd, e)

    print("DONE ids", ids)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
