# كتالوج عيوب موقع ركن التطور — الكويت

تاريخ الفحص: 16 سبتمبر 2026  
الموقع الحي: https://rukn-eltatawer.com/kw/  
المنصة: ووردبريس 7.1 · قالب Kayan Theme 1.4.2 · PHP 8.3.33 · LiteSpeed  
الإضافات: Polylang 3.8.9 · Rank Math 1.0.278 · LiteSpeed Cache 7.9.1 · WPCode Lite 2.3.9 · Classic Editor · Classic Widgets · Easy TOC 2.0.87.1 · Rukn CSV Importer 2.0.0 · WPVibe 1.16.5 · Advanced Editor Tools 5.10.1

> الرابط المرسل `rukn-eltawer.com` لا يوجد له DNS (NXDOMAIN). المضيف الصحيح: **rukn-eltatawer.com**.

هذا الملف يستخرج **كل عيب ونقص** ظهر في الواجهة، لوحة التحكم، الخيارات، والمحتوى، وملفات القالب.  
ما طُبّق سابقاً (أرقام DNI، slug الإنجليزية `english`، سايت ماب 200، `service_categories`) موثّق في `audit/kuwait-live-site-report.md`. الرقم المنشور يبقى **+971** إلى حين إصدار خط **+965**. لا يُعاد استيراد CSV فوق المقالات المنشورة.

---

## ملخص تنفيذي

| المستوى | العدد التقريبي | أمثلة |
|---|---|---|
| حرج (SEO / فهرسة / هوية الدولة) | 18 | canonical مضاعف `/kw/kw/`، 404 يُحوَّل للرئيسية، Schema فارغ، خريطة دبي، «اختر الإمارة»، عنوان/وصف الرئيسية مقطوعان |
| عالٍ (واجهة / تحويل / لغة) | 22 | قائمة سطح المكتب فارغة، بحث الواجهة 0 نتائج، لا نموذج تواصل، الإنجليزية ليست لغة Polylang، `html lang=ar` على الصفحات الإنجليزية |
| متوسط (محتوى / إعدادات ناقصة) | 28 | 1248 مقالاً بلا صورة، CPT فارغ، سوشيال/خريطة/شعار غير مضبوطين، عناوين مكررة |
| منخفض / تقني في القالب | 20+ | قوالب WP ناقصة، خطأ إملائي `YourColoe`، منطق Schema مكسور، بقايا الإمارات في الودجات |

---

## أ) حرج — فهرسة وSEO والهوية المحلية

### A1. Canonical مضاعف المسار على الرئيسية و`/en/`

- الرئيسية: `<link rel="canonical" href="https://rukn-eltatawer.com/kw/kw/">`
- `/kw/en/`: canonical `https://rukn-eltatawer.com/kw/kw/en/`
- السبب المحتمل: الموقع مثبت في مجلد `/kw` و`home` = `https://rukn-eltatawer.com/kw`، ثم Rank Math أو Polylang أو سكربت WPCode يضيف `/kw` مرة ثانية.
- الأثر: جوجل قد يفهرس مساراً غير موجود أو يعتبر الصفحة نسخة.

### A2. عنوان ووصف الرئيسية لا يُطبَّقان

إعداد Rank Math موجود وصحيح:

- `homepage_title` = `ركن التطور الكويت | كشف تسربات، عزل، تكييف وصيانة في كل المحافظات`
- `homepage_description` = فقرة كاملة عن الخدمات بالدينار الكويتي

ما يظهر في HTML:

- `<title>ركن التطور الكويت</title>` (اسم الموقع فقط)
- `meta description` = `ركن التطور الكويت`
- `og:title` يحتفظ بالعنوان الطويل، أي أن Open Graph و`<title>` غير متطابقين

السبب: **`show_on_front = posts`** و`page_on_front = 0`. لا توجد صفحة ثابتة للرئيسية. القالب يحقن هوم مخصّص عبر `index.php` → `TemplatePart('home')` بينما ووردبريس/Rank Math يعامل الصفحة كأرشيف مقالات. حقول عنوان الرئيسية في Rank Math لا تُطبَّق على أرشيف المقالات.

### A3. `robots.txt` لمجلد الكويت يعيد 302

- `https://rukn-eltatawer.com/kw/robots.txt` → **HTTP 302** إلى `https://rukn-eltatawer.com/kw` (وسم LiteSpeed: `HTTP.404`)
- السايت ماب مذكور فقط في `https://rukn-eltatawer.com/robots.txt` الجذري
- مزيج `www` / بدون www في نفس الملف الجذري (الإمارات/السعودية/قطر بـ www، الكويت/عمان/البحرين/مصر بدون)

### A4. صفحات 404 تُحوَّل للرئيسية (soft 404)

ملف القالب:

`components/packs/@404/shape.php`

```php
wp_redirect( home_url() );
```

أي رابط غير موجود (مثال: `/kw/this-page-does-not-exist-xyz/` و`/kw/contact/`) يرجع **200 على الرئيسية** بدل 404. جوجل يعامل ذلك كـ soft 404، وتتضرر مراقبة الروابط الميتة في Rank Math 404 Monitor.

قوالب ووردبريس القياسية **غير موجودة** (`404.php`, `search.php`, `single.php`, `page.php`, `archive.php`). WPVibe يسجّلها ضمن `templates_missing`. التوجيه يتم عبر `syntax.php` (`ThemeStatic::Locate`) وليس هرمية القوالب.

### A5. Schema LocalBusiness فارغ وغير صالح لجوجل

يُطبع على الرئيسية و`/en/`:

```json
{
  "@type": "LocalBusiness",
  "name": "",
  "description": "",
  "address": { "streetAddress": "", "addressLocality": "", "addressRegion": "", "postalCode": "", "addressCountry": "" },
  "telephone": "",
  "aggregateRating": { "@type": "AggregateRating", "ratingValue": "", "reviewCount": "" }
}
```

في القالب `SchemaItems/LocalBusiness.php`:

- اسم الخيار مكتوب خطأ: **`YourColoe_Schema_business`** (ناقص r) — الخيار غير موجود في قاعدة البيانات
- يطبع `aggregateRating` فارغاً دائماً إن لم تُملأ الحقول (مخالف لإرشادات Google)
- خصائص غير قياسية: `socialMedia`, `website`, `operationDays`
- JSON-LD يستخدم `http://schema.org` وقد يفسد بسبب فواصل/`socialMedia`

خيار Rank Math:

- `knowledgegraph_type` = **company** (يجب LocalBusiness / HomeAndConstructionBusiness)
- `knowledgegraph_name` = **ركن التطور** بدون «الكويت»
- `local_business_type` = **Organization**
- لا `kayan_seo_gbp_url` (رابط Google Business Profile للكويت)

شعار المؤسسة في Schema Rank Math: صورة ترس من موقع الإمارات  
`https://www.rukn-eltatawer.com/wp-content/uploads/icon/setting.png`

### A6. hreflang يشير إلى صفحة عربية

على الرئيسية:

- `hreflang="ar"` → `https://rukn-eltatawer.com/kw/`
- `hreflang="en"` → `https://rukn-eltatawer.com/kw/en/`

`/kw/en/` يعرض **نفس الهوم العربية** (h1 عربي، dir=rtl) مع `og:locale=en_US` وcanonical `/kw/kw/en/`. المسار الإنجليزي الفعلي هو `/kw/english/` وليس له hreflang.

الصفحات الإنجليزية (خدمات/تواصل/محافظات) **بلا hreflang**.

### A7. تعارض الروابط: أرشيف CPT يصطدم بالمقالات

- `/kw/services/water-leak-detection/` **يُحوَّل** إلى مقال مدونة `.../water-leak-detection-al-ahmadi/`
- الصفحة الإنجليزية الصحيحة: `/kw/english/services/water-leak-detection/`
- أرشيف CPT `/kw/services/` يعمل، لكن h1 = **`services`** (slug إنجليزي خام لا «الخدمات»)
- نفس العيب: `/reviews/` h1=`reviews`، `/faqs/` عنوان الأرشيف إنجليزي خام

### A8. سايت ماب التصنيفات يشير إلى taxonomy غير مستخدم كما يُتوقع

- `sitemap_index.xml` يتضمن `category-sitemap.xml`
- ووردبريس العام **لا يعرّض REST `/categories`**
- المقالات مصنّفة على `cities` و`service_categories` وليس `category` الافتراضي
- صور السايت ماب: `include_featured_image = off` و**0** مقالات لها صورة مميزة أصلاً

### A9. هوية الدولة مختلطة: الكويت في الإعدادات / الإمارات في الواجهة

| عنصر | القيمة الحية |
|---|---|
| رقم الهاتف/واتساب/DNI | +971586634710 |
| `company__adress` | مدينة الكويت، الكويت |
| `company__map_code` | **فارغ** → الخريطة الافتراضية **دبي، الإمارات** |
| ودجت الباحث | تسمية **«اختر الإمارة»** + قائمة دبي/أبوظبي إن لم تُملأ المدن |
| ودجت الإحصائيات (افتراضي القالب) | «ثقة الآلاف من العملاء في جميع أنحاء **الإمارات**» |
| ودجات الحالات/الأعمال/الآراء/الأسئلة | أمثلة دبي مارينا، «إمارات الدولة السبع» |
| محتوى 1248 مقالاً | كلها تحتوي `971` في النص |

`kayan-i18n/countries.php` يعرف الكويت بشكل صحيح، لكن الفوتر والودجات لا تقرأ دولة المجلد؛ تسقط على قيم الإمارات.

---

## ب) حرج/عالٍ — الواجهة والتحويل

### B1. قائمة سطح المكتب فارغة

- قائمة WP «القائمة الرئيسية» معيّنة على موقع `main-menu` وفيها 5 عناصر: الرئيسية، من نحن، اتصل بنا، المدونة، English
- HTML: `<nav class="menu"></nav>` **فارغ**
- الشعار أيقونة Font Awesome + نص، **وليس** `logo.webp` المرفوع (المكتبة فيها 5 ملفات فقط ولم تُربط)
- عنصر English يشير إلى **`/kw/en/`** (عربي) لا `/kw/english/`
- لا قائمة إنجليزية منفصلة (`pll.nav_menus` فارغ)

الكود في `#header/part.php` يبني الشجرة من `wp_get_nav_menu_items`. النتيجة الفارغة تعني أن العناصر تُصفَّى في الواجهة (Polylang أو فشل `get_nav_menu_locations` أمام الزائر) أو أن سطح المكتب لا يُظهر ما يُفترض أن يظهر.

### B2. البحث الأمامي يعيد صفراً رغم REST

- `/kw/?s=leak` → `/kw/search/leak`
- h1 مزدوج: «نتائج البحث عن leak» + «لم يتم العثور علي "leak"»
- `<article>` / `hentry` = 0
- REST `/wp/v2/search?search=leak` يجد صفحات إنجليزية؛ البحث العربي «كشف» موجود في 1248 مقالاً عبر REST
- لا canonical لصفحة البحث
- القالب يعيد توجيه `?s=` إلى `/search/` في `syntax.php` ثم يعرض قالب بحث داخلي فارغ (`search.php` غير موجود)

### B3. لا نموذج تواصل

- لا Contact Form 7 ولا WPForms ولا أي إضافة نماذج
- `/kw/contact-us/` و`/kw/english/contact-us/`: نص + هاتف/واتساب **بدون `<form>`**
- سياسة الخصوصية تتحدث عن «نماذج التواصل» وهي غير موجودة
- `/kw/contact/` يُحوَّل للرئيسية بسبب A4

### B4. عدّادات الإحصائيات تظهر 0 ونصوص ناقصة

HTML الرئيسية:

- `<div class="num" data-count="16">0</div>` و`data-count="8">0`
- `<div class="num">[[عدد المشاريع]]</div>` و`[[سنة التأسيس]]` — **رموز قوالب غير مستبدلة**
- العداد يعتمد IntersectionObserver في `rukn_stats.php` / الهيرو؛ إن لم يعمل JS يبقى 0
- المحتوى الافتراضي للودجت إماراتي (15000 عميل، «الإمارات»)

### B5. 16 رابطاً `href="#"` في الرئيسية

روابط خدمات (علامات تسرب المياه، الكشف بدون تكسير، أنواع العزل…) كلها `#`.  
رابط العنوان في الفوتر أيضاً `#` لأن `footer__company__adress_url` غير موجود.

### B6. خريطة الفوتر على دبي

`#footer/part.php` سطر 156:

```php
if( empty( $footer__map_embed ) ) $footer__map_embed = 'https://maps.google.com/maps?q=Dubai,United+Arab+Emirates&z=12&output=embed';
```

`company__map_code` فارغ في الخيارات. حقل الخريطة أُضيف في 1.4.1 بتعليق صريح أنه كان مفقوداً فتبقى الخريطة على دبي — **ولم يُملأ بعد للكويت**.

عنوان الفوتر يسقط على «دبي، الإمارات العربية المتحدة» إن فُرغ `company__adress` (مضبوط الآن على مدينة الكويت).

### B7. الباحث الجغرافي مبني على تصنيفات الإمارات

`rukn_finder.php`:

- التسمية ثابتة: **اختر الإمارة**
- الوضع التلقائي يقرأ taxonomy **`category`** و**`city`**
- `category` غير ظاهر كتصنيف عام للمقالات؛ `city` (المفرد) **0 حدود**
- التصنيف الفعلي للمحافظات: **`cities`** (جمع) — 6 محافظات × 208 مقالاً
- إن فرغت القوائم: افتراض دبي، أبوظبي، الشارقة…

### B8. أزرار الاتصال تعمل الآن لكن برقم إماراتي

بعد الإصلاح السابق:

- DNI: `phone` و`wa_number` = 971586634710
- `RuknCS.call_show=true`, `call_number=+971586634710`
- لا يظهر رقم +965 في كامل HTML المفحوص

ثوابت القالب ما زالت إماراتية:

```php
define('RUKN_CS_DEFAULT_WA', '971586634710');
```

RuknContact يعلّق حقول التصنيف على **`category`** لا `service_categories`/`cities`، فيسقط المستوى الهرمي للتصنيف على موقع لا يستخدم `category`.

---

## ج) اللغة (Polylang) — إعدادات ناقصة ومتضاربة

| الإعداد | القيمة | المشكلة |
|---|---|---|
| اللغات | ar (افتراضي) + en | — |
| محتوى معيّن `en` | **0** منشورات/صفحات | 27 صفحة إنجليزية موجودة كأبناء لصفحة `english` وليست ترجمات Polylang |
| `home_url` للإنجليزية | `/kw/en/` | يعرض العربية |
| `locale` الإنجليزية | `en_US` | الأنسب `en_GB` أو `en` للكويت وليس الولايات المتحدة |
| علم الإنجليزية | `us.png` عبر **http://** | محتوى مختلط + علم أمريكا |
| `browser` | true | إعادة توجيه حسب لغة المتصفح قد تُدخل الزائر إلى `/en/` العربي |
| `force_lang` | 1 | بادئة اللغة |
| `hide_default` | true | العربية بلا بادئة |
| `html lang` على `/english/` | **ar** + **dir=rtl** | الصفحة إنجليزية |
| `og:locale` على `/english/` | **ar_AR** | يجب en_US/en_GB |
| المقالات العربية | 1248 بلا مقابل EN | لا hreflang للمقالات |
| أنواع Polylang | services, reviews, faqs… | الـ CPT فارغ أصلاً |
| تصنيفات Polylang تتضمن | `category`, `city`, `questions` | `category` غير مستخدم، `city` فارغ، `questions` مربوط بـ `bot` غير المسجّل كنوع ظاهر |

صفحة 3819 (slug=`english`) حلّت المسارات `/kw/english/...` لكنها **ليست** لغة Polylang. طبقتان للإنجليزية تتصارعان: بادئة `en` vs شجرة صفحات `english`.

---

## د) المحتوى والبيانات

### D1. المقالات (1248 منشورة)

| فحص | النتيجة |
|---|---|
| صورة مميزة `_thumbnail_id` | **0 / 1248** |
| `<img` داخل المحتوى | **0 / 1248** |
| ذكر `971` في المحتوى | **1248 / 1248** |
| وسوم | 3 وسوم فقط، كل منها count=1 |
| عناوين مكررة | **24 مجموعة** (عنوانان لكل منها) — سباك منازل، كهربائي منازل، تركيب عشب… |
| مكتبة الوسائط | **5** ملفات شعارات، 4 منها `alt` فارغ |
| `og:image` للمقالات | ترس الإمارات أو شعار عام |

عينة مقال 1278: ~65KB HTML نصي بلا صور، 6 مرات 971.

### D2. خدمات CPT (16)

- كل خدمة: **160–200 حرفاً**، بلا صورة، بلا تفاصيل/أسعار/FAQ
- أرشيف h1 إنجليزي خام
- لا تصادم مقصود مع صفحات `/english/services/...` إلا عبر slug العربي `/services/{slug}/` الذي يلتقط مقال المدونة

### D3. CPT فارغة بالكامل

| النوع | العدد | أرشيف الواجهة |
|---|---|---|
| reviews | 0 | h1=`reviews` |
| faqs | 0 | الأسئلة في الرئيسية من ودجت القالب (نصوص إمارات) لا من CPT |
| pricing | 0 | — |
| portfolio | 0 | — |
| before_after | مسجّل في الثيم / REST 404 للمسار | — |

لا ودجات/سايدبار: `wp sidebar list` و`wp widget list` = **[]**. Classic Widgets مفعّل دون مناطق مسجّلة.

### D4. الصفحات (31)

**عربية (4):** مدونة، خصوصية، من نحن، اتصل بنا. المدونة محتواها سطر واحد (~52 حرفاً) وh1 مكرر مرتين. الواجهة: **0 بطاقات مقالات** (`article`/`hentry` = 0) رغم 1248 منشوراً و`page_for_posts=1282`.

**إنجليزية (27):** كلها `featured_media=0`، بلا نموذج، محتوى 400–1400 حرف. لا صفحات عربية مقابلة للمحافظات (`/kw/hawalli/` إلخ تُبتلع كـ 404→رئيسية). الصفحات الإنجليزية للمحافظات فقط تحت `/kw/english/{city}/`.

`salmiya` و`fintas` مصنّفان في `cities` **بعدد 0 مقالات** ويظهران في النظام دون محتوى.

### D5. تصنيفات مزدوجة وغير مكتملة

- `cities` (هرمي، على post+CPT): 6 محافظات × 208 + السالمية 0 + الفنطاس 0
- `city` (غير هرمي، على post فقط): **فارغ** — وهو ما يقرأه الباحث
- `service_categories`: 14 فئة مجموع counts = 1248، لكن `object_type` = **services و portfolio فقط** (ليست المقالات في تعريف التسجيل). الربط السابق عبر SQL قد لا يظهر في محرر المقال
- لا `category` عام في قائمة التصنيفات العامة بينما القالب وRuknContact يعتمدان عليه
- Polylang ما زال يزامن `category`

### D6. CSV في المستودع

`rukn-eltatawer-kuwait-FULL.csv`: 1248 صفاً، **كلها draft**، 2496 `{PHONE_RUKN_KUWAIT}` و2496 `{WHATSAPP_RUKN_KUWAIT}`، 1224 عنواناً فريداً (24 تكراراً). **لا تعِد الاستيراد فوق المنشور.**

---

## هـ) إعدادات القالب وRank Math الناقصة

خيارات **فارغة أو غير موجودة** (يُفترض ملؤها لموقع كويتي):

- `footer__logo`, `footer__content`, `social_footer`, `social_footer_list`
- `facebook`, `instagram`, `twitter`, `youtube`, `linkedin` = فارغ
- `footer__company__adress_url`, `company__map_code`, `company__map_title`
- `YourColoe_Schema_business` / أي Schema عمل محلي للثيم
- `kayan_seo_gbp_url`, `kayan_seo_local_type`
- شعار الموقع: لا خيار `logo` — الهيدر نص+أيقونة؛ `site_icon=8777` (logo-icon.webp بلا alt في الميديا)
- `site_logo` في إعدادات WP = null

Rank Math:

- نوع المعرفة Company/Organization لا LocalBusiness كويتي
- شعار المؤسسة من نطاق الإمارات `www.rukn-eltatawer.com`
- `hasSitemap=0` داخل `rank_math_analytics_all_services` رغم أن السايت ماب HTTP 200
- وحدات مفعّلة تشمل 404-monitor بينما الثيم يلغي 404
- لا إعدادات Webmaster منفصلة (`rank_math_webmaster` غير موجود كخيار بهذا الاسم)

WPCode:

- منشور واحد: 3811 (سكربت الكويت)
- **9 مسودات** بقايا تجارب (`Rukn KW REST ping`, completeness…)
- **14 في المهملات**

لا إضافة نماذج. التعليقات مغلقة. `blog_public=1`.

---

## و) عيوب القالب البرمجية (Kayan 1.4.2)

المسار الحي: `wp-content/themes/kayan-theme`  
المصدر المشار إليه في style.css: github.com/m-elsaad22/Kayan-Theme

1. **لا `single.php` / `page.php` / `archive.php` / `404.php` / `search.php`** — التوجيه عبر `syntax.php` و`index.php` فقط.
2. **`@404/shape.php` يحوّل كل 404 للرئيسية** — يجب صفحة 404 حقيقية مع status 404.
3. **`LocalBusiness.php`**: خطأ `YourColoe`؛ يطبع تقييمات فارغة؛ JSON غير قياسي.
4. **منطق الإخفاء مقلوب/هش**: يطبع السكيما فقط إذا وُجد مفتاح `hide_schema_business` وكان فارغاً؛ وملف `schema/setup.php` يكرر LocalBusiness.
5. **الفوتر**: افتراض خريطة دبي وعنوان دبي.
6. **`rukn_finder.php`**: «إمارة» + taxonomies خاطئة (`category`, `city`).
7. **ودجات Standard** (`rukn_cases`, `rukn_reviews`, `works`, `Faqs__simple2`, `rukn_results`, `city__widget`): محتوى افتراضي إماراتي.
8. **`rukn_stats.php`**: نص افتراضي «الإمارات»؛ العداد يبدأ من 0.
9. **RuknContact**: مربوط بـ `category`؛ ثابت واتساب 971.
10. **`functions.php`**: `@ini_set` و`ob_start()` في الثيم؛ `__()` بثلاث وسوم خاطئة في `AddTaxonomy`.
11. **هيدر**: مخرجات غير صالحة HTML5 (`<root>` كغلاف الصفحة).
12. **`rel` مكرر** على زر واتساب: `rel="nofollow noopener noreferrer" rel="noopener"`.
13. **أعلام Polylang http://** (محتوى مختلط).
14. **Easy TOC** يظهر «Toggle» بالإنجليزية داخل الصفحات العربية والإنجليزية.
15. **`show_on_front=posts`** يتعارض مع هوم الثيم المحقون في `kayan-stabilization/homepage.php`.
16. **تضارب `cities` vs `city`**.
17. **CPT `bot` / taxonomy `questions`** مذكوران في Polylang وغير ظاهرين كمنتج للموقع.
18. **النصوص الإنجليزية للأرشيف** تستخدم `post_type` slug كـ h1.
19. **البحث** لا يستخدم قالب نتائج يعرض `WP_Query` القياسي ببطاقات.
20. **لا تسجيل sidebars** رغم Classic Widgets.
21. **`DISALLOW_FILE_EDIT`** (متوقع أمنياً) مع سكربتات WPCode كثيرة في المسودات.
22. **بقايا رموز `[[عدد المشاريع]]` / `[[سنة التأسيس]]`** في محتوى الهوم الحي.

---

## ز) بنية الروابط والموقع

| المسار | السلوك |
|---|---|
| `/kw/` | هوم عربية، canonical `/kw/kw/`، قائمة فارغة، خريطة دبي |
| `/kw/en/` | نفس الهوم العربية، `og:locale=en_US` |
| `/kw/english/` | إنجليزية حقيقية، `html lang=ar` `dir=rtl` |
| `/kw/contact/` | 302/ابتلاع → الرئيسية |
| `/kw/contact-us/` | صفحة عربية بلا نموذج |
| `/kw/blog/` | بلا بطاقات مقالات، h1 مكرر |
| `/kw/services/` | أرشيف CPT، h1=`services` |
| `/kw/services/water-leak-detection/` | يتحول لمقال مدونة |
| `/kw/english/services/water-leak-detection/` | صفحة خدمة إنجليزية تعمل |
| `/kw/robots.txt` | 302 الرئيسية |
| `/kw/sitemap_index.xml` | 200 XML (Rank Math) |
| `rukn-eltawer.com` | NXDOMAIN |

إعدادات الكتابة: `/%postname%/`. الصفحة الرئيسية ليست صفحة. المدونة هي 1282 لكن الأرشيف البصري فارغ.

---

## ح) أمن وتشغيل (ملاحظات غير استغلالية)

- ووردبريس 7.1 / PHP 8.3.33 / LiteSpeed Cache 7.9.1
- WPVibe 1.16.5 يتوفر له تحديث 1.17.0
- مستخدمان: `admin` (1) و`cursor` (2، MAHMOUD ELSAAD)
- البريد: `m@rukn-eltatawer.com`
- المنطقة الزمنية: Asia/Kuwait — صحيح
- لغة الموقع: `ar`
- بداية الأسبوع: السبت — مناسب للكويت
- التعليقات/التبليغ مغلقة
- HTML الثقيل (~300KB للرئيسية) مع LiteSpeed؛ طلبات HTML العامة قد تنقطع بمهلة تحت ضغط الفحص (REST أخف)
- لا تُنشر كلمات مرور التطبيقات في المستودع

---

## ط) أولويات الإصلاح المقترحة (بدون تنفيذ في هذا الفحص)

1. صفحة 404 حقيقية: حذف `wp_redirect` من `@404/shape.php` وإرجاع 404.
2. صفحة رئيسية ثابتة (`show_on_front=page`) وربط عنوان/وصف Rank Math؛ إصلاح canonical `/kw/`.
3. `/kw/robots.txt` يجب أن يكون نصاً 200 مع السايت ماب.
4. إيقاف أو تعبئة LocalBusiness الفارغ؛ نوع Rank Math = LocalBusiness كويتي؛ شعار محلي.
5. hreflang: `en` → `/kw/english/` وتعيين صفحات EN في Polylang (أو تعطيل لغة `en` إن كانت الشجرة اليدوية هي المعتمدة).
6. إصلاح عنصر القائمة English + إظهار `nav.menu`.
7. `company__map_code` لمدينة الكويت؛ استبدال «اختر الإمارة» بـ «اختر المحافظة» وقراءة `cities`.
8. نموذج تواصل؛ إصلاح قالب البحث ليعرض النتائج.
9. صور مميزة و`og:image` كويتي؛ إزالة ترس الإمارات.
10. إفراغ CPT أو ملء reviews/faqs؛ h1 أرشيف عربي.
11. استبدال +971 بـ +965 عند الإصدار في الخيارات + DNI + 1248 مقالاً.
12. حذف مسودات WPCode الزائدة وبقايا `[[...]]`.
13. صفحات هبوط عربية للمحافظات أو إعادة توجيه منظمة إلى أرشيف `cities`.
14. لا إعادة استيراد CSV الحالي.

---

## ي) ما تم إصلاحه سابقاً على الحي (لا يُعاد)

- تعبئة `phonenumber` / `contact_number` / `whatsapp_number` / `kayan_country_kw_*`
- تشغيل أزرار الاتصال وDNI
- العنوان مدينة الكويت + إحداثيات 29.375859, 47.977405 و`ar_KW`
- slug صفحة 3819 = `english`
- سايت ماب HTTP 200
- ربط 1248 مقالاً بـ `service_categories` حسب التصنيف
