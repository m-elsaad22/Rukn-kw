<?php
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
        'https://www.rukn-eltatawer.com/kw/en/' => 'https://rukn-eltatawer.com/kw/english/',
        'https://rukn-eltatawer.com/kw/en/' => 'https://rukn-eltatawer.com/kw/english/',
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
        '<h1>portfolio</h1>' => '<h1>أعمالنا</h1>',
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
    return (bool) preg_match('~/kw/english(/|$)~', $path);
}

function rukn_kw_abs($path)
{
    $path = '/' . ltrim((string) $path, '/');
    $path = preg_replace('~/+~', '/', $path);
    return RUKN_KW_ORIGIN . $path;
}

add_filter('wp_get_nav_menu_items', 'rukn_kw_keep_menu_items', 99, 3);
function rukn_kw_keep_menu_items($items, $menu, $args)
{
    if (!empty($items)) {
        foreach ($items as $item) {
            if (isset($item->title) && $item->title === 'English') {
                $item->url = rukn_kw_abs('/kw/english/');
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
        'post_type'        => 'nav_menu_item',
        'posts_per_page'   => -1,
        'orderby'          => 'menu_order',
        'order'            => 'ASC',
        'tax_query'        => array(array(
            'taxonomy' => 'nav_menu',
            'field'    => 'term_id',
            'terms'    => $menu_id,
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
    $en = rukn_kw_abs('/kw/english/');
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    $pairs = array(
        '/kw/' => array($ar, $en),
        '/kw/about-us/' => array(rukn_kw_abs('/kw/about-us/'), rukn_kw_abs('/kw/english/about-us/')),
        '/kw/contact-us/' => array(rukn_kw_abs('/kw/contact-us/'), rukn_kw_abs('/kw/english/contact-us/')),
        '/kw/privacy-policy/' => array(rukn_kw_abs('/kw/privacy-policy/'), rukn_kw_abs('/kw/english/privacy-policy/')),
        '/kw/blog/' => array(rukn_kw_abs('/kw/blog/'), rukn_kw_abs('/kw/english/')),
        '/kw/english/' => array($ar, $en),
        '/kw/english/about-us/' => array(rukn_kw_abs('/kw/about-us/'), rukn_kw_abs('/kw/english/about-us/')),
        '/kw/english/contact-us/' => array(rukn_kw_abs('/kw/contact-us/'), rukn_kw_abs('/kw/english/contact-us/')),
        '/kw/english/privacy-policy/' => array(rukn_kw_abs('/kw/privacy-policy/'), rukn_kw_abs('/kw/english/privacy-policy/')),
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
    $url = str_replace('https://rukn-eltatawer.com/kw/kw/', 'https://rukn-eltatawer.com/kw/', $url);
    $url = str_replace('https://www.rukn-eltatawer.com/kw/kw/', 'https://rukn-eltatawer.com/kw/', $url);
    if (is_front_page() && !is_paged() && !rukn_kw_is_en()) {
        return rukn_kw_abs('/kw/');
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
            'services'  => 'الخدمات',
            'reviews'   => 'تقييمات العملاء',
            'faqs'      => 'الأسئلة الشائعة',
            'pricing'   => 'الأسعار',
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

    if (preg_match('~^/kw/en(?:/|$)~', $path_r) && strpos($path, '/english') === false) {
        $rest = '';
        if (preg_match('~^/kw/en/(.*)$~', $path_r, $m)) {
            $rest = trim($m[1], '/');
        }
        wp_safe_redirect(rukn_kw_abs('/kw/english/' . ($rest !== '' ? $rest . '/' : '')), 301);
        exit;
    }

    if (is_404()) {
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
    $dir  = rukn_kw_is_en() ? 'ltr' : 'rtl';
    echo '<!DOCTYPE html><html lang="' . esc_attr($lang) . '" dir="' . esc_attr($dir) . '"><head>';
    echo '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">';
    echo '<title>' . esc_html($title) . '</title>';
    wp_head();
    echo '<style>
    body{font-family:Cairo,Tahoma,sans-serif;background:#f6f8fb;margin:0;color:#0A1F4E}
    .rk-wrap{max-width:1100px;margin:40px auto;padding:0 16px}
    .rk-card{background:#fff;border-radius:16px;padding:28px;box-shadow:0 8px 30px rgba(10,31,78,.08)}
    .rk-card h1{margin-top:0}
    .rk-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin-top:24px}
    .rk-item{background:#fff;border-radius:14px;padding:18px;text-decoration:none;color:#0A1F4E;box-shadow:0 4px 16px rgba(10,31,78,.07);display:block}
    .rk-item h2{font-size:18px;margin:0 0 8px}
    .rk-item p{margin:0;color:#466;font-size:14px;line-height:1.7}
    .rk-wa{display:inline-block;margin-top:18px;background:#25D366;color:#fff;padding:12px 18px;border-radius:999px;text-decoration:none;font-weight:700}
    .rk-nav a{margin-left:12px}
    </style></head><body class="rukn-kw-shell">';
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
    rukn_kw_shell_start('الصفحة غير موجودة | ركن التطور الكويت');
    echo '<div class="rk-wrap"><div class="rk-card">';
    echo '<h1>الصفحة غير موجودة</h1>';
    echo '<p>الرابط غير صحيح أو نُقل المحتوى. يمكنك العودة للرئيسية أو مراسلتنا عبر واتساب.</p>';
    echo '<p class="rk-nav"><a href="' . esc_url(rukn_kw_abs('/kw/')) . '">الرئيسية</a>';
    echo ' <a href="' . esc_url(rukn_kw_abs('/kw/blog/')) . '">المدونة</a>';
    echo ' <a href="' . esc_url(rukn_kw_abs('/kw/contact-us/')) . '">تواصل</a></p>';
    echo '<a class="rk-wa" href="https://wa.me/' . rawurlencode(RUKN_KW_WA) . '" rel="noopener">واتساب</a>';
    echo '</div></div>';
    rukn_kw_shell_end();
}

function rukn_kw_render_search()
{
    $q = trim((string) get_search_query());
    $title = 'نتائج البحث: ' . $q . ' | ركن التطور الكويت';
    status_header(200);
    rukn_kw_shell_start($title);
    echo '<div class="rk-wrap"><div class="rk-card"><h1>نتائج البحث عن ' . esc_html($q) . '</h1>';
    $query = new WP_Query(array(
        's'              => $q,
        'post_type'      => array('post', 'page', 'services'),
        'post_status'    => 'publish',
        'posts_per_page' => 24,
    ));
    if ($q === '' || !$query->have_posts()) {
        echo '<p>لا توجد نتائج مطابقة. جرّب كلمة أوضح أو تواصل عبر واتساب.</p>';
        echo '<a class="rk-wa" href="https://wa.me/' . rawurlencode(RUKN_KW_WA) . '" rel="noopener">واتساب</a>';
    } else {
        echo '<div class="rk-grid">';
        while ($query->have_posts()) {
            $query->the_post();
            echo '<a class="rk-item" href="' . esc_url(get_permalink()) . '">';
            echo '<h2>' . esc_html(get_the_title()) . '</h2>';
            echo '<p>' . esc_html(wp_trim_words(wp_strip_all_tags(get_the_excerpt() ?: get_the_content()), 24)) . '</p>';
            echo '</a>';
        }
        echo '</div>';
        wp_reset_postdata();
    }
    echo '</div></div>';
    rukn_kw_shell_end();
}

function rukn_kw_render_blog()
{
    status_header(200);
    rukn_kw_shell_start('المدونة | ركن التطور الكويت');
    echo '<div class="rk-wrap"><div class="rk-card"><h1>المدونة</h1>';
    echo '<p>مقالات ونصائح عملية لخدمات المنزل في الكويت.</p></div>';
    $paged = max(1, (int) get_query_var('paged'), (int) get_query_var('page'));
    $query = new WP_Query(array(
        'post_type'      => 'post',
        'post_status'    => 'publish',
        'posts_per_page' => 12,
        'paged'          => $paged,
    ));
    echo '<div class="rk-grid">';
    while ($query->have_posts()) {
        $query->the_post();
        echo '<a class="rk-item" href="' . esc_url(get_permalink()) . '">';
        echo '<h2>' . esc_html(get_the_title()) . '</h2>';
        echo '<p>' . esc_html(wp_trim_words(wp_strip_all_tags(get_the_excerpt() ?: get_the_content()), 22)) . '</p>';
        echo '</a>';
    }
    echo '</div>';
    echo '<div class="rk-wrap" style="padding:24px 0">';
    echo paginate_links(array(
        'total'   => $query->max_num_pages,
        'current' => $paged,
    ));
    echo '</div>';
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
    echo "\n<!-- rukn-kw-fixpack-20260923b -->\n";
}

add_action('wp_head', 'rukn_kw_hide_call_css', 99);
function rukn_kw_hide_call_css()
{
    echo '<style id="rukn-kw-hide-call">
    a[href^="tel:"],
    a[href*="tel:+971"],
    .btn-call, .call-btn, .rukn-call, [data-rukn-call],
    .fcontact a[href^="tel:"], header a[href^="tel:"],
    a.phone, .phone-btn, .header-call, .footer-call { display:none !important; }
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
    $html = preg_replace('~<root(\s|>)~i', '<div$1', $html);
    $html = preg_replace('~</root>~i', '</div>', $html);
    $html = preg_replace('~<script type="application/ld\+json">\{[^{}]*"@type": "LocalBusiness"[^<]*\}</script>~s', '', $html);
    $html = preg_replace('~href="tel:[^"]+"~', 'href="#rukn-no-call"', $html);
    $html = preg_replace('~\+971[\s\-]*58[\s\-]*663[\s\-]*4710~', '', $html);
    $html = preg_replace('~\+971586634710~', '', $html);
    $nav = '<nav class="menu"><a href="' . esc_url(rukn_kw_abs('/kw/')) . '">الرئيسية</a><a href="' . esc_url(rukn_kw_abs('/kw/about-us/')) . '">من نحن</a><a href="' . esc_url(rukn_kw_abs('/kw/contact-us/')) . '">اتصل بنا</a><a href="' . esc_url(rukn_kw_abs('/kw/blog/')) . '">المدونة</a><a href="' . esc_url(rukn_kw_abs('/kw/english/')) . '">English</a></nav>';
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
