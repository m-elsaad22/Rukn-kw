/**
 * Rukn KW runtime fixpack (WPCode snippet 3811).
 * WhatsApp stays UAE. Call buttons and published phone numbers stay hidden
 * until a Kuwait +965 line exists.
 */
if (!defined('ABSPATH')) {
 return;
}

if (!defined('RUKN_KW_WA')) {
 define('RUKN_KW_WA', '971586634710');
}
if (!defined('RUKN_KW_EMAIL')) {
 define('RUKN_KW_EMAIL', 'm@rukn-eltatawer.com');
}
if (!defined('RUKN_KW_ORIGIN')) {
 define('RUKN_KW_ORIGIN', 'https://rukn-eltatawer.com');
}

add_action('admin_init', static function () {
 global $pagenow;
 if ($pagenow === 'edit-comments.php') {
 wp_safe_redirect(admin_url());
 exit;
 }
 remove_meta_box('dashboard_recent_comments', 'dashboard', 'normal');
 foreach (get_post_types() as $post_type) {
 if (post_type_supports($post_type, 'comments')) {
 remove_post_type_support($post_type, 'comments');
 remove_post_type_support($post_type, 'trackbacks');
 }
 }
});
add_filter('comments_open', '__return_false', 20, 2);
add_filter('pings_open', '__return_false', 20, 2);
add_filter('comments_array', '__return_empty_array', 10, 2);
add_action('admin_menu', static function () {
 remove_menu_page('edit-comments.php');
});
add_action('init', static function () {
 if (is_admin_bar_showing()) {
 remove_action('admin_bar_menu', 'wp_admin_bar_comments_menu', 60);
 }
});

add_filter('pre_option_phonenumber', 'rukn_kw_empty_phone', 10, 1);
add_filter('pre_option_contact_number', 'rukn_kw_empty_phone', 10, 1);
add_filter('pre_option_kayan_country_kw_phone', 'rukn_kw_empty_phone', 10, 1);
add_filter('pre_option_kayan_show_call_buttons', 'rukn_kw_empty_phone', 10, 1);
add_filter('pre_option_rukn_hide_call_global', static function ($v) {
 return 'on';
}, 10, 1);
add_filter('pre_option_whatsapp_number', static function ($v) {
 return RUKN_KW_WA;
}, 10, 1);
add_filter('pre_option_kayan_currency', static function ($v) {
 return 'KWD';
}, 10, 1);
add_filter('pre_option_currency', static function ($v) {
 return 'KWD';
}, 10, 1);
add_filter('pre_option_kayan_tax_rate', static function ($v) {
 return '0';
}, 10, 1);
add_filter('pre_option_footer__map_embed', 'rukn_kw_kuwait_map', 10, 1);
add_filter('pre_option_company__map_code', 'rukn_kw_kuwait_map', 10, 1);
add_filter('option_HomeIntro', 'rukn_kw_filter_homeintro', 20);
add_filter('get_post_metadata', 'rukn_kw_filter_widget_meta', 20, 4);

function rukn_kw_empty_phone($v)
{
 return '';
}

function rukn_kw_uae_replacements()
{
 static $map = null;
 if ($map !== null) {
 return $map;
 }
 $logo = 'https://rukn-eltatawer.com/kw/wp-content/uploads/2026/09/logo.webp';
 $map = array(
 'https://rukn-eltatawer.com/kw/kw/' => 'https://rukn-eltatawer.com/kw/',
 'https://www.rukn-eltatawer.com/kw/kw/' => 'https://rukn-eltatawer.com/kw/',
 'https://www.rukn-eltatawer.com/kw/' => 'https://rukn-eltatawer.com/kw/',
 'https://www.rukn-eltatawer.com/wp-content/uploads/icon/setting.png' => $logo,
 'https://rukn-eltatawer.com/wp-content/uploads/icon/setting.png' => $logo,
 'اختر الإمارة' => 'اختر المحافظة',
 'خريطة الإمارات الكحلية' => 'خريطة الكويت',
 'في جميع أنحاء الإمارات' => 'في جميع أنحاء الكويت',
 'جميع إمارات الدولة السبع بلا استثناء' => 'جميع محافظات الكويت بلا استثناء',
 'إمارات الدولة السبع' => 'محافظات الكويت الست',
 'سجل حافل في السوق الإماراتي' => 'سجل حافل في السوق الكويتي',
 'في مختلف إمارات الإمارات' => 'في مختلف محافظات الكويت',
 'خدماتنا في جميع {%إمارات الدولة%}' => 'خدماتنا في جميع {%محافظات الكويت%}',
 'أينما كنت في الإمارات' => 'أينما كنت في الكويت',
 'تغطية كاملة لـ 7 إمارات' => 'تغطية كاملة لـ 6 محافظات',
 'فريق محلي في كل إمارة' => 'فريق محلي في كل محافظة',
 'المعايير المعتمدة في دولة الإمارات' => 'المعايير المعتمدة في دولة الكويت',
 'رقم تسجيل ضريبي (VAT) رسمي وفواتير نظامية' => 'فواتير واضحة بالدينار الكويتي بعد المعاينة',
 'maps.google.com/maps?q=Dubai,United+Arab+Emirates' => 'maps.google.com/maps?q=Kuwait+City,Kuwait',
 'دبي، الإمارات العربية المتحدة' => 'مدينة الكويت، الكويت',
 'فيلا — دبي مارينا' => 'فيلا — مدينة الكويت',
 'فيلا — البرشاء' => 'فيلا — حولي',
 'مبنى — الشارقة' => 'مبنى — الفروانية',
 'class="uae-svg"' => 'class="kw-svg"',
 "class='uae-svg'" => "class='kw-svg'",
 '.uae-svg' => '.kw-svg',
 '"currency":"AED"' => '"currency":"KWD"',
 "'currency':'AED'" => "'currency':'KWD'",
 'data-currency="AED"' => 'data-currency="KWD"',
 "data-currency='AED'" => "data-currency='KWD'",
 '<small>AED</small>' => '<small>KWD</small>',
 '"taxRate":"5"' => '"taxRate":"0"',
 "'taxRate':'5'" => "'taxRate':'0'",
 '"taxRate":5' => '"taxRate":0',
 'http://rukn-eltatawer.com/' => 'https://rukn-eltatawer.com/',
 '[[عدد المشاريع]]' => '540+',
 '[[سنة التأسيس]]' => '2015',
 '<h1>services</h1>' => '<h1>الخدمات</h1>',
 '<h1>reviews</h1>' => '<h1>تقييمات العملاء</h1>',
 '<h1>faqs</h1>' => '<h1>الأسئلة الشائعة</h1>',
 '<h1>pricing</h1>' => '<h1>الأسعار</h1>',
 'تغطية 8 مدينة' => 'تغطية محافظات الكويت',
 '8 مدينة' => '6 محافظات',
 '8 مدن' => '6 محافظات',
 '>Toggle<' => '>المحتويات<',
 );
 return $map;
}

function rukn_kw_scrub_uae_copy($value)
{
 if (is_array($value)) {
 foreach ($value as $key => $item) {
 $value[$key] = rukn_kw_scrub_uae_copy($item);
 }
 return $value;
 }
 if (!is_string($value) || $value === '') {
 return $value;
 }
 $value = strtr($value, rukn_kw_uae_replacements());
 $value = preg_replace('~(https://(?:www\.)?rukn-eltatawer\.com)?/kw/english(/|$)~', '$1/kw/en$2', $value);
 $value = str_replace('/kw/en/blog/', '/kw/en/', $value);
 $value = str_replace('/kw/en/about-us-2/', '/kw/en/about-us/', $value);
 $value = str_replace('/kw/en/contact-us-2/', '/kw/en/contact-us/', $value);
 $value = str_replace('m@rukn-eltatawer.comالتغطية', 'm@rukn-eltatawer.com التغطية', $value);
 $value = str_replace('m@rukn-eltatawer.comال', 'm@rukn-eltatawer.com ال', $value);
 $value = str_replace('دبي مارينا', 'مدينة الكويت', $value);
 if ($value === 'البرشاء') {
 $value = 'حولي';
 }
 if ($value === 'الشارقة') {
 $value = 'الفروانية';
 }
 if ($value === '7 إمارات') {
 $value = '6 محافظات';
 }
 return $value;
}

function rukn_kw_kuwait_map_svg()
{
 return '<svg class="kw-svg" viewBox="0 0 300 220" aria-hidden="true"><path d="M52 78 L162 44 L196 50 L208 78 L172 94 C164 108 166 122 186 132 L230 152 L214 196 L160 208 L88 190 L48 150 L42 110 Z"/><path d="M198 56 L228 48 L236 66 L214 74 Z"/></svg>';
}

function rukn_kw_replace_uae_map($html)
{
 $html = preg_replace(
 '~<svg class="(?:uae|kw)-svg"[^>]*>\s*<path d="M40,70[^"]*"\s*/>\s*</svg>~s',
 rukn_kw_kuwait_map_svg(),
 $html
 );
 return $html;
}

function rukn_kw_replace_parent_icons($html)
{
 $map = array(
 'search.png' => 'fas fa-magnifying-glass',
 'location1.png' => 'fas fa-location-dot',
 'setting.png' => 'fas fa-screwdriver-wrench',
 'price.png' => 'fas fa-file-invoice-dollar',
 'water-leak-detection.png' => 'fas fa-droplet',
 'insulation-services.png' => 'fas fa-layer-group',
 'electrical-appliance-repair.png' => 'fas fa-snowflake',
 'cleaning-services.png' => 'fas fa-spray-can-sparkles',
 'pest-control.png' => 'fas fa-bug-slash',
 'plumbing-services.png' => 'fas fa-wrench',
 'building-maintenance.png' => 'fas fa-helmet-safety',
 'landscaping-services.png' => 'fas fa-tree',
 'decoration-services.png' => 'fas fa-paint-roller',
 'skilled-technicians.png' => 'fas fa-user-gear',
 'whatsapp.png' => 'fab fa-whatsapp',
 'tab.png' => 'fas fa-briefcase',
 'lifetime-warranty.png' => 'fas fa-shield-halved',
 'fast-response.png' => 'fas fa-bolt',
 );
 return preg_replace_callback(
 '~<img([^>]+)src=["\']https://(?:www\.)?rukn-eltatawer\.com/wp-content/uploads/icon/([^"\']+)["\'][^>]*>~i',
 static function ($m) use ($map) {
 $file = strtolower(basename($m[2]));
 $fa = isset($map[$file]) ? $map[$file] : 'fas fa-circle-check';
 return '<i class="' . $fa . '" aria-hidden="true"></i>';
 },
 $html
 );
}

function rukn_kw_filter_homeintro($value)
{
 $value = rukn_kw_scrub_uae_copy($value);
 if (is_array($value) && isset($value['slider_intro_v1']) && is_array($value['slider_intro_v1'])) {
 $value['slider_intro_v1']['hide_call_button'] = 'on';
 }
 return $value;
}

function rukn_kw_filter_widget_meta($check, $object_id, $meta_key, $single)
{
 if ($check !== null || $meta_key !== 'widget_post_meta') {
 return $check;
 }
 remove_filter('get_post_metadata', 'rukn_kw_filter_widget_meta', 20);
 $raw = get_post_meta($object_id, $meta_key, false);
 add_filter('get_post_metadata', 'rukn_kw_filter_widget_meta', 20, 4);
 return rukn_kw_scrub_uae_copy($raw);
}

function rukn_kw_kuwait_map($v)
{
 return 'https://maps.google.com/maps?q=Kuwait+City,Kuwait&z=11&output=embed';
}

function rukn_kw_is_en()
{
 $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
 return (bool) preg_match('~/kw/(en|english)(/|$)~', $path);
}

function rukn_kw_abs($path)
{
 $path = '/' . ltrim((string) $path, '/');
 $path = preg_replace('~/+~', '/', $path);
 if (preg_match('~^/kw(/|$)~', $path)) {
 $path = preg_replace('~^/kw~', '', $path);
 if ($path === '') {
 $path = '/';
 }
 }
 return set_url_scheme(home_url($path), 'https');
}

add_filter('allowed_redirect_hosts', static function ($hosts) {
 $hosts[] = 'rukn-eltatawer.com';
 $hosts[] = 'www.rukn-eltatawer.com';
 return array_values(array_unique($hosts));
});

add_filter('wp_get_nav_menu_items', 'rukn_kw_keep_menu_items', 99, 3);
function rukn_kw_keep_menu_items($items, $menu, $args)
{
 if (!empty($items)) {
 foreach ($items as $item) {
 if (isset($item->title) && $item->title === 'English') {
 $item->url = rukn_kw_abs('/kw/en/');
 }
 }
 return $items;
 }
 $menu_id = 0;
 if (is_object($menu) && isset($menu->term_id)) {
 $menu_id = (int) $menu->term_id;
 } elseif (is_numeric($menu)) {
 $menu_id = (int) $menu;
 }
 if (!$menu_id) {
 return $items;
 }
 $raw = get_posts(array(
 'post_type' => 'nav_menu_item',
 'posts_per_page' => -1,
 'orderby' => 'menu_order',
 'order' => 'ASC',
 'tax_query' => array(array(
 'taxonomy' => 'nav_menu',
 'field' => 'term_id',
 'terms' => $menu_id,
 )),
 'suppress_filters' => true,
 ));
 if (empty($raw)) {
 return $items;
 }
 $built = array();
 foreach ($raw as $post) {
 $built[] = wp_setup_nav_menu_item($post);
 }
 return $built;
}

add_filter('pll_check_browser_language', '__return_false');
add_filter('pll_rel_hreflang_attributes', 'rukn_kw_hreflang', 20);
function rukn_kw_hreflang($hreflangs)
{
 $ar = rukn_kw_abs('/kw/');
 $en = rukn_kw_abs('/kw/en/');
 $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
 $pairs = array(
 '/kw/' => array($ar, $en),
 '/kw/about-us/' => array(rukn_kw_abs('/kw/about-us/'), rukn_kw_abs('/kw/en/about-us/')),
 '/kw/contact-us/' => array(rukn_kw_abs('/kw/contact-us/'), rukn_kw_abs('/kw/en/contact-us/')),
 '/kw/privacy-policy/' => array(rukn_kw_abs('/kw/privacy-policy/'), rukn_kw_abs('/kw/en/privacy-policy/')),
 '/kw/blog/' => array(rukn_kw_abs('/kw/blog/'), $en),
 '/kw/en/' => array($ar, $en),
 '/kw/en/about-us/' => array(rukn_kw_abs('/kw/about-us/'), rukn_kw_abs('/kw/en/about-us/')),
 '/kw/en/contact-us/' => array(rukn_kw_abs('/kw/contact-us/'), rukn_kw_abs('/kw/en/contact-us/')),
 '/kw/en/privacy-policy/' => array(rukn_kw_abs('/kw/privacy-policy/'), rukn_kw_abs('/kw/en/privacy-policy/')),
 '/kw/en/services/' => array($ar, rukn_kw_abs('/kw/en/services/')),
 '/kw/en/service/' => array($ar, $en),
 );
 $norm = '/' . trim($path, '/') . '/';
 $norm = preg_replace('~/+~', '/', $norm);
 if (isset($pairs[$norm])) {
 return array('ar' => $pairs[$norm][0], 'en' => $pairs[$norm][1], 'x-default' => $pairs[$norm][0]);
 }
 return array('ar' => $ar, 'en' => $en, 'x-default' => $ar);
}

add_filter('rank_math/frontend/canonical', 'rukn_kw_canonical', 99);
add_filter('get_canonical_url', 'rukn_kw_canonical', 99);
function rukn_kw_canonical($url)
{
 $url = is_string($url) ? $url : '';
 $url = str_replace('https://rukn-eltatawer.com/kw/kw/', 'https://www.rukn-eltatawer.com/kw/', $url);
 $url = str_replace('https://www.rukn-eltatawer.com/kw/kw/', 'https://www.rukn-eltatawer.com/kw/', $url);
 $url = preg_replace('~^https://rukn-eltatawer\.com/kw~', 'https://www.rukn-eltatawer.com/kw', $url);
 $url = str_replace('/kw/english/', '/kw/en/', $url);
 if (is_front_page() && !is_paged() && !rukn_kw_is_en()) {
 return 'https://www.rukn-eltatawer.com/kw/';
 }
 return $url;
}

add_filter('pre_get_document_title', 'rukn_kw_document_title', 99);
add_filter('rank_math/frontend/title', 'rukn_kw_document_title', 99);
function rukn_kw_document_title($title)
{
 if (is_front_page() && !is_paged() && !rukn_kw_is_en()) {
 return 'ركن التطور الكويت | كشف تسربات، عزل، تكييف وصيانة في كل المحافظات';
 }
 if (is_page('contact-us')) {
 return rukn_kw_is_en()
 ? 'Contact via WhatsApp | Rukn El Tatawer Kuwait'
 : 'تواصل عبر واتساب | ركن التطور الكويت';
 }
 if (is_page('about-us')) {
 return rukn_kw_is_en()
 ? 'About us | Rukn El Tatawer Kuwait'
 : 'من نحن | ركن التطور الكويت';
 }
 if (rukn_kw_is_en() && is_page()) {
 return get_the_title() . ' | Rukn El Tatawer Kuwait';
 }
 if (is_post_type_archive()) {
 $labels = array(
 'services' => 'الخدمات',
 'reviews' => 'تقييمات العملاء',
 'faqs' => 'الأسئلة الشائعة',
 'pricing' => 'الأسعار',
 'portfolio' => 'أعمالنا',
 );
 $pt = get_query_var('post_type');
 if (is_array($pt)) {
 $pt = reset($pt);
 }
 if (isset($labels[$pt])) {
 return $labels[$pt] . ' | ركن التطور الكويت';
 }
 }
 if (is_search()) {
 return 'نتائج البحث: ' . get_search_query() . ' | ركن التطور الكويت';
 }
 if (is_404()) {
 return 'الصفحة غير موجودة | ركن التطور الكويت';
 }
 return $title;
}

add_filter('rank_math/frontend/description', 'rukn_kw_description', 99);
function rukn_kw_description($desc)
{
 if (is_front_page() && !is_paged() && !rukn_kw_is_en()) {
 return 'شركة ركن التطور للخدمات المنزلية في الكويت: كشف تسربات، عزل، تكييف، سباكة، تنظيف ومكافحة حشرات في كل المحافظات. أسعار بالدينار الكويتي بعد المعاينة. تواصل عبر واتساب.';
 }
 return $desc;
}

add_filter('rank_math/json_ld', 'rukn_kw_jsonld', 99, 2);
function rukn_kw_jsonld($data, $jsonld)
{
 if (!is_array($data)) {
 return $data;
 }
 foreach ($data as $key => $node) {
 if (!is_array($node)) {
 continue;
 }
 foreach (array('telephone', 'phone', 'phoneNumber') as $phone_key) {
 if (isset($node[$phone_key])) {
 unset($data[$key][$phone_key]);
 }
 }
 }
 return $data;
}

add_action('template_redirect', 'rukn_kw_early_routes', -200);
function rukn_kw_early_routes()
{
 if (is_admin()) {
 return;
 }
 rukn_kw_buffer_start();
 $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
 $path_r = rtrim($path, '/');

 if (preg_match('~/kw/robots\.txt$~', $path_r)) {
 status_header(200);
 nocache_headers();
 header('Content-Type: text/plain; charset=UTF-8');
 echo "User-agent: *\nAllow: /\nDisallow: /wp-admin/\nAllow: /wp-admin/admin-ajax.php\n\n";
 echo "Sitemap: https://rukn-eltatawer.com/kw/sitemap_index.xml\n";
 exit;
 }

 if (preg_match('~/kw/english(?:/|$)~', $path)) {
 $rest = '';
 if (preg_match('~/kw/english/(.*)$~', $path_r, $m)) {
 $rest = trim($m[2], '/');
 }
 $map = array(
 'about-us-2' => 'about-us',
 'contact-us-2' => 'contact-us',
 );
 if (isset($map[$rest])) {
 $rest = $map[$rest];
 }
 wp_safe_redirect(rukn_kw_abs('/kw/en/' . ($rest !== '' ? $rest . '/' : '')), 301);
 exit;
 }

 if (preg_match('~/kw/en/?$~', $path_r)) {
 rukn_kw_serve_page(3819);
 return;
 }

 if (is_404()) {
 if (rukn_kw_try_en_page($path_r)) {
 return;
 }
 rukn_kw_render_404();
 exit;
 }

 if (is_search()) {
 rukn_kw_render_search();
 exit;
 }

 if (is_page(1282) || is_page('blog')) {
 rukn_kw_render_blog();
 exit;
 }
}

function rukn_kw_shell_start($title)
{
 $lang = rukn_kw_is_en() ? 'en' : 'ar';
 $dir = rukn_kw_is_en() ? 'ltr' : 'rtl';
 $home = esc_url(rukn_kw_abs('/kw/'));
 $about = esc_url(rukn_kw_abs('/kw/about-us/'));
 $contact = esc_url(rukn_kw_abs('/kw/contact-us/'));
 $blog = esc_url(rukn_kw_abs('/kw/blog/'));
 $en = esc_url(rukn_kw_abs('/kw/en/'));
 $wa = 'https://wa.me/' . rawurlencode(RUKN_KW_WA);
 echo '<!DOCTYPE html><html lang="' . esc_attr($lang) . '" dir="' . esc_attr($dir) . '"><head>';
 echo '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">';
 echo '<title>' . esc_html($title) . '</title>';
 wp_head();
 echo '<style id="rukn-kw-design-shell">
 :root{--navy:#0A1F4E;--turq:#2E9DF7;--aqua:#4FA8FF;--gold:#C9A227;--gold2:#F0CE73;--wa:#25D366;--bg:#F4F8FD;--text:#1C2E44;--text2:#3A5068;--border:#E2EAF5;--r-m:24px;--sh-l:0 24px 60px rgba(10,31,78,.16);--grad:linear-gradient(135deg,#0A1F4E 0%,#1A3A6B 45%,#2E9DF7 100%);--grad-cta:linear-gradient(135deg,#2980D4,#2E9DF7)}
 body.rukn-kw-shell{font-family:Cairo,Tajawal,Tahoma,sans-serif;background:var(--bg);margin:0;color:var(--text);line-height:1.7}
 .rk-hdr{background:var(--grad);color:#fff;padding:18px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
 .rk-hdr a{color:#fff;text-decoration:none;font-weight:700}
 .rk-hdr nav{display:flex;gap:14px;flex-wrap:wrap}
 .rk-hdr .btn-wa{background:var(--wa);padding:10px 16px;border-radius:12px}
 .phero{padding:48px 24px 36px;background:var(--grad);color:#fff}
 .phero h1{margin:0;color:#fff;font-size:clamp(28px,4vw,42px)}
 .phero .psub{color:rgba(255,255,255,.86);margin-top:12px;max-width:720px}
 .phero .crumb a{color:#fff}
 .sec{padding:48px 24px}
 .wrap{max-width:1400px;margin:0 auto}
 .blog-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:26px}
 .bcard{background:#fff;border:1px solid var(--border);border-radius:var(--r-m);overflow:hidden;text-decoration:none;color:inherit;display:block;transition:.3s}
 .bcard:hover{transform:translateY(-8px);box-shadow:var(--sh-l)}
 .bcard .bimg{height:140px;background:var(--grad);display:grid;place-items:center;color:#fff;font-size:32px}
 .bcard .bbody{padding:22px}
 .bcard h3{margin:0 0 8px;font-size:18px;color:var(--navy)}
 .bcard p{margin:0;color:var(--text2);font-size:14px}
 .bcard .bread{display:inline-flex;margin-top:12px;color:var(--turq);font-weight:700}
 .pager{display:flex;justify-content:center;gap:8px;margin-top:36px;flex-wrap:wrap}
 .err-wrap{min-height:70vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:80px 24px;background:var(--grad);color:#fff}
 .err-num{font-weight:900;font-size:clamp(90px,16vw,160px);line-height:1;background:linear-gradient(120deg,#fff,var(--aqua));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
 .err-wrap h2{color:#fff;margin:10px 0 14px}
 .err-wrap p{color:rgba(255,255,255,.82);max-width:520px;margin:0 auto 30px}
 .err-actions{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
 .err-actions a,.err-links a{color:#fff}
 .btn{display:inline-flex;align-items:center;gap:8px;padding:14px 22px;border-radius:14px;font-weight:700;text-decoration:none}
 .btn-quote{background:linear-gradient(120deg,var(--gold),var(--gold2));color:#0A1F4E}
 .btn-wa{background:var(--wa);color:#fff}
 .err-links{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-top:28px}
 </style></head><body class="rukn-kw-shell">';
 echo '<header class="rk-hdr"><a href="' . $home . '">ركن التطور الكويت</a><nav>';
 echo '<a href="' . $home . '">الرئيسية</a><a href="' . $about . '">من نحن</a><a href="' . $contact . '">تواصل</a><a href="' . $blog . '">المدونة</a><a href="' . $en . '">English</a>';
 echo '</nav><a class="btn-wa" href="' . esc_url($wa) . '" rel="noopener">واتساب</a></header>';
}

function rukn_kw_shell_end()
{
 wp_footer();
 echo '</body></html>';
}

function rukn_kw_render_404()
{
 status_header(404);
 nocache_headers();
 $en = rukn_kw_is_en();
 rukn_kw_shell_start($en ? 'Page not found | Rukn El Tatawer Kuwait' : 'الصفحة غير موجودة | ركن التطور الكويت');
 $home = esc_url($en ? rukn_kw_abs('/kw/en/') : rukn_kw_abs('/kw/'));
 $blog = esc_url(rukn_kw_abs('/kw/blog/'));
 $contact = esc_url($en ? rukn_kw_abs('/kw/en/contact-us/') : rukn_kw_abs('/kw/contact-us/'));
 $wa = 'https://wa.me/' . rawurlencode(RUKN_KW_WA);
 echo '<section class="err-wrap"><div class="wrap">';
 echo '<div class="err-num">404</div>';
 if ($en) {
 echo '<h2>This page is not available</h2>';
 echo '<p>The link is wrong or the page moved. Go back home or message us on WhatsApp.</p>';
 echo '<div class="err-actions"><a class="btn btn-quote" href="' . $home . '">Home</a>';
 echo '<a class="btn btn-wa" href="' . esc_url($wa) . '" rel="noopener">WhatsApp</a></div>';
 echo '<div class="err-links"><a href="' . $home . '">Home</a><a href="' . $contact . '">Contact</a></div>';
 } else {
 echo '<h2>عذراً، هذه الصفحة غير موجودة</h2>';
 echo '<p>الرابط غير صحيح أو نُقل المحتوى. يمكنك العودة للرئيسية أو مراسلتنا عبر واتساب.</p>';
 echo '<div class="err-actions"><a class="btn btn-quote" href="' . $home . '">العودة للرئيسية</a>';
 echo '<a class="btn btn-wa" href="' . esc_url($wa) . '" rel="noopener">واتساب</a></div>';
 echo '<div class="err-links"><a href="' . $home . '">الرئيسية</a><a href="' . $blog . '">المدونة</a><a href="' . $contact . '">تواصل</a></div>';
 }
 echo '</div></section>';
 rukn_kw_shell_end();
}

function rukn_kw_render_search()
{
 $q = trim((string) get_search_query());
 $title = 'نتائج البحث: ' . $q . ' | ركن التطور الكويت';
 status_header(200);
 rukn_kw_shell_start($title);
 echo '<section class="phero compact"><div class="wrap"><h1>نتائج البحث عن ' . esc_html($q) . '</h1>';
 echo '<p class="psub">مقالات وصفحات ركن التطور الكويت.</p></div></section><section class="sec"><div class="wrap">';
 $query = new WP_Query(array(
 's' => $q,
 'post_type' => array('post', 'page', 'services'),
 'post_status' => 'publish',
 'posts_per_page' => 24,
 ));
 if ($q === '' || !$query->have_posts()) {
 echo '<p>لا توجد نتائج مطابقة. جرّب كلمة أوضح أو تواصل عبر واتساب.</p>';
 echo '<a class="btn btn-wa" href="https://wa.me/' . rawurlencode(RUKN_KW_WA) . '" rel="noopener">واتساب</a>';
 } else {
 echo '<div class="blog-grid">';
 while ($query->have_posts()) {
 $query->the_post();
 echo '<a class="bcard" href="' . esc_url(get_permalink()) . '">';
 echo '<div class="bimg"><i class="fas fa-magnifying-glass"></i></div><div class="bbody">';
 echo '<h3>' . esc_html(get_the_title()) . '</h3>';
 echo '<p>' . esc_html(wp_trim_words(wp_strip_all_tags(get_the_excerpt() ?: get_the_content()), 24)) . '</p>';
 echo '<span class="bread">اقرأ المزيد</span></div></a>';
 }
 echo '</div>';
 wp_reset_postdata();
 }
 echo '</div></section>';
 rukn_kw_shell_end();
}

function rukn_kw_render_blog()
{
 status_header(200);
 rukn_kw_shell_start('المدونة | ركن التطور الكويت');
 echo '<section class="phero compact"><div class="wrap">';
 echo '<div class="crumb"><a href="' . esc_url(rukn_kw_abs('/kw/')) . '">الرئيسية</a> / المدونة</div>';
 echo '<h1>مدونة ركن التطور — نصائح لخدمات المنزل في الكويت</h1>';
 echo '<p class="psub">مقالات ونصائح عملية لخدمات المنزل في محافظات الكويت.</p></div></section>';
 $paged = max(1, (int) get_query_var('paged'), (int) get_query_var('page'));
 $query = new WP_Query(array(
 'post_type' => 'post',
 'post_status' => 'publish',
 'posts_per_page' => 12,
 'paged' => $paged,
 ));
 echo '<section class="sec"><div class="wrap"><div class="blog-grid">';
 $first = true;
 while ($query->have_posts()) {
 $query->the_post();
 $feat = $first ? ' featured' : '';
 $first = false;
 echo '<a class="bcard' . $feat . '" href="' . esc_url(get_permalink()) . '">';
 echo '<div class="bimg"><i class="fas fa-book-open"></i></div><div class="bbody">';
 echo '<h3>' . esc_html(get_the_title()) . '</h3>';
 echo '<p>' . esc_html(wp_trim_words(wp_strip_all_tags(get_the_excerpt() ?: get_the_content()), 22)) . '</p>';
 echo '<span class="bread">اقرأ المزيد</span></div></a>';
 }
 echo '</div><div class="pager">';
 echo paginate_links(array(
 'total' => $query->max_num_pages,
 'current' => $paged,
 ));
 echo '</div></div></section>';
 wp_reset_postdata();
 rukn_kw_shell_end();
}

add_filter('language_attributes', 'rukn_kw_language_attributes', 20);
function rukn_kw_language_attributes($out)
{
 if (rukn_kw_is_en()) {
 return 'lang="en" dir="ltr"';
 }
 return 'lang="ar" dir="rtl"';
}

add_action('wp_head', 'rukn_kw_head_meta', 1);
function rukn_kw_head_meta()
{
 echo "\n<!-- rukn-kw-fixpack-20261004 -->\n";
 rukn_kw_print_social_meta();
}

add_action('wp_head', 'rukn_kw_hide_call_css', 99);
function rukn_kw_hide_call_css()
{
 echo '<style id="rukn-kw-hide-call">
 a[href^="tel:"],
 a[href*="tel:+971"],
 a[href="#rukn-no-call"],
 .btn-call, .call-btn, .rukn-call, [data-rukn-call],
 .fab-call, .fab-btn.fab-call, .header-call, .footer-call,
 .fcontact a[href^="tel:"], header a[href^="tel:"],
 a.phone, .phone-btn { display:none !important; }
 .kw-svg{width:100%;max-width:340px}
 .kw-svg path{fill:rgba(255,255,255,.10);stroke:#4FA8FF;stroke-width:2.5}
 </style>';
}

add_action('template_redirect', 'rukn_kw_buffer_start', -10);
function rukn_kw_buffer_start()
{
 if (is_admin() || wp_doing_ajax()) {
 return;
 }
 static $started = false;
 if ($started) {
 return;
 }
 $started = true;
 ob_start('rukn_kw_buffer_filter');
}

function rukn_kw_buffer_filter($html)
{
 if (!is_string($html) || $html === '') {
 return $html;
 }
 $html = rukn_kw_scrub_uae_copy($html);
 $html = rukn_kw_replace_parent_icons($html);
 $html = rukn_kw_replace_uae_map($html);
 $html = str_replace(' rel="nofollow noopener noreferrer" rel="noopener"', ' rel="nofollow noopener noreferrer"', $html);
 $html = preg_replace('~<root(\s|>)~i', '<div$1', $html);
 $html = preg_replace('~</root>~i', '</div>', $html);
 $html = preg_replace('~<script type="application/ld\+json">\{[^{}]*"@type": "LocalBusiness"[^<]*\}</script>~s', '', $html);
 $html = preg_replace('~href="tel:[^"]+"~', 'href="#rukn-no-call"', $html);
 $html = preg_replace('~\+971[\s\-]*58[\s\-]*663[\s\-]*4710~', '', $html);
 $html = preg_replace('~\+971586634710~', '', $html);
 $nav = '<nav class="menu"><a href="' . esc_url(rukn_kw_abs('/kw/')) . '">الرئيسية</a><a href="' . esc_url(rukn_kw_abs('/kw/about-us/')) . '">من نحن</a><a href="' . esc_url(rukn_kw_abs('/kw/contact-us/')) . '">اتصل بنا</a><a href="' . esc_url(rukn_kw_abs('/kw/blog/')) . '">المدونة</a><a href="' . esc_url(rukn_kw_abs('/kw/en/')) . '">English</a></nav>';
 $html = str_replace('<nav class="menu"></nav>', $nav, $html);
 if (rukn_kw_is_en()) {
 $html = preg_replace('~<html lang="ar" dir="rtl">~', '<html lang="en" dir="ltr">', $html, 1);
 $html = str_replace('og:locale" content="ar_AR"', 'og:locale" content="en_GB"', $html);
 }
 $page_title = esc_html(wp_get_document_title());
 if (preg_match('~<title>[^<]*</title>~i', $html)) {
 $html = preg_replace('~<title>[^<]*</title>~i', '<title>' . $page_title . '</title>', $html, 1);
 } else {
 $html = preg_replace('~</head>~i', '<title>' . $page_title . '</title></head>', $html, 1);
 }
 return $html;
}

add_action('wp_footer', 'rukn_kw_contact_form_js', 50);
function rukn_kw_contact_form_js()
{
 if (!is_page('contact-us')) {
 return;
 }
 $wa = wp_json_encode('https://wa.me/' . RUKN_KW_WA);
 echo '<script>
 document.addEventListener("DOMContentLoaded",function(){
 if(document.getElementById("rukn-kw-wa-form")) return;
 var box=document.querySelector("article")||document.querySelector(".--primary--intro--pages")||document.querySelector("main")||document.querySelector(".standard-page")||document.body;
 var f=document.createElement("form");
 f.id="rukn-kw-wa-form";
 f.style.cssText="max-width:640px;margin:32px auto;padding:20px;background:#fff;border-radius:16px;display:flex;flex-direction:column;gap:10px;position:relative;z-index:1;box-shadow:0 8px 30px rgba(10,31,78,.08)";
 f.innerHTML="<h2>طلب عبر واتساب</h2><input name=\\"name\\" required placeholder=\\"الاسم\\" style=\\"padding:10px\\"><input name=\\"area\\" placeholder=\\"المحافظة / المنطقة\\" style=\\"padding:10px\\"><input name=\\"service\\" placeholder=\\"الخدمة المطلوبة\\" style=\\"padding:10px\\"><textarea name=\\"msg\\" rows=\\"4\\" placeholder=\\"وصف المشكلة\\" style=\\"padding:10px\\"></textarea><button type=\\"submit\\" style=\\"padding:12px;background:#25D366;color:#fff;border:0;border-radius:10px;font-weight:700\\">إرسال واتساب</button><p>لا يظهر رقم اتصال حالياً. نستخدم واتساب حتى يصدر خط كويتي.</p>";
 f.addEventListener("submit",function(e){
 e.preventDefault();
 var t="طلب من موقع الكويت\\nالاسم: "+f.name.value+"\\nالمنطقة: "+f.area.value+"\\nالخدمة: "+f.service.value+"\\n"+f.msg.value;
 window.open(' . $wa . '+"?text="+encodeURIComponent(t),"_blank");
 });
 box.appendChild(f);
 });
 </script>';
}

function rukn_kw_en_map()
{
 return array(
  '' => 3819,
  'service' => 3819,
  'about-us' => 3821,
  'about-us-2' => 3821,
  'contact-us' => 3823,
  'contact-us-2' => 3823,
  'privacy-policy' => 3825,
  'service/privacy-policy' => 3825,
  'services' => 3827,
  'services/water-leak-detection' => 3829,
  'services/roof-insulation' => 3831,
  'services/waterproofing' => 3833,
  'services/general-maintenance' => 3835,
  'services/building-maintenance' => 3837,
  'services/plumbing' => 3839,
  'services/drain-cleaning' => 3841,
  'services/electrical' => 3843,
  'services/ac-maintenance' => 3845,
  'services/cleaning' => 3847,
  'services/pest-control' => 3849,
  'services/landscaping' => 3851,
  'services/swimming-pools' => 3853,
  'services/painting' => 3855,
  'services/gypsum-board' => 3857,
  'services/interior-design' => 3859,
  'service/kuwait-city' => 3861,
  'kuwait-city' => 3861,
  'service/hawalli' => 3863,
  'hawalli' => 3863,
  'service/farwaniya' => 3865,
  'farwaniya' => 3865,
  'service/ahmadi' => 3867,
  'ahmadi' => 3867,
  'service/jahra' => 3869,
  'jahra' => 3869,
  'service/mubarak-al-kabeer' => 3871,
  'mubarak-al-kabeer' => 3871,
 );
}

add_action('parse_request', 'rukn_kw_parse_en', 1);
function rukn_kw_parse_en($wp)
{
 if (is_admin()) {
  return;
 }
 $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
 if (!preg_match('#/kw/en(/|$)#', $path)) {
  return;
 }
 $rel = trim((string) preg_replace('#^.*?/kw/en/?#', '', $path), '/');
 $map = rukn_kw_en_map();
 if (isset($map[$rel])) {
  $wp->query_vars = array('page_id' => (int) $map[$rel]);
 }
}

function rukn_kw_serve_page($id)
{
 $post = get_post((int) $id);
 if (!$post || $post->post_status !== 'publish') {
  return false;
 }
 global $wp_query;
 $wp_query = new WP_Query(array('page_id' => (int) $id));
 status_header(200);
 return true;
}

function rukn_kw_try_en_page($path_r)
{
 $rel = trim((string) preg_replace('#^.*?/kw/en/?#', '', $path_r), '/');
 $map = rukn_kw_en_map();
 if (!isset($map[$rel])) {
  return false;
 }
 return rukn_kw_serve_page($map[$rel]);
}

function rukn_kw_print_social_meta()
{
 if (is_admin()) {
  return;
 }
 $title = wp_get_document_title();
 $desc = '';
 if (is_front_page() && !rukn_kw_is_en()) {
  $desc = 'شركة ركن التطور للخدمات المنزلية في الكويت: كشف تسربات، عزل، تكييف، سباكة، تنظيف ومكافحة حشرات في كل المحافظات. أسعار بالدينار الكويتي بعد المعاينة. تواصل عبر واتساب.';
 } elseif (rukn_kw_is_en() && (is_front_page() || is_page(3819))) {
  $desc = 'Rukn El Tatawer home services in Kuwait: leak detection, insulation, AC, plumbing, cleaning and pest control across all governorates. Quotes in KWD after inspection. WhatsApp the Kuwait desk.';
 } elseif (is_singular()) {
  $id = get_queried_object_id();
  $desc = (string) get_post_meta($id, 'rank_math_description', true);
  if ($desc === '') {
   $desc = wp_strip_all_tags(get_the_excerpt($id));
  }
  if ($desc === '') {
   $desc = wp_trim_words(wp_strip_all_tags(get_post_field('post_content', $id)), 28);
  }
 }
 $desc = html_entity_decode(wp_strip_all_tags((string) $desc), ENT_QUOTES, 'UTF-8');
 $desc = trim(preg_replace('/\s+/u', ' ', $desc));
 if (function_exists('mb_substr')) {
  $desc = mb_substr($desc, 0, 160);
 } else {
  $desc = substr($desc, 0, 160);
 }
 $url = rukn_kw_canonical(home_url(add_query_arg(array(), $GLOBALS['wp']->request ?? '')));
 echo '<meta name="description" content="' . esc_attr($desc) . '">' . "\n";
 echo '<meta property="og:title" content="' . esc_attr($title) . '">' . "\n";
 echo '<meta property="og:description" content="' . esc_attr($desc) . '">' . "\n";
 echo '<meta property="og:url" content="' . esc_url($url) . '">' . "\n";
 echo '<meta property="og:type" content="' . (is_singular('post') ? 'article' : 'website') . '">' . "\n";
 echo '<meta name="twitter:card" content="summary_large_image">' . "\n";
}

add_action('wp_head', 'rukn_kw_article_css', 40);
function rukn_kw_article_css()
{
 if (!is_singular('post')) {
  return;
 }
 echo '<style id="rukn-kw-article">
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
</style>';
}

add_action('init', 'rukn_kw_apply_meta_queue', 20);
function rukn_kw_apply_meta_queue()
{
 $raw = get_option('rukn_kw_meta_apply');
 if (empty($raw) || $raw === '0' || $raw === 0) {
  return;
 }
 $json = is_string($raw) ? base64_decode($raw, true) : false;
 if ($json === false && is_string($raw)) {
  $json = $raw;
 }
 $payload = json_decode((string) $json, true);
 if (!is_array($payload) || empty($payload['items'])) {
  update_option('rukn_kw_meta_apply', '0', false);
  return;
 }
 foreach ($payload['items'] as $item) {
  $id = isset($item['id']) ? (int) $item['id'] : 0;
  if ($id < 1) {
   continue;
  }
  if (!empty($item['excerpt'])) {
   wp_update_post(array('ID' => $id, 'post_excerpt' => $item['excerpt']));
  }
  if (!empty($item['rank_math_description'])) {
   update_post_meta($id, 'rank_math_description', $item['rank_math_description']);
  }
  if (!empty($item['rank_math_focus_keyword'])) {
   update_post_meta($id, 'rank_math_focus_keyword', $item['rank_math_focus_keyword']);
  }
  if (!empty($item['rank_math_title'])) {
   update_post_meta($id, 'rank_math_title', $item['rank_math_title']);
  }
  if (!empty($item['meta']) && is_array($item['meta'])) {
   foreach ($item['meta'] as $key => $val) {
    update_post_meta($id, $key, $val);
   }
  }
  if (!empty($item['tags']) && is_array($item['tags'])) {
   wp_set_post_tags($id, $item['tags'], false);
  }
 }
 update_option('rukn_kw_meta_apply', '0', false);
}

add_filter('the_content', 'rukn_kw_strip_leaked_css', 1);
function rukn_kw_strip_leaked_css($content)
{
 if (!is_string($content) || strpos($content, '.rukn-wrap{') === false) {
  return $content;
 }
 return preg_replace('~<p>\s*\.rukn-wrap\{.*?</p>~s', '', $content, 1);
}