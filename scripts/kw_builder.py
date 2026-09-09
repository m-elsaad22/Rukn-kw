"""Build unique Kayan-ready HTML + metabox payloads for one Kuwait service article."""
from __future__ import annotations

import hashlib
import re
from html import escape

from kw_cities import CITIES, parse_slug
from kw_family_copy import family_sections
from kw_service_facts import FACTS, family_of
from kw_unique_bank import depth_blocks, inspection_list, city_essays

CITY_OUTLINE = {
    "kuwait": 0,
    "hawalli": 1,
    "farwaniya": 2,
    "mubarak-al-kabeer": 3,
    "al-ahmadi": 4,
    "al-jahra": 5,
}

PHONE = "+971586634710"
WA = "971586634710"
TEL = "tel:+971586634710"
WA_URL = "https://wa.me/971586634710"
COMPANY = "ركن التطور"
HOME = "https://rukn-eltatawer.com/kw/"

ARTICLE_CSS = """
<style>
.rukn-wrap{color:#0A1A33;line-height:1.85;font-size:17px}
.rukn-hero{background:linear-gradient(135deg,#0A1F4E 0%,#1269eb 70%,#1FB5A3 140%);color:#fff;border-radius:18px;padding:22px 18px;margin:16px 0 22px}
.rukn-hero .hero-label{display:inline-block;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25);border-radius:999px;padding:4px 12px;font-size:13px;margin:0 0 10px}
.rukn-hero p{color:#f4f7ff;margin:0 0 10px}
.rukn-hero-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
.rukn-btn{display:inline-flex;align-items:center;gap:8px;background:#fff;color:#0A1F4E;text-decoration:none;border-radius:12px;padding:11px 16px;font-weight:700;min-height:44px}
.rukn-btn-wa{background:#1FB5A3;color:#fff}
.rukn-grid{display:grid;grid-template-columns:1fr;gap:12px;margin:14px 0}
@media(min-width:720px){.rukn-grid.cols-3{grid-template-columns:1fr 1fr 1fr}.rukn-grid.cols-2{grid-template-columns:1fr 1fr}}
.rukn-card,.rukn-step{background:#fff;border:1px solid #d7e3f7;border-radius:16px;padding:16px;box-shadow:0 8px 24px rgba(10,31,78,.06)}
.rukn-card>i,.rukn-step .num{color:#1269eb}
.rukn-card h3,.rukn-step h3{margin:8px 0 6px;color:#0A1F4E;font-size:18px}
.rukn-step{display:flex;gap:12px;align-items:flex-start}
.rukn-step .num{min-width:42px;height:42px;border-radius:12px;background:#e8f1ff;display:flex;align-items:center;justify-content:center;font-weight:800}
.responsive-table{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:12px 0 20px;border:1px solid #d7e3f7;border-radius:14px}
.responsive-table table{width:100%;border-collapse:collapse;min-width:280px}
.responsive-table th{background:#0A1F4E;color:#fff;text-align:right;padding:10px}
.responsive-table td{padding:10px;border-top:1px solid #e6eef8}
.responsive-table tr:nth-child(even) td{background:#f6f9ff}
blockquote.warning-box,blockquote.expert-tip{border-radius:14px;padding:14px 16px;margin:14px 0}
blockquote.warning-box{background:#fff6e8;border:1px solid #f0d3a0}
blockquote.expert-tip{background:#eefaf7;border:1px solid #b7e6de}
.rukn-cta{background:#0A1F4E;color:#fff;border-radius:18px;padding:20px;margin:22px 0}
.rukn-cta h2{color:#fff;margin:8px 0;font-size:22px}
.rukn-cta p{color:#dbe7ff}
.author-box{background:#f4f8ff;border:1px solid #d7e3f7;border-radius:12px;padding:10px 14px;margin:0 0 16px;font-size:14px}
</style>
"""


def _seed(*parts) -> int:
    h = hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def _pick(seed: int, items, offset=0):
    return items[(seed + offset) % len(items)]


def _areas(city, seed, n=4):
    areas = list(city["areas"])
    start = seed % len(areas)
    out = []
    for i in range(n):
        out.append(areas[(start + i * 2) % len(areas)])
    return out


def _is_tech_title(title: str) -> bool:
    return not title.startswith("شركة")


def related_links(service_slug: str, city_key: str, catalog: dict, seed: int):
    links = []
    same_service = catalog.get(service_slug, {})
    other_cities = [k for k in same_service if k != city_key]
    if other_cities:
        k = other_cities[seed % len(other_cities)]
        p = same_service[k]
        links.append((p["title"], HOME + p["slug"] + "/"))
    fam = family_of(service_slug)
    siblings = []
    for s, cities in catalog.items():
        if s == service_slug:
            continue
        if family_of(s) != fam:
            continue
        if city_key in cities:
            siblings.append(cities[city_key])
    for p in siblings[:2]:
        links.append((p["title"], HOME + p["slug"] + "/"))
    links.append(("خدمات ركن التطور في الكويت", HOME))
    seen = set()
    uniq = []
    for t, u in links:
        if u in seen:
            continue
        seen.add(u)
        uniq.append((t, u))
    return uniq[:4]


def build(post: dict, catalog: dict) -> dict:
    slug = post["post_name"]
    title = post["post_title"]
    service_slug, city_key = parse_slug(slug)
    city = CITIES[city_key]
    spec = FACTS.get(service_slug)
    if not spec:
        spec = {
            "family": family_of(service_slug),
            "noun": re.sub(r"^(شركة|فني|سباك|كهربائي)\s*", "", title).strip(),
            "problem": "الحالة تختلف حسب الموقع والاستخدام",
            "audience": "أصحاب المنازل والمنشآت في الكويت",
            "tools": ["فحص موقع", "أدوات مناسبة", "تقرير واضح"],
            "signs": ["تكرار المشكلة", "ضعف النتيجة المنزلية", "تأثر الاستخدام اليومي", "رائحة أو أثر ظاهر", "تأخر المعالجة"],
            "mistakes": ["حل مؤقت يخفي المصدر", "مواد غير مناسبة للخامة"],
            "types": ["معاينة", "تنفيذ", "متابعة"],
            "icon": "fa-tools",
        }
    seed = _seed(post["ID"], slug, service_slug, city_key)
    outline = CITY_OUTLINE.get(city_key, seed % 6)
    areas = _areas(city, seed, 4)
    areas_txt = "، ".join(areas[:4])
    noun = spec["noun"]
    kw = title
    icon = spec.get("icon") or "fa-tools"
    tech = _is_tech_title(title)
    who = "الفني المختص" if tech else "فريق التنفيذ"
    company_line = f"{who} لدى {COMPANY}"
    fam = spec.get("family") or family_of(service_slug)

    intros = [
        f"{spec['problem']} هذا ما يدفع أغلب طلبات {noun} {city['in']}. {city['buildings']}.",
        f"الاحتياج إلى {noun} {city['in']} يظهر من الاستخدام اليومي: {spec['problem']}",
        f"{city['climate']} لذلك مسار {noun} هنا لا يُنسخ من محافظة أخرى حتى لو تشابه العنوان.",
        f"{spec['audience']} يطلبون {noun} عندما تتكرر علامة واضحة. {spec['problem']}",
        f"هل تحتاج {noun} الآن أم يكفي ترتيب معاينة؟ {spec['problem']} يظهر {city['in']} بشكل مختلف حسب المبنى.",
        f"{city['access']} هذا يغيّر موعد {noun} وتجهيز المعدات أكثر مما يبدو من عنوان الصفحة.",
    ]
    intro = intros[outline]
    direct = (
        f"{kw} تعني تنفيذ {noun} داخل {city['label']} بعد معاينة الموقع وكتابة النطاق قبل البدء. "
        f"الخدمة تناسب {spec['audience']}. لا يُسعَّر العمل عبر وصف هاتفي فقط لأن {city['water']}"
    )

    h2_what = [
        f"ما الذي يشمله {noun} {city['in']}؟",
        f"كيف نفهم طلب {noun} داخل {city['name']}؟",
        f"نطاق {noun} الفعلي لا العنوان التسويقي",
        f"هل {kw} تناسب حالتك الآن؟",
        f"ماذا يعني طلب {noun} في {city['label']}؟",
        f"متى يكون {noun} حلاً مناسباً؟",
    ][outline]

    what_p = (
        f"{noun} ليس قائمة مهام منسوخة. {spec['problem']} "
        f"في {city['label']} نبدأ من نوع المبنى: {city['buildings']}. "
        f"المناطق التي نرتّب الزيارة إليها حسب الاتفاق تشمل {areas_txt}."
    )

    signs_h = [
        f"علامات تحتاج معها {noun} في {city['name']}",
        f"متى لا يكفي الحل المنزلي لـ{noun}؟",
        f"أعراض تتكرر في {city['label']}",
        f"ما الذي نسأل عنه قبل زيارة {noun}؟",
        f"مؤشرات تؤكد أن {noun} أصبح ضرورياً",
        f"كيف تفرّق بين عرض بسيط ومصدر مستمر؟",
    ][outline]

    extra_signs = [
        f"تأثر الاستخدام اليومي في {areas[0]}",
        f"عودة المشكلة بعد تجربة منزلية في {areas[1]}",
        f"ظهور أثر في أكثر من نقطة داخل الوحدة",
        f"تغير واضح بعد الحر أو الرطوبة في {city['name']}",
    ]
    sign_items = (spec["signs"][:] + extra_signs)[:7]

    process = [
        (f"توضيح الحالة في {city['name']}", f"نستلم الوصف أو صورة لتحديد إن كانت الزيارة في {areas[0]} كافية أم تحتاج تجهيزاً."),
        ("معاينة مكتوبة", f"نوثق الخامة والوصول و{city['water']} قبل اختيار الأداة."),
        ("تحديد النطاق", f"نكتب ما سيُنفَّذ وما لن يُنفَّذ حتى لا يتوسع العمل أثناء الزيارة في {city['label']}."),
        ("التنفيذ حسب الخامة", f"الأدوات المستخدمة تشمل: {'، '.join(spec['tools'][:4]) }."),
        ("مراجعة التسليم", f"تُغلق الزيارة بعد معاينتك للنتيجة في {areas[1]}."),
    ]
    if outline in (1, 4):
        process[0], process[1] = process[1], process[0]
    if outline in (2, 5):
        process.append(("متابعة إن لزم", f"بعض حالات {noun} تحتاج زيارة تحقق بعد استقرار الخامة أو الطقس في {city['name']}."))

    cost_rows = [
        ("نوع الخدمة ونطاق الغرف أو الوحدات", f"يختلف {noun} بين نقطة واحدة ومسار كامل داخل {city['label']}."),
        ("حالة الموقع الآن", spec["problem"]),
        ("الخامات والأدوات", "، ".join(spec["tools"][:3])),
        ("سهولة الوصول والوقوف", city["access"]),
        ("الوقت داخل اليوم", "بعض الأعمال تُفضَّل خارج الذروة أو بعد إغلاق المحل."),
        ("عمر التشطيب أو الجهاز", f"في {city['name']} يظهر أثر العمر على التشخيص أكثر من وصف الهاتف."),
    ]
    if outline % 2:
        cost_rows.append(("الجمع مع خدمة مرتبطة", "إن ظهر أثناء المعاينة احتياج مرتبط يُعرض منفصلاً لا يُضاف صامتاً."))

    mistakes = spec["mistakes"] + [
        f"تأجيل العمل رغم أن {city['climate']}",
        "المقارنة بالسعر الهاتفي دون نطاق مكتوب",
        f"إغلاق المصدر الظاهر في {areas[0]} دون فحص باقي المسار",
    ]

    types_h = [
        f"مسارات شائعة لـ{noun}",
        f"أنواع {noun} التي نناقشها في المعاينة",
        f"لا ننفّذ كل نوع في كل زيارة",
        f"كيف نختار مسار {noun}؟",
        f"جدول المسارات بدون أسعار مخترعة",
        f"ما الذي يُطرح حسب حالة {city['name']}؟",
    ][outline]

    compare_rows = [
        ("التشخيص", f"ربط {spec['problem']} بالموقع في {city['name']}", "حل جاهز من حالة أخرى"),
        ("التكلفة", "عوامل مكتوبة بعد الزيارة بالدينار الكويتي عند الاتفاق", "رقم عبر الهاتف قبل الرؤية"),
        ("المناخ والمبنى", city["climate"], "خطة منسوخة من مدينة أخرى"),
        ("الوضوح", "نطاق قبل التنفيذ", "اتفاق شفهي يتوسع"),
        ("التسليم", f"مراجعة نقطة ظاهرة في {areas[0]}", "انصراف بعد «شكله تمام»"),
    ]

    tips = [
        f"صوّر النقطة من زاويتين قبل الزيارة في {areas[0]}؛ ذلك يختصر وقت المعاينة.",
        f"اذكر عمر التمديدات أو آخر صيانة لـ{noun} إن وُجدت.",
        f"في {city['label']} أخبرنا عن موقف السيارات أو الحارس قبل الوصول.",
        f"لا تخلط مواد تنظيف أو كيماويات قبل وصول {who}.",
        city["water"],
        f"إن كانت الحالة قرب الكهرباء أو الغاز نؤمّن أولاً ثم نحدد باقي {noun}.",
    ]
    tip = _pick(seed, tips)
    warn = _pick(
        seed,
        [
            f"التجارب العشوائية قد تخفي مصدر {noun} وتوسّع الضرر خصوصاً مع الرطوبة أو الكهرباء.",
            f"لا تستخدم ضغط ماء عالياً أو مواد كاوية قبل معرفة خامة السطح في {city['name']}.",
            f"العمل على ارتفاع أو غاز أو لوحة كهرباء ليس تجربة منزلية.",
            f"تأجيل {noun} مع {city['climate']} يجعل الإصلاح أوسع لا أرخص.",
        ],
        outline,
    )

    faqs = _faqs(kw, noun, city, spec, areas, tech, seed)
    features = _features(noun, city, spec, seed)
    steps_meta = [{"title": a, "content": b} for a, b in process]
    price_items = [{"title": a, "value": b} for a, b in cost_rows]
    related = related_links(service_slug, city_key, catalog, seed)

    rel_html = ""
    if related:
        a_t, a_u = related[0]
        rel_html = f'<p>يمكنك أيضاً الاطلاع على <a href="{a_u}">{escape(a_t)}</a> إذا كان الاحتياج مرتبطاً بنفس الخدمة في محافظة أخرى أو بمسار قريب.</p>'

    sections = _compose_sections(
        outline=outline,
        title=title,
        kw=kw,
        noun=noun,
        city=city,
        city_key=city_key,
        intro=intro,
        direct=direct,
        h2_what=h2_what,
        what_p=what_p,
        signs_h=signs_h,
        sign_items=sign_items,
        process=process,
        types_h=types_h,
        spec=spec,
        fam=fam,
        cost_rows=cost_rows,
        compare_rows=compare_rows,
        mistakes=mistakes,
        tip=tip,
        warn=warn,
        icon=icon,
        areas=areas,
        areas_txt=areas_txt,
        company_line=company_line,
        rel_html=rel_html,
        related=related,
        tech=tech,
        seed=seed,
        who=who,
    )

    html = "\n".join(sections)
    excerpt = (
        f"{noun} {city['in']}: {spec['problem']} "
        f"معاينة في {areas[0]} ثم نطاق مكتوب داخل {city['label']}."
    )[:180]

    rm_title = f"{kw} 2026 | {COMPANY}"
    if len(rm_title) > 60:
        rm_title = f"{kw} | {COMPANY}"
    rm_desc = (
        f"{spec['problem']} {city['in']}. "
        f"نحدد النطاق بعد المعاينة في {city['label']} دون أسعار مخترعة عبر الهاتف."
    )[:158]

    tags = [
        noun,
        city["name"],
        COMPANY,
        fam if isinstance(fam, str) else "خدمات منزلية",
        areas[0],
        spec["types"][0] if spec.get("types") else "معاينة",
        "الكويت",
    ]

    meta = {
        "phone_number": PHONE,
        "whatsapp_number": WA,
        "last_update": "09-09-2026",
        "yourcolor__faqs": faqs,
        "post__call_section__data": {
            "call_section_title": f"هل تحتاج إلى {noun} {city['in']}؟",
            "call_section_content": f"صف الحالة أو أرسل صورة، ونحدد إن كانت الزيارة في {city['name']} كافية.",
            "call_section_phone": PHONE,
            "call_section_whatsapp": WA,
        },
        "post__features__data": {
            "features__title": f"ماذا يميز تنفيذ {noun} مع {COMPANY}؟",
            "features__content": f"تفاصيل تناسب {city['label']} لا قائمة عامة منسوخة.",
            "yourcolor__post_features": features,
        },
        "post__work_steps__data": {
            "work_steps__title": f"خطوات {noun} {city['in']}",
            "work_steps__content": f"الترتيب يتغير حسب المبنى في {city['name']}.",
            "work_steps_items": steps_meta,
        },
        "post__price_list__data": {
            "price_list__title": f"ما الذي يحرّك تكلفة {noun}؟",
            "price_list__content": "لا توجد قائمة أسعار ثابتة هنا لأن الحالة تتغير. الجدول يوضح عوامل المعاينة.",
            "price_list__table_title1": "العامل",
            "price_list__table_title2": "كيف يظهر في {0}".format(city["name"]),
            "price_list__items": price_items,
        },
        "post__services__data": {
            "services__title": "خدمات مرتبطة تُطلب أثناء المعاينة",
            "services__content": f"لا تُضاف تلقائياً إلى {noun}.",
            "post_services_items": [
                {"title": t, "content": "تُعرض إن ظهرت حاجة أثناء الفحص."}
                for t, _u in related[:3]
            ],
        },
        "post__card__data": {
            "post_card_title": f"طلب {noun} {city['in']}",
            "post_card_content": spec["problem"],
        },
        "post__service_request__data": {
            "orderservices": f"اطلب {noun}",
            "contentservices": f"معاينة في {city['label']} ثم نطاق مكتوب.",
        },
        "YourColor_Service": {
            "description": excerpt,
            "addressLocality": city["name"],
            "addressCountry": "KW",
            "addressRegion": "الكويت",
            "telephone": PHONE,
            "areaServed": city["label"],
            "streetAddress": "الكويت",
        },
        "YourColor_Article": {
            "headline": title,
            "description": excerpt,
            "articleBody": spec["problem"],
        },
    }

    return {
        "html": html,
        "excerpt": excerpt,
        "tags": tags,
        "rank_math_title": rm_title,
        "rank_math_description": rm_desc,
        "rank_math_focus_keyword": kw,
        "meta": meta,
        "word_count_hint": len(re.findall(r"\S+", re.sub(r"<[^>]+>", " ", html))),
        "service_slug": service_slug,
        "city_key": city_key,
        "faqs": faqs,
    }


def _features(noun, city, spec, seed):
    icons = [
        spec.get("icon") or "fa-tools",
        "fa-clipboard-check",
        "fa-map-location-dot",
        "fa-file-invoice",
        "fa-user-check",
        "fa-phone",
    ]
    titles = [
        ("معاينة قبل التنفيذ", f"نربط {spec['problem']} بواقع المبنى في {city['name']}."),
        ("أدوات مناسبة للخامة", "، ".join(spec["tools"][:3])),
        ("تغطية محلية", city["buildings"]),
        ("نطاق مكتوب", "تعرف ما سيُنفَّذ قبل أن يبدأ العمل."),
        ("تواصل مباشر", "اتصال أو واتساب بدون وسيط إعلانات."),
        ("مناخ الكويت", city["climate"]),
    ]
    start = seed % 3
    items = []
    for i in range(4):
        t, c = titles[(start + i) % len(titles)]
        items.append({"title": t, "content": c, "icon": f'<i class="fa-solid {icons[i]}"></i>'})
    return items


def _faqs(kw, noun, city, spec, areas, tech, seed):
    who = "الفني" if tech else "فريق الخدمة"
    s = spec["signs"]
    m = spec["mistakes"]
    base = [
        {"question": f"ما هي {kw}؟", "answer": f"هي تنفيذ {noun} داخل {city['label']} بعد معاينة توضح المصدر والنطاق. {spec['problem']}"},
        {"question": f"هل تغطون {areas[0]} و{areas[1]}؟", "answer": f"نعم ضمن {city['label']}. نؤكد إمكانية الوصول عند حجز الموعد لأن {city['access']}"},
        {"question": f"كيف تتحدد تكلفة {noun}؟", "answer": "بعد المعاينة حسب المساحة والحالة والخامات. لا نثبت رقماً عاماً لكل البيوت بالدينار الكويتي قبل الرؤية."},
        {"question": "هل توجد أسعار ثابتة في الصفحة؟", "answer": "لا. أي رقم قبل الفحص مضلل لأن الحالات تختلف داخل المحافظة الواحدة."},
        {"question": f"كم تستغرق زيارة {noun}؟", "answer": f"تُقدَّر بعد رؤية الموقع في {city['name']}. الزيارة القصيرة تختلف عن المسار الكامل."},
        {"question": "هل يمكن التنفيذ في نفس اليوم؟", "answer": "يعتمد على حجم العمل وجدول الفريق. الحالات التي تمس السلامة تُقدَّم في الترتيب."},
        {"question": f"ما الأدوات المستخدمة في {noun}؟", "answer": "، ".join(spec["tools"]) + "."},
        {"question": f"ما الأخطاء الشائعة قبل وصول {who}؟", "answer": m[0] + " " + m[1]},
        {"question": "هل المعاينة قبل التسعير؟", "answer": f"نعم. {city['water']}"},
        {"question": "كيف أحجز؟", "answer": f"عبر الاتصال أو واتساب. اذكر {noun} ومنطقتك مثل {areas[0]} وصورة للنقطة إن أمكن."},
        {"question": f"هل يناسب {noun} {spec['audience']}؟", "answer": f"هذا هو الجمهور الأساسي. نوضح إن كانت الحالة تحتاج مساراً آخر أثناء المعاينة في {city['name']}."},
        {"question": f"ما الذي يميز العمل في {city['label']}؟", "answer": city["climate"] + " " + city["buildings"]},
        {"question": f"هل {s[0]} يكفي لطلب الزيارة؟", "answer": f"إذا تكرر أو اجتمع مع {s[1]} فغالباً نعم. التجربة المنزلية المتكررة تضيع وقتاً أكثر مما توفّر."},
        {"question": f"أين يظهر {noun} أكثر داخل البيت؟", "answer": f"حسب الخدمة: قد يبدأ من {s[2]} ثم يمتد. المعاينة في {areas[2] if len(areas)>2 else city['name']} تربط العرض بالمصدر."},
        {"question": f"هل تعملون في {areas[3] if len(areas)>3 else city['name']}؟", "answer": f"نعم ضمن تغطية {city['label']} بعد تأكيد الموعد والوصول."},
        {"question": "هل تستخدمون ضمانات أو تقييمات عامة في الصفحة؟", "answer": "لا نضع تقييماً مخترعاً ولا نسبة نجاح عامة. نلتزم بما نعاينه ونكتبه."},
    ]
    n = 9 + (seed % 4)
    start = seed % len(base)
    out = []
    seen = set()
    for i in range(len(base)):
        f = base[(start + i * 3) % len(base)]
        if f["question"] in seen:
            continue
        seen.add(f["question"])
        out.append(f)
        if len(out) >= n:
            break
    return out[:12]


def _city_scenario(noun, city, city_key, spec, areas, outline):
    stories = {
        "kuwait": (
            f"يوم عمل {noun} بين الوسط والأبراج",
            f"في {areas[0]} قد يكون المدخل التجاري أضيق من بيت في {areas[1]}. الأبراج تحتاج تنسيق المصعد، والبيوت القديمة قد تخفي تمديدات تحت طبقات تشطيب.",
            f"الرطوبة الساحلية تجعل الزجاج والمكيف الخارجي جزءاً من قراءة الموقع حتى لو كان طلبك {noun} لغرفة داخلية. {spec['problem']}",
            f"الضغط بين الأدوار يغيّر تشخيص الماء والكهرباء. لذلك لا ننسخ زمن التنفيذ من ضاحية هادئة إلى الشرق في ساعة الذروة.",
        ),
        "hawalli": (
            f"{noun} في كثافة السالمية وحولي",
            f"الشقة في {areas[0]} تستقبل غبار الممر أسرع من فيلا في {areas[1]}. الواجهة البحرية تسرّع تآكل الألمنيوم إن كانت الخدمة تمسه.",
            f"الزحام ظهراً يجعل نافذة الدخول جزءاً من الاتفاق لا تفصيلاً ثانوياً. {spec['problem']}",
            f"مضخات العمائر شائعة؛ أي ضعف فيها يظهر على السباكة والسخان حتى لو كان الطلب {noun} لغرفة واحدة.",
        ),
        "farwaniya": (
            f"{noun} بين العمائر والمحلات في الفروانية",
            f"الحركة اليومية في {areas[0]} تعيد الغبار أسرع من بيت أهدأ في {areas[1]}. المحل الأرضي قد يحتاج عملاً بعد الإغلاق.",
            f"شبكات أقدم في بعض البيوت تجعل التسرب أو ضعف الضغط يظهر متأخراً. {spec['problem']}",
            f"الغبار الداخلي أعلى من الساحل؛ لذلك تجفيف الخامات وحماية الدهان جزء من قراءة الموقع.",
        ),
        "mubarak-al-kabeer": (
            f"{noun} في فلل الضواحي بمبارك الكبير",
            f"الأحواش والملاحق في {areas[0]} تضيف نقاط فحص لا تظهر في شقة. السطح والخزان غالباً أقرب للعمل من وسط المدينة.",
            f"الوقوف أسهل غالباً، لكن الحوش الترابي والغبار يصلان للمكيفات بسرعة. {spec['problem']}",
            f"في {areas[1]} قد نجمع الملحق مع البيت في نفس المعاينة إذا كان المصدر مشتركاً.",
        ),
        "al-ahmadi": (
            f"{noun} بين الساحل والمساحات في الأحمدي",
            f"الواجهة في {areas[0]} قد تكون أملح من بيت داخلي في {areas[1]}. المسافات أطول؛ نؤكد نافذة اليوم لا وعداً فضفاضاً.",
            f"الأسطح الكبيرة والخزانات جزء متكرر من الفحص حتى لو بدأ الطلب من غرفة. {spec['problem']}",
            f"المضخات المنزلية شائعة، والضغط صيفاً يغيّر شكل العطل في الأدوار العلوية.",
        ),
        "al-jahra": (
            f"{noun} مع الغبار والمساحات في الجهراء",
            f"الغبار الصحراوي في {areas[0]} يلتصق بالدكت والخزان والستائر أكثر من الساحل. المسافة من العاصمة تجعل تأكيد صباح التنفيذ أوضح.",
            f"الأحواش والملاحق نقاط إخفاء للحشرات أو للرمل حول الفتحات. {spec['problem']}",
            f"الخزان السطحي وفتحته جزء ثابت من المعاينة إذا كانت الخدمة تمس الماء أو السطح في {areas[1]}.",
        ),
    }
    h, p1, p2, p3 = stories.get(city_key, stories["kuwait"])
    if outline % 2:
        p1, p2 = p2, p1
    return [f"<h2>{escape(h)}</h2><p>{escape(p1)}</p><p>{escape(p2)}</p><p>{escape(p3)}</p>"]


def _long_unique_blocks(noun, city, spec, outline, areas_txt, company_line, seed):
    parts = [x.strip() for x in areas_txt.split("، ") if x.strip()]
    while len(parts) < 3:
        parts.append(city["name"])
    a0, a1, a2 = parts[0], parts[1], parts[2]
    tools = "، ".join(spec["tools"])
    types = "، ".join(spec["types"])
    audience = spec["audience"]
    headings = [
        f"الأدوات والخامات المستخدمة في {noun}",
        f"تأثير مناخ {city['name']} على {noun}",
        f"ما الذي نجهّزه قبل زيارة {noun}؟",
        f"حدود الحل المنزلي أمام {noun}",
        f"السلامة أثناء {noun}",
        f"بعد التسليم: كيف تحافظ على نتيجة {noun}؟",
        f"لمن تناسب الخدمة ولمن لا تناسب؟",
        f"كيف نقرأ المبنى قبل بدء {noun}؟",
    ]
    bodies = [
        f"<p>تنفيذ {escape(noun)} يعتمد على ملاءمة الأداة للخامة لا على كثرة العدد. نستخدم: {escape(tools)}. في {escape(city['name'])} قد نغيّر الترتيب لأن {escape(city['climate'])}</p><p>أي مادة ذات رائحة أو تحتاج تهوية تُذكر قبل الدخول خصوصاً في المجالس المغلقة. {escape(company_line)} لا يخلط مواداً لم تُختبر على السطح الظاهر.</p>",
        f"<p>{escape(city['climate'])} هذا يغيّر جفاف الدهان والعزل وثبات التنظيف ومدة بقاء المعالجة حسب نوع الخدمة. العمل في {escape(a0)} قد يُجدول في ساعة ألطف من الظهيرة إذا كانت الحرارة تؤثر على النتيجة.</p><p>{escape(city['buildings'])} لذلك لا ننسخ زمن التنفيذ من محافظة أخرى حتى لو تشابه عنوان الخدمة.</p>",
        f"<p>قبل الوصول نسأل عن موقف السيارات، ووجود حارس، ومصدر المياه والكهرباء. {escape(city['access'])} إن كان العمل في {escape(a1)} نؤكد نافذة الدخول حتى لا يضيع وقت المعاينة على الانتظار.</p><p>إذا كانت الحالة تمس الغاز أو اللوحة أو ارتفاع السطح نؤمّن أولاً. {escape(spec['problem'])}</p>",
        f"<p>الحل المنزلي يناسب الصيانة الشكلية القصيرة. عندما تتكرر {escape(spec['signs'][0])} أو {escape(spec['signs'][1])} يصبح التجريب خسارة وقت. الخطأ الشائع: {escape(spec['mistakes'][0])}.</p><p>المسار المهني يفصل العرض عن المصدر ثم يكتب النطاق. هذا أوضح لـ{escape(audience)} من وعد هاتفي.</p>",
        f"<p>نمنع دخول الأطفال والحيوانات إلى منطقة العمل إن وُجدت مواد أو كهرباء مكشوفة. في الحوش أو السطح نراعي الحرارة والغبار. أي تصريف ماء يُوجَّه بعيداً عن الكهرباء.</p><p>إذا ظهرت حاجة لإغلاق المحبس أو القاطع نخبرك قبل التنفيذ لا بعده.</p>",
        f"<p>بعد التسليم نشرح ما الذي تراقبه في الأيام التالية حسب نوع {escape(noun)}: عودة الرطوبة، ضعف التبريد، عودة الحشرة، أو تقشر الدهان. المتابعة موعد يُذكر إن كانت الحالة تستدعيه وليست شعاراً عاماً.</p><p>في {escape(a2)} نذكّر بتأثير الغبار أو الرطوبة الساحلية على عمر النتيجة إن كان ذلك مرتبطاً بالخدمة.</p>",
        f"<p>الخدمة موجّهة أساساً إلى {escape(audience)}. إن كانت الحالة خارج نطاق {escape(noun)} نوضح ذلك بدل توسيع العمل صامتاً. المسارات المحتملة داخل المعاينة: {escape(types)}.</p><p>لا ننفّذ كل مسار في كل زيارة. الجدول يوضح متى يُطرح كل مسار داخل {escape(city['label'])}.</p>",
        f"<p>ننظر إلى عمر التشطيب، وعدد المستخدمين، وموقع العطل الظاهر، وسهولة فتح الأسقف أو الخزائن. {escape(city['water'])}</p><p>هذه القراءة تمنع اختيار مادة تخدش الرخام أو عزل يخفي رطوبة نشطة أو تمديداً يزيد الحمل على لوحة ضعيفة.</p>",
    ]
    picks = list(range(8))
    paras = [f"<h2>{escape(headings[i])}</h2>{bodies[i]}" for i in picks]
    extra_table = (
        '<div class="responsive-table"><table><thead><tr><th>البند</th><th>ماذا نفحص في الموقع</th></tr></thead><tbody>'
        f"<tr><td>المناخ المحلي</td><td>{escape(city['climate'])}</td></tr>"
        f"<tr><td>المبنى</td><td>{escape(city['buildings'])}</td></tr>"
        f"<tr><td>الوصول</td><td>{escape(city['access'])}</td></tr>"
        f"<tr><td>الخامة أو الأداة</td><td>{escape(tools)}</td></tr>"
        f"<tr><td>الجمهور</td><td>{escape(audience)}</td></tr>"
        "</tbody></table></div>"
    )
    extra_p = (
        f"<p>زاوية إضافية من رقم الصفحة ({seed % 97}): نربط {escape(spec['signs'][2])} بما نراه في {escape(a0)} "
        f"ولا نعمم نتيجة بيت في {escape(a1)} على وحدة مختلفة التشطيب. هذا ما يجعل صفحة {escape(noun)} "
        f"في {escape(city['name'])} مختلفة عن صفحة الخدمة نفسها في محافظة أخرى.</p>"
    )
    return paras + [extra_table, extra_p]


def _compose_sections(**k):
    city = k["city"]
    noun = k["noun"]
    kw = k["kw"]
    icon = k["icon"]
    sections = [ARTICLE_CSS, '<div class="rukn-wrap">']
    sections.append(
        '<p class="author-box">'
        '<i class="fa-solid fa-pen"></i> <strong>كتب هذا المقال:</strong> فريق المحتوى الفني في ركن التطور &nbsp;|&nbsp; '
        '<i class="fa-solid fa-calendar"></i> <strong>آخر تحديث:</strong> سبتمبر 2026 &nbsp;|&nbsp; '
        '<i class="fa-solid fa-check"></i> <strong>مراجعة:</strong> فريق العمليات في ركن التطور'
        "</p>"
    )
    sections.append(f"<p>{escape(k['intro'])}</p>")
    sections.append(f"<p>{escape(k['direct'])}</p>")
    sections.append(
        '<div class="rukn-hero">'
        f'<p class="hero-label">{escape(city["label"])} · {escape(noun)}</p>'
        f"<p>{escape(k['what_p'][:280])}</p>"
        '<p class="rukn-hero-actions">'
        f'<a class="rukn-btn" href="{TEL}"><i class="fa-solid fa-phone"></i> اتصل الآن</a>'
        f'<a class="rukn-btn rukn-btn-wa" href="{WA_URL}"><i class="fa-brands fa-whatsapp"></i> واتساب</a>'
        "</p></div>"
    )
    sections.append("[post_call]")

    block_what = [
        f"<h2>{escape(k['h2_what'])}</h2>",
        f"<p>{escape(k['what_p'])}</p>",
        f"<p>{escape(city['buildings'])} {escape(city['climate'])}</p>",
        f"<p>{escape(kw)} تُفهم داخل {escape(city['label'])} من خلال المعاينة لا من عنوان المقال وحده. "
        f"{escape(k['who'])} يكتب النطاق بعد رؤية الخامة والوصول.</p>",
    ]
    block_signs = [
        f"<h2>{escape(k['signs_h'])}</h2>",
        "<p>إذا تكرر أحد هذه الأمور فغالباً تحتاج زيارة لا تجربة جديدة:</p>",
        "<ul>" + "".join(f"<li>{escape(s)}</li>" for s in k["sign_items"]) + "</ul>",
        f"<p>اجتماع علامتين معاً أوضح من علامة واحدة عابرة. في {escape(k['areas'][0])} نسأل أيضاً عن آخر محاولة منزلية حتى لا نكررها.</p>",
    ]
    cards = '<div class="rukn-grid cols-3">'
    for t in k["spec"]["types"][:3]:
        cards += (
            '<div class="rukn-card">'
            f'<i class="fa-solid {icon}"></i>'
            f"<h3>{escape(t)}</h3>"
            f"<p>يُطرح هذا المسار إذا أشارت المعاينة إليه في {escape(city['name'])}، لا كبند ثابت في كل عقد.</p>"
            "</div>"
        )
    cards += "</div>"
    block_types = [f"<h2>{escape(k['types_h'])}</h2>", cards, "[post_features]"]
    steps_html = ""
    for i, (st, sp) in enumerate(k["process"], 1):
        steps_html += (
            '<div class="rukn-step">'
            f'<div class="num">{i:02d}</div>'
            f"<div><h3>{escape(st)}</h3><p>{escape(sp)}</p></div>"
            "</div>"
        )
    block_steps = [
        f"<h2>كيف يتم {escape(noun)} في {escape(city['name'])}؟</h2>",
        f"<p>{escape(k['company_line'])} يرتّب العمل حسب الوصول والخامة لا حسب قالب جاهز.</p>",
        steps_html,
        "[post_steps]",
    ]
    table = (
        '<div class="responsive-table"><table><thead><tr>'
        "<th>العامل</th><th>كيف يظهر في الموقع</th></tr></thead><tbody>"
        + "".join(f"<tr><td>{escape(a)}</td><td>{escape(b)}</td></tr>" for a, b in k["cost_rows"])
        + "</tbody></table></div>"
    )
    block_cost = [
        f"<h2>كم تكلفة {escape(noun)} {escape(city['in'])}؟</h2>",
        "<p>لا نضع أسعاراً ثابتة هنا ولا أرقاماً بالدينار الكويتي قبل المعاينة. الجدول يوضح ما الذي تتغير معه التكلفة بعد الرؤية.</p>",
        table,
        "[post_prices]",
    ]
    cmp = (
        '<div class="responsive-table"><table><thead><tr>'
        "<th>المعيار</th><th>بعد معاينة منظمة</th><th>المسار المتعجل</th></tr></thead><tbody>"
        + "".join(
            f"<tr><td>{escape(a)}</td><td>{escape(b)}</td><td>{escape(c)}</td></tr>"
            for a, b, c in k["compare_rows"]
        )
        + "</tbody></table></div>"
    )
    block_cmp = [
        f"<h2>ما الذي يتغير عندما تُفحص حالة {escape(noun)}؟</h2>",
        cmp,
        f'<blockquote class="expert-tip"><i class="fa-solid fa-lightbulb"></i> <strong>نصيحة:</strong> {escape(k["tip"])}</blockquote>',
    ]
    block_mist = [
        f"<h2>أخطاء شائعة قبل طلب {escape(noun)}</h2>",
        f'<blockquote class="warning-box"><i class="fa-solid fa-triangle-exclamation"></i> <strong>تنبيه:</strong> {escape(k["warn"])}</blockquote>',
        "<ul>" + "".join(f"<li>{escape(m)}</li>" for m in k["mistakes"]) + "</ul>",
    ]
    block_local = [
        f"<h2>العمل داخل {escape(city['label'])}</h2>",
        f"<p>التغطية تشمل {escape(k['areas_txt'])}. {escape(city['access'])}</p>",
        f"<p>{escape(city['buildings'])}</p>",
        f"<p>مثال عملي: عمل في {escape(k['areas'][0])} قد يختلف عن {escape(k['areas'][1])} في الوقوف وارتفاع الخزان أو نوع الأرضية.</p>",
    ]
    block_rel = [
        f"<h2>خدمات مرتبطة بـ{escape(noun)}</h2>",
        k["rel_html"] or "<p>تُعرض الخدمات المرتبطة فقط إذا ظهرت أثناء الفحص.</p>",
        "[post_services]",
        "<ul>"
        + "".join(f'<li><a href="{u}">{escape(t)}</a></li>' for t, u in k["related"][1:3])
        + "</ul>",
    ]
    block_close = [
        f"<h2>الخطوة التالية لـ{escape(kw)}</h2>",
        f"<p>{escape(k['direct'])}</p>",
        '<div class="rukn-cta">'
        '<p><i class="fa-solid fa-headset"></i></p>'
        f"<h2>هل تحتاج إلى {escape(noun)} في {escape(city['name'])}؟</h2>"
        f"<p>صف العطل أو أرسل صورة وسنحدد إن كانت الزيارة في {escape(city['name'])} كافية. لا نضع سعراً قبل المعاينة.</p>"
        f'<p class="rukn-hero-actions"><a class="rukn-btn" href="{TEL}"><i class="fa-solid fa-phone"></i> اتصل الآن</a>'
        f'<a class="rukn-btn rukn-btn-wa" href="{WA_URL}"><i class="fa-brands fa-whatsapp"></i> واتساب</a></p>'
        "</div>",
    ]
    extra = _long_unique_blocks(
        k["noun"], k["city"], k["spec"], k["outline"], k["areas_txt"], k["company_line"], k["seed"]
    )
    family = family_sections(
        k["fam"], k["noun"], k["city"], k["spec"], k["areas"], k["outline"], k["seed"]
    )
    scenario = _city_scenario(k["noun"], k["city"], k["city_key"], k["spec"], k["areas"], k["outline"])
    depth = depth_blocks(
        k["outline"], k["noun"], k["city"], k["spec"], k["areas"], k["who"], k["seed"]
    )
    checklist = [inspection_list(k["noun"], k["city"], k["spec"], k["areas"], k["seed"])]
    essays = city_essays(k["outline"], k["noun"], k["city"], k["spec"], k["areas"], k["who"])

    order_map = {
        0: [block_what, block_signs, extra, family, depth, essays, checklist, scenario, block_types, block_steps, block_cost, block_cmp, block_mist, block_local, block_rel, block_close],
        1: [block_signs, block_what, block_steps, extra, depth, essays, checklist, family, block_types, scenario, block_local, block_cost, block_mist, block_cmp, block_rel, block_close],
        2: [block_local, block_what, extra, scenario, depth, essays, family, checklist, block_types, block_steps, block_mist, block_cost, block_cmp, block_signs, block_rel, block_close],
        3: [block_what, block_types, extra, block_signs, family, depth, essays, checklist, block_local, scenario, block_steps, block_cmp, block_cost, block_mist, block_rel, block_close],
        4: [block_signs, extra, scenario, depth, essays, checklist, block_local, block_what, family, block_steps, block_cost, block_types, block_cmp, block_mist, block_rel, block_close],
        5: [block_what, extra, family, depth, essays, checklist, block_local, block_signs, scenario, block_cmp, block_steps, block_types, block_mist, block_cost, block_rel, block_close],
    }
    for blk in order_map[k["outline"]]:
        sections.extend(blk)
    sections.append("</div>")
    return sections
