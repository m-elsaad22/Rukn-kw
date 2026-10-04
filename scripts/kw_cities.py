"""Kuwait governorate profiles used to keep city pages from becoming find-replace copies."""

CITIES = {
    "kuwait": {
        "key": "kuwait",
        "name": "الكويت",
        "prep": "بالكويت",
        "in": "في الكويت",
        "label": "مدينة الكويت",
        "areas": [
            "الشرق",
            "المرقاب",
            "القبلة",
            "دسمان",
            "الصالحية",
            "كيفان",
            "الخالدية",
            "الشامية",
            "الفيحاء",
            "الروضة",
            "العديلية",
            "القادسية",
            "المنصورية",
            "الدعية",
        ],
        "buildings": "بيوت قديمة في الوسط وأبراج سكنية قرب الشرق، مع مجالس واسعة وشقق إدارية فوق المحلات",
        "climate": "رطوبة ساحلية صيفاً وغبار موسمي يلتصق بالزجاج والمكيفات والسطوح",
        "access": "الوقوف في الشرق والصالحية يحتاج تنسيقاً زمنياً أوفّق من الأحياء الداخلية",
        "water": "ضغط المياه يختلف بين الأدوار العالية في الأبراج والبيوت الأرضية",
        "angle": "ساحلي_إداري",
    },
    "hawalli": {
        "key": "hawalli",
        "name": "حولي",
        "prep": "بحولي",
        "in": "في حولي",
        "label": "محافظة حولي",
        "areas": [
            "حولي",
            "السالمية",
            "الجابرية",
            "الرميثية",
            "سلوى",
            "بيان",
            "مشرف",
            "الشعب",
            "النقرة",
        ],
        "buildings": "كثافة شقق وأبراج في السالمية وحولي، وفلل أهدأ في بيان ومشرف",
        "climate": "رذاذ بحري في السالمية يسرّع تآكل الألمنيوم والتكييف الخارجي",
        "access": "الشوارع التجارية في حولي والسالمية تزدحم ظهراً، لذلك نثبّت ساعة الدخول",
        "water": "مضخات العمائر شائعة، وأي ضعف فيها يغيّر تشخيص السباكة والسخان",
        "angle": "ساحلي_كثيف",
    },
    "farwaniya": {
        "key": "farwaniya",
        "name": "الفروانية",
        "prep": "بالفروانية",
        "in": "في الفروانية",
        "label": "محافظة الفروانية",
        "label_alt": "الفروانية",
        "areas": [
            "الفروانية",
            "خيطان",
            "العمرية",
            "الرابية",
            "الأندلس",
            "جليب الشيوخ",
            "الفردوس",
            "الرقعي",
            "العارضية",
        ],
        "buildings": "مزيج عمائر سكنية ومحلات أرضية وبيوت عوائل، مع حركة يومية أعلى من الضواحي",
        "climate": "غبار داخلي أعلى من الساحل بسبب الحركة والرياح، والحرارة تنعكس على الأسطح",
        "access": "جليب الشيوخ وخيطان يحتاجان نافذة صباحية أو مسائية لتفادي الزحام",
        "water": "شبكات أقدم في بعض البيوت تجعل التسرب يظهر متأخراً تحت البلاط",
        "angle": "سكني_تجاري",
    },
    "mubarak-al-kabeer": {
        "key": "mubarak-al-kabeer",
        "name": "مبارك الكبير",
        "prep": "بمبارك الكبير",
        "in": "في مبارك الكبير",
        "label": "محافظة مبارك الكبير",
        "areas": [
            "مبارك الكبير",
            "القرين",
            "العدان",
            "القصور",
            "أبو فطيرة",
            "صباح السالم",
            "المسيلة",
            "الفنيطيس",
        ],
        "buildings": "فلل حديثة وشوارع أوسع، مع أحواش وملاحق خارجية أكثر من وسط المدينة",
        "climate": "حرارة السطح أعلى، والغبار يصل للحدائق والمكيفات الخارجية بسرعة",
        "access": "الوقوف أسهل غالباً، لكن بعض الأزقة الداخلية تحتاج تنبيه الحارس أو أهل البيت",
        "water": "خزانات سطحية شائعة في الفلل، وأي خلل فيها ينعكس على الضغط صيفاً",
        "angle": "فلل_ضواحي",
    },
    "al-ahmadi": {
        "key": "al-ahmadi",
        "name": "الأحمدي",
        "prep": "بالأحمدي",
        "in": "في الأحمدي",
        "label": "محافظة الأحمدي",
        "areas": [
            "الأحمدي",
            "الفحيحيل",
            "الفنطاس",
            "المنقف",
            "أبو حليفة",
            "العقيلة",
            "الصباحية",
            "الرقة",
            "هدية",
            "فهد الأحمد",
        ],
        "buildings": "فلل واسعة وبيوت عمالية ومناطق ساحلية، مع أسطح كبيرة تحتاج عزل ومتابعة",
        "climate": "رطوبة ساحلية في الفنطاس والفحيحيل، وغبار وحرارة أعلى في الداخل",
        "access": "المسافات بين الأحياء أطول، لذلك نجمع الأعمال المتقاربة في نفس اليوم عند الاتفاق",
        "water": "خزانات ومضخات منزلية منتشرة، والضغط يختلف بين البيوت الأرضية والدور العلوي",
        "angle": "ساحلي_مساحات",
    },
    "al-jahra": {
        "key": "al-jahra",
        "name": "الجهراء",
        "prep": "بالجهراء",
        "in": "في الجهراء",
        "label": "محافظة الجهراء",
        "areas": [
            "الجهراء",
            "النعيم",
            "القصر",
            "العيون",
            "القيروان",
            "كاظمة",
            "الواحة",
            "جنوب الجهراء",
        ],
        "buildings": "بيوت وفلل بمساحات أكبر وأحواش ترابية أو مزروعة، مع ملاحق خارجية متكررة",
        "climate": "غبار صحراوي يلتصق بالستائر والدكت والخزانات أكثر من الساحل",
        "access": "المسافة من العاصمة أطول، لذلك نؤكد الموعد صباح التنفيذ لا وعداً جامداً قبل أسبوع",
        "water": "الخزانات السطحية والغبار حول فتحاتها جزء ثابت من الفحص",
        "angle": "صحراوي_واسع",
    },
}

CITY_SUFFIX = {
    "kuwait": "kuwait",
    "hawalli": "hawalli",
    "farwaniya": "farwaniya",
    "mubarak-al-kabeer": "mubarak-al-kabeer",
    "al-ahmadi": "al-ahmadi",
    "al-jahra": "al-jahra",
}


def city_note(city: dict, family: str = "", service_slug: str = "") -> str:
    """Governorate sentence that matches the service — not a pasted water/building line."""
    slug = (service_slug or "").lower()
    fam = (family or "").lower()
    buildings = city.get("buildings") or ""
    climate = city.get("climate") or ""
    access = city.get("access") or ""
    water = city.get("water") or ""
    if fam == "pest" or any(x in slug for x in ("pest", "insect", "termite", "cockroach", "bed-bug", "ant", "rodent")):
        return f"{climate} أماكن الاختباء تختلف حسب المبنى: {buildings}"
    if "diesel" in slug:
        return f"{access} نقرأ خزان الديزل من موقعه وتهويته، لا من ضغط مياه البيت."
    if fam == "ac" or any(x in slug for x in ("ac-", "-ac", "duct", "split-ac", "central-ac")):
        return climate
    if fam in ("garden", "solar") or ("pool" in slug and "pest" not in slug):
        return f"{climate} {access}"
    if fam in ("moving", "ship"):
        return access
    water_slug = any(
        x in slug
        for x in ("water", "plumb", "leak", "tank", "heater", "pump", "drain", "sewage")
    )
    if "diesel" not in slug and (fam in ("leaks", "elec") or water_slug):
        return water
    if fam == "cleaning" and any(x in slug for x in ("tank", "bathroom", "kitchen", "pool")):
        return water
    if fam in ("paint", "reno", "install"):
        return f"{buildings} {climate}"
    return buildings


def parse_slug(slug: str):
    for key in (
        "mubarak-al-kabeer",
        "al-ahmadi",
        "al-jahra",
        "farwaniya",
        "hawalli",
        "kuwait",
    ):
        suf = "-" + key
        if slug.endswith(suf):
            return slug[: -len(suf)], key
    return slug, "kuwait"
