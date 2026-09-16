# تدقيق موقع ركن التطور — الكويت

تاريخ الفحص: 16 سبتمبر 2026  
الموقع الحي: https://rukn-eltatawer.com/kw/  
المنصة: ووردبريس 7.1 + قالب Kayan Theme 1.4.2 + Polylang + Rank Math + LiteSpeed + WPVibe

> الرابط المرسل `rukn-eltawer.com` لا يوجد له DNS. الموقع الصحيح هو **rukn-eltatawer.com/kw**.

## حالة الدخول

تم الاتصال بالموقع وفحص الواجهة العامة وREST بنجاح. **لم يمكن تطبيق إصلاحات داخل لوحة التحكم** لأن بيانات الدخول المرفقة مرفوضة:

| المحاولة | النتيجة |
|---|---|
| `cursor` + كلمة المرور العادية | «كلمة المرور غير صحيحة» |
| كلمة مرور التطبيقات على `/kw` والموقع الرئيسي و`/sa` | `incorrect_password` / تطبيق غير صالح |
| البريد `m@rukn-eltatawer.com` | موجود، لكن كلمة المرور غير صحيحة |
| XML-RPC | 403 من LiteSpeed |

المستخدم `cursor` (الاسم الظاهر: MAHMOUD ELSAȚD، المعرّف 2) موجود على الموقع. أعد توليد **كلمة مرور تطبيقات** من المستخدم ← الأمان، وأرسلها دون أخطاء نسخ، ثم يمكن تشغيل `scripts/apply_kuwait_wp_fixes.py`.

## الأعطال الحرجة

### 1) أرقام التواصل ناقصة أو إماراتية على موقع كويتي

| المصدر | القيمة |
|---|---|
| Kayan DNI `GET /wp-json/kayan/v1/dni` | `phone: ""`, `wa_number: ""` |
| `window.RuknCS.call_number` | فارغ في سكربت، و`+971586634710` في سكربت آخر |
| `window.RuknCS.call_show` | `false` |
| أزرار الهاتف في الثيم (`kayan_show_call_buttons`) | مخفية افتراضياً |
| Schema / واتساب / اتصل بنا | `+971 58 663 4710` (رمز الإمارات) |
| البريد | `m@rukn-eltatawer.com` |

صفحة اتصل بنا الإنجليزية تقول صراحة إن الرقم +971 مؤقت إلى حين إصدار رقم +965. هذا يفسّر الفراغ في DNI و`call_number`. حتى مع الرقم المؤقت يجب تعبئة خيارات الثيم حتى لا تبقى أزرار الاتصال مكسورة.

سكربت في الصفحة يلصق الرقم مرتين:

```js
a.href = "tel:+971586634710" + phone;
a.href = "tel:+971586634710" + cfg.call_number;
```

وعند طلب الخدمة يُبنى رابط واتساب مكسور بإضافة `?text=` مرتين.

**ما يجب ضبطه في خيارات القالب (Theme Options):**

- `phonenumber` / `contact_number` = الرقم المعتمد (حالياً `+971586634710` إلى حين +965)
- `whatsapp_number` = `971586634710`
- `kayan_show_call_buttons` = تشغيل
- أرقام Kayan Track → جدول الأرقام + DNI

### 2) `robots.txt` وملفات Sitemap للكويت ترجع HTTP 404

المحتوى XML/نصي موجود، لكن **رمز الحالة 404**. جوجل يتجاهل السايت ماب إذا كان 404.

- https://rukn-eltatawer.com/kw/robots.txt → 404
- https://rukn-eltatawer.com/kw/sitemap_index.xml → 404
- https://rukn-eltatawer.com/kw/post-sitemap.xml → 404

`robots.txt` الجذري للموقع الرئيسي يذكر سايت ماب الكويت بشكل صحيح، لكن سايت ماب الكويت نفسه 404.

### 3) النسخة الإنجليزية منهارّة (Polylang)

- اللغة الإنجليزية: `count = 0` للمقالات
- `page_on_front = 0` للعربية والإنجليزية (لا توجد صفحة رئيسية ثابتة في Polylang)
- صفحة إنجليزية slug=`en` (id 3819) تتصادم مع بادئة Polylang `/en/`
- `/kw/en/` و`/kw/english/` يعيدان الصفحة العربية
- `hreflang="en-KW"` يشير إلى `/kw/english/` بينما Polylang يستخدم `/kw/en/`
- صفحات EN (خدمات، تواصل، سياسة الخصوصية، المدن) لها **نفس رابط** الصفحات العربية بسبب أن الأب هو صفحة `en`

**الإصلاح:** تغيير slug الصفحة 3819 من `en` إلى `home` (أو `english`)، تعيينها صفحة رئيسية للإنجليزية في Polylang، وتعيين الصفحة العربية الرئيسية صفحة أمامية للعربية.

### 4) تصنيف المقالات غير مكتمل

- تصنيف ووردبريس `category` غير ظاهر في REST (`/wp-json/wp/v2/categories` → لا يوجد مسار)
- `service_categories`: 14 قسماً وكلها `count = 0` (لم تُربط بالمقالات)
- `cities`: 6 محافظات × 208 مقال = 1248 (مكتمل)
- `salmiya` و`fintas` موجودان في التصنيف والرئيسية لكن **0 مقالات**
- الوسوم على عينة المقالات: فارغة
- ملف CSV المحلي فيه عمود `categories` لم يُسقط على `service_categories`

### 5) وسائط وصور

- المكتبة: **5 ملفات فقط** (شعارات)
- عينة 500/1248 مقال: `featured_media = 0`
- `og:image` للمقالات = صورة ترس عامة من موقع الإمارات: `https://www.rukn-eltatawer.com/wp-content/uploads/icon/setting.png`
- CSV يستخدم صور نسبية مثل `service-65532.webp` غير المرفوعة

### 6) أنواع محتوى فارغة

| النوع | العدد |
|---|---|
| مقالات منشورة | 1248 |
| خدمات CPT | 16 |
| reviews | 0 |
| faqs | 0 |
| pricing | 0 |
| portfolio | 0 |
| before_after | غير متاح عبر REST |

الأسئلة الشائعة في الرئيسية مكتوبة داخل القالب وليست من CPT `faqs`.

### 7) إعدادات SEO/Schema ناقصة للكويت

- Schema يستخدم هاتف إماراتي مع `addressCountry: KW` و`priceRange: KWD` (تضارب دولة/رقم)
- لا إحداثيات كويت (`kayan_seo_latitude` / `longitude`)
- `kayan_seo_locale` يُفضّل `ar_KW` وليس `ar_SA`
- لا رابط Google Business Profile للكويت (`kayan_seo_gbp_url`)
- أعلام Polylang تُحمّل من `http://` غير آمن

### 8) تعارض روابط الخدمات الإنجليزية

`/kw/services/water-leak-detection/` (صفحة خدمة إنجليزية) تُحوّل إلى مقال عربي  
`/kw/water-leak-detection-al-ahmadi/` بسبب تشابه الـ slug مع المقالات.

## ملف CSV في المستودع

`rukn-eltatawer-kuwait-FULL.csv`

- 1248 صف (نفس عدد المقالات المنشورة)
- الحالة كلها `draft` بينما الحيّ `publish`
- `{PHONE_RUKN_KUWAIT}` × 2496 و`{WHATSAPP_RUKN_KUWAIT}` × 2496
- 24 عنواناً مكرراً (1224 عنواناً فريداً)
- لا تعيد استيراد الملف كما هو: سيُنشئ نسخاً مسودة فوق المحتوى المنشور

جهّز نسخة الاستيراد عبر:

```bash
python3 scripts/prepare_kuwait_csv.py
```

## ما يُكمَل بعد نجاح الدخول

1. تعبئة أرقام الهاتف/واتساب في Theme Options وKayan Track (حتى لو بقي +971 مؤقتاً).
2. تشغيل `kayan_show_call_buttons`.
3. حذف/تصحيح سكربتات Code Snippets التي تلصق `tel:+971586634710` مع المتغيّر مرة ثانية.
4. إصلاح slug صفحة EN وتعيين الصفحات الأمامية في Polylang.
5. إصلاح حالة HTTP لـ robots/sitemap (Rank Math + مسار المجلد الفرعي `/kw`).
6. ربط المقالات بـ `service_categories`.
7. صورة مميزة افتراضية للكويت بدل أيقونة الإمارات.
8. عدم إعادة استيراد CSV إلا بعد إزالة التكرار ومطابقة الـ slug.

السكربت `scripts/apply_kuwait_wp_fixes.py` ينفّذ ما يمكن عبر REST/WPVibe بعد توفير بيانات دخول صالحة.
