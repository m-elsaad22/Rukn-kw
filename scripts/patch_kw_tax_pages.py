#!/usr/bin/env python3
"""Assign city terms + family categories, and expand thin AR/EN pages.

Does not write Rank Math titles. Leaves the 24 duplicate drafts unpublished.
"""
from __future__ import annotations

import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kw_cities import parse_slug
from kw_service_facts import FACTS, FAMILIES, family_of
from rewrite_kw_articles import load_catalog
from wp_kw_client import rest

CITY_TERM = {
    "kuwait": 2,
    "hawalli": 17,
    "farwaniya": 18,
    "mubarak-al-kabeer": 19,
    "al-ahmadi": 20,
    "al-jahra": 21,
}

FAM_CAT = {
    "cleaning": 3,
    "maintenance": 4,
    "leaks": 5,
    "reno": 6,
    "install": 7,
    "garden": 8,
    "moving": 9,
    "solar": 10,
    "pest": 11,
    "tech": 12,
    "ship": 13,
    "paint": 14,
    "elec": 15,
    "ac": 16,
}

WA = "https://wa.me/971586634710"

FAM_EN = {
    "leaks": "Leak mapping and waterproofing come first. A ceiling stain in Hawalli is often a roof tank or a neighbour’s wet room, not the paint you can see.",
    "ac": "Split and ducted cooling in Kuwait is coil wash, condensate fall and a written reading — not perfume in the vents before May.",
    "cleaning": "Deep cleaning here is dust, grease and tank rooms. Marble and wood get a spot-test; a roof tank is not a mop of the lid.",
    "maintenance": "General and building visits list defects with photos, then a dinar quote. Safety items (live boards, active leaks) go first.",
    "install": "Joinery, gypsum, doors, cameras and cladding start with a site measure. A pretty delivery day is not the test in this climate.",
    "reno": "Renovation and inspection write the wet layer and the board before new tile or paint. We do not decorate over an open source.",
    "garden": "Gardens, irrigation and shade have to survive July and saline water. Turf on builder’s sand is not a garden.",
    "moving": "Moving and storage protect marble, doors and servers. Path width in Capital towers is part of the quote, not an extra at the lift.",
    "solar": "Solar on a Kuwait roof is shade, dust and structure under the array — not a panel count copied from another market.",
    "pest": "Pest work closes food, moisture and cracks. A spray of the visible insect while the harbour stays open is how jobs bounce.",
    "tech": "Locksmiths, carpenters and on-call electricians announce the trade limit before they open a wall or a lock.",
    "ship": "Freight is documents, volume-weight and packing. A dinar guess from a photo of a box is not a booking.",
    "paint": "Paint and decor fail on dust and moisture, not on the colour chip. Exterior coats run early morning so they do not flash-dry.",
    "elec": "Electrics and plumbing isolate the board or the stopcock first. A hot socket is a visit, not a larger adaptor.",
}


AR_CONTACT = f"""<section>
<h2>تواصل مع مكتب الكويت</h2>
<p>راسل واتساب باسم المنطقة، ونوع الخدمة، وصورة للنقطة. نرد بموعد معاينة. لا يُثبَّت مبلغ بالدينار الكويتي من وصف هاتفي أو صورة وحدها.</p>
<p><a href="{WA}">واتساب ركن التطور الكويت</a></p>
<p>البريد: <a href="mailto:m@rukn-eltatawer.com">m@rukn-eltatawer.com</a></p>
<h3>التغطية</h3>
<p>ست محافظات: العاصمة، حولي، الفروانية، الأحمدي، الجهراء، ومبارك الكبير. السالمية مسار حولي، والفنطاس مسار الأحمدي — ليستا محافظتين مستقلتين.</p>
<h3>ماذا ترسل في الرسالة الأولى</h3>
<ul>
<li>المحافظة والحي ونوع المبنى (فيلا، شقة، محل).</li>
<li>صورة للتسرب أو الوحدة أو الجدار أو الحوش.</li>
<li>إن كان هناك أطفال أو مواعيد إغلاق للمبنى تغيّر ساعة الدخول.</li>
</ul>
<h3>ماذا يحدث بعد الرسالة</h3>
<p>نؤكد إمكانية الوصول، نحدد نافذة المعاينة، ثم نكتب النطاق والسعر بعد الرؤية. الحالات التي تمس الكهرباء أو الغاز أو طفح الصرف تُقدَّم في الترتيب.</p>
<p>الصفحة الإنجليزية: <a href="/kw/en/contact/">Contact the Kuwait desk</a>.</p>
</section>
"""

AR_BLOG = """<section>
<h2>دليل خدمات المنزل في الكويت</h2>
<p>هذه الصفحة فهرس للعائلات، لا مدونة أخبار. كل خدمة لها ست مقالات حسب المحافظة، مكتوبة بعد المعاينة بالدينار الكويتي. لا نضع تقييماً مخترعاً ولا سعراً عاماً هنا.</p>
<p>اختر العائلة ثم ادخل مقال العاصمة أو حولي أو الأحمدي حسب موقعك. السالمية تُقرأ مع حولي، والفنطاس مع الأحمدي.</p>
{families}
<p>للحجز: <a href="/kw/contact-us/">صفحة التواصل</a> أو <a href="https://wa.me/971586634710">واتساب</a>.</p>
</section>
"""


def family_blog_html(cat: dict) -> str:
    order = [
        "leaks",
        "ac",
        "elec",
        "cleaning",
        "pest",
        "maintenance",
        "install",
        "paint",
        "garden",
        "reno",
        "tech",
        "moving",
        "ship",
        "solar",
    ]
    notes = {
        "leaks": "البقعة في السقف ليست دائماً المصدر. المقالات هنا تربط العزل والخزان والحمام قبل التكسير.",
        "ac": "الغسيل والميل والقراءة المكتوبة قبل أي شحن فريون. الملح في السالمية غير غبار الجهراء.",
        "elec": "اللوحة والمحبس يُعزلان قبل الفك. غسالة الصحون والمضخة والسخان ليست «فيشاً إضافياً».",
        "cleaning": "الرخام والخشب والخزان مسارات منفصلة. التنظيف العميق غير مسح السطح.",
        "pest": "المصدر في المجلى أو المنهل أو الحوش. الرش الظاهر بلا إغلاق الشق يعيد النشاط.",
        "maintenance": "عقد أو زيارة: نكتب العطل الظاهر قبل استبدال القطعة.",
        "install": "القياس والقاعدة قبل الخامة: كاميرات، أبواب أمنية، شتر، إيبوكسي، خزانات.",
        "paint": "التحضير تحت إضاءة المكان. لا دهان فوق بلل أو غبار إنشائي.",
        "garden": "الري والتصريف والملوحة. العشب يوم التسليم ليس اختبار أغسطس.",
        "reno": "فحص الفلل والشروخ والبيارة قبل التشطيب الجديد.",
        "tech": "سباك وكهربائي ونجار وفتح أبواب: حدود التخصص تُعلن قبل الأداة.",
        "moving": "الممر والرخام والمصعد جزء من النقل لا بنداً لاحقاً.",
        "ship": "الوثائق والوزن الحجمي قبل موعد التحميل.",
        "solar": "الظل والغبار على السطح قبل عدد الألواح.",
    }
    parts = []
    for fam in order:
        items = []
        for slug, spec in FACTS.items():
            if spec["family"] != fam:
                continue
            rec = (cat.get(slug) or {}).get("kuwait")
            if not rec:
                continue
            items.append(
                f'<li><a href="/kw/{rec["slug"]}/">{rec["title"]}</a></li>'
            )
        if not items:
            continue
        parts.append(
            f"<h3>{FAMILIES[fam]}</h3><p>{notes[fam]}</p>"
            f"<ul>{''.join(items[:8])}</ul>"
        )
    return "\n".join(parts)


def en_services_html(cat: dict) -> str:
    order = list(FAM_EN)
    blocks = [
        "<h2>All trades — one contractor in Kuwait</h2>",
        "<p>English pages summarise the trade. Neighbourhood Arabic articles remain the long guides for the Capital, Hawalli, Farwaniya, Ahmadi, Jahra and Mubarak Al-Kabeer. Quotes are in Kuwaiti dinar after inspection.</p>",
        "<p>Salmiya is dispatched with Hawalli. Fintas is dispatched with Ahmadi. They are not extra governorates.</p>",
    ]
    for fam in order:
        items = []
        for slug, spec in FACTS.items():
            if spec["family"] != fam:
                continue
            rec = (cat.get(slug) or {}).get("kuwait")
            if not rec:
                continue
            items.append(
                f'<li><a href="/kw/{rec["slug"]}/">{spec["noun"]}</a> — Arabic guide for the Capital; other governorates follow the same slug with the city name.</li>'
            )
        if not items:
            continue
        title = {
            "leaks": "Leaks and insulation",
            "ac": "Air conditioning",
            "elec": "Electrics and plumbing",
            "cleaning": "Cleaning",
            "pest": "Pest control",
            "maintenance": "Maintenance",
            "install": "Installation and finishing",
            "paint": "Painting and decor",
            "garden": "Gardens",
            "reno": "Renovation and inspection",
            "tech": "On-call trades",
            "moving": "Moving and storage",
            "ship": "Freight",
            "solar": "Solar",
        }[fam]
        blocks.append(f"<h3>{title}</h3><p>{FAM_EN[fam]}</p><ul>{''.join(items)}</ul>")
    blocks.append(
        f'<p><a href="{WA}">WhatsApp the Kuwait desk</a> · '
        '<a href="mailto:m@rukn-eltatawer.com">m@rukn-eltatawer.com</a></p>'
    )
    return "\n".join(blocks)


def assign_tax(posts) -> dict:
    updated = 0
    skipped = 0
    failed = []
    for p in posts:
        pid = int(p["id"])
        slug = p.get("slug") or ""
        svc, city = parse_slug(slug)
        term = CITY_TERM.get(city)
        fam = (FACTS.get(svc) or {}).get("family") or family_of(svc)
        cat_id = FAM_CAT.get(fam, 3)
        have_cities = p.get("cities") or []
        have_cats = p.get("categories") or []
        body = {}
        if term and not have_cities:
            body["cities"] = [term]
        # new posts landed in cleaning (3) even when the family is not cleaning
        if have_cats == [3] and fam != "cleaning" and not have_cities:
            body["categories"] = [cat_id]
        elif not have_cats:
            body["categories"] = [cat_id]
        if not body:
            skipped += 1
            continue
        try:
            rest(f"/wp/v2/posts/{pid}", method="POST", body=body, timeout=120)
            updated += 1
            if updated % 20 == 0:
                print(f"tax {updated}", flush=True)
        except Exception as e:
            failed.append({"id": pid, "slug": slug, "err": str(e)[:200]})
            time.sleep(0.3)
    return {"updated": updated, "skipped": skipped, "failed": failed[:12], "n_failed": len(failed)}


def iter_all_posts():
    page = 1
    while True:
        rows = rest(f"/wp/v2/posts&per_page=100&page={page}&status=publish")
        if not rows:
            break
        yield from rows
        if len(rows) < 100:
            break
        page += 1


def main():
    print("=== taxonomy ===")
    posts = list(iter_all_posts())
    print("published", len(posts))
    print(assign_tax(posts))
    _, cat = load_catalog()
    print("=== pages ===")
    rest("/wp/v2/pages/1279", method="POST", body={"content": AR_CONTACT})
    print("OK contact 1279")
    rest("/wp/v2/pages/1282", method="POST", body={"content": AR_BLOG.format(families=family_blog_html(cat))})
    print("OK blog 1282")
    rest("/wp/v2/pages/3827", method="POST", body={"content": en_services_html(cat)})
    print("OK en services 3827")
    # city term descriptions stay accurate; salmiya/fintas get a redirect in runtime
    rest(
        "/wp/v2/cities/22",
        method="POST",
        body={
            "description": "السالمية منطقة داخل محافظة حولي وليست محافظة مستقلة. الطلبات تُحوَّل إلى دليل حولي."
        },
    )
    rest(
        "/wp/v2/cities/23",
        method="POST",
        body={
            "description": "الفنطاس منطقة داخل محافظة الأحمدي وليست محافظة مستقلة. الطلبات تُحوَّل إلى دليل الأحمدي."
        },
    )
    print("OK city terms salmiya/fintas")
    print("done")


if __name__ == "__main__":
    raise SystemExit(main() or 0)
