<?php
/**
 * Rukn KW runtime fixpack (WPCode snippet 3811).
 * Marker: RUKN_KW_GSC_FIXPACK 20261020a
 * Live English stays /kw/en/. Canonical host stays www.
 * WhatsApp stays UAE. Call buttons stay hidden.
 */
if (!defined('ABSPATH')) {
    return;
}

add_filter('pll_check_browser_language', '__return_false');
add_filter('pre_option_kayan_currency', 'rukn_kw_kwd');
add_filter('pre_option_currency', 'rukn_kw_kwd');
add_filter('pre_option_kayan_tax_rate', 'rukn_kw_tax0');
function rukn_kw_kwd($v)
{
    return 'KWD';
}
function rukn_kw_tax0($v)
{
    return '0';
}

add_action('init', 'rukn_kw_gsc_oneshot', 0);
add_action('init', 'rukn_kw_robots_txt', 1);
function rukn_kw_robots_txt()
{
    if (is_admin()) {
        return;
    }
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    if (!preg_match('#/kw/robots\.txt/?$#i', $path)) {
        return;
    }
    status_header(200);
    nocache_headers();
    header('Content-Type: text/plain; charset=UTF-8');
    echo "User-agent: *\n";
    echo "Allow: /\n";
    echo "Disallow: /wp-admin/\n";
    echo "Allow: /wp-admin/admin-ajax.php\n\n";
    echo "Sitemap: https://www.rukn-eltatawer.com/kw/sitemap_index.xml\n";
    exit;
}

function rukn_kw_gsc_oneshot()
{
    if (get_option('rukn_kw_gsc_fix_20261020a')) {
        return;
    }
    global $wpdb;
    $deleted = (int) $wpdb->query(
        "DELETE FROM {$wpdb->postmeta} WHERE meta_key='rank_math_title' AND (meta_value LIKE '%01151481000%' OR meta_value LIKE '%الإعلان للإيجار%')"
    );
    $phone_rows = $wpdb->get_results(
        "SELECT post_id, meta_value FROM {$wpdb->postmeta} WHERE meta_key='rank_math_title' AND meta_value LIKE '%0541673020%'"
    );
    $phones = 0;
    if (is_array($phone_rows)) {
        foreach ($phone_rows as $row) {
            $clean = rukn_kw_clean_title((string) $row->meta_value);
            if ($clean === '' || $clean === '%title%') {
                delete_post_meta((int) $row->post_id, 'rank_math_title');
            } else {
                update_post_meta((int) $row->post_id, 'rank_math_title', $clean);
            }
            $phones++;
        }
    }
    $opt = get_option('rank-math-options-sitemap');
    if (is_array($opt)) {
        foreach (array('pt_services_sitemap', 'pt_reviews_sitemap', 'pt_faqs_sitemap', 'pt_pricing_sitemap', 'pt_portfolio_sitemap', 'pt_before_after_sitemap') as $key) {
            $opt[$key] = 'off';
        }
        $opt['include_featured_image'] = 'on';
        update_option('rank-math-options-sitemap', $opt);
    }
    $titles = get_option('rank-math-options-titles');
    if (is_array($titles)) {
        $titles['pt_services_robots'] = array('noindex');
        $titles['pt_services_custom_robots'] = 'on';
        update_option('rank-math-options-titles', $titles);
    }
    update_option(
        'rukn_kw_gsc_fix_20261020a',
        array(
            'deleted_spam_titles' => $deleted,
            'cleaned_phone_titles' => $phones,
            'at' => current_time('mysql'),
        ),
        false
    );
}

function rukn_kw_clean_title($title)
{
    if (!is_string($title) || $title === '') {
        return $title;
    }
    $title = html_entity_decode($title, ENT_QUOTES, 'UTF-8');
    $title = preg_replace('/[📞📢]/u', ' ', $title);
    $title = preg_replace('/0?1151481000/u', ' ', $title);
    $title = preg_replace('/0541673020/u', ' ', $title);
    $title = preg_replace('/الإعلان للإيجار/u', ' ', $title);
    $title = preg_replace('/\s*(?:[|\-–—])\s*$/u', '', $title);
    $title = preg_replace('/\s+/u', ' ', $title);
    return trim((string) $title);
}

add_filter('rank_math/frontend/title', 'rukn_kw_clean_title', 99);
add_filter('pre_get_document_title', 'rukn_kw_clean_title', 99);
add_filter('document_title', 'rukn_kw_clean_title', 99);
add_filter('wp_title', 'rukn_kw_clean_title', 99);

add_action('wp_head', 'rukn_kw_head_min', 1);
function rukn_kw_head_min()
{
    $title = rukn_kw_clean_title(wp_get_document_title());
    $desc = '';
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    $is_en = (bool) preg_match('#/kw/en(/|$)#', $path);
    if (function_exists('is_front_page') && is_front_page() && !is_paged() && !$is_en) {
        $desc = 'شركة ركن التطور للخدمات المنزلية في الكويت: كشف تسربات، عزل، تكييف، سباكة، تنظيف ومكافحة حشرات في كل المحافظات. أسعار بالدينار الكويتي بعد المعاينة. تواصل عبر واتساب.';
    } elseif ($is_en && (preg_match('#/kw/en/?$#', $path) || (function_exists('is_page') && is_page(3819)))) {
        $desc = 'Rukn El Tatawer home services in Kuwait. Quotes in KWD after inspection. WhatsApp the Kuwait desk.';
    } elseif (function_exists('is_singular') && is_singular()) {
        $id = get_queried_object_id();
        $desc = (string) get_post_meta($id, 'rank_math_description', true);
        if ($desc === '') {
            $desc = wp_strip_all_tags((string) get_the_excerpt($id));
        }
    }
    $desc = trim(preg_replace('/\s+/u', ' ', html_entity_decode(wp_strip_all_tags((string) $desc), ENT_QUOTES, 'UTF-8')));
    $desc = rukn_kw_clean_title($desc);
    if (function_exists('mb_substr')) {
        $desc = mb_substr($desc, 0, 160);
    }
    $url = rukn_kw_canonical('');
    echo '<title>' . esc_html($title) . '</title>' . "\n";
    if ($desc !== '') {
        echo '<meta name="description" content="' . esc_attr($desc) . '">' . "\n";
        echo '<meta property="og:description" content="' . esc_attr($desc) . '">' . "\n";
    }
    echo '<meta property="og:title" content="' . esc_attr($title) . '">' . "\n";
    echo '<meta property="og:url" content="' . esc_url($url) . '">' . "\n";
    echo '<link rel="canonical" href="' . esc_url($url) . '">' . "\n";
    echo rukn_kw_hreflang_tags($path);
    echo '<style id="rukn-kw-hide-tel">a[href^="tel:"]{display:none!important}</style>' . "\n";
}

function rukn_kw_hreflang_tags($path)
{
    $norm = rukn_kw_norm_path($path);
    $ar_home = 'https://www.rukn-eltatawer.com/kw/';
    $en_home = 'https://www.rukn-eltatawer.com/kw/en/';
    $pairs = array(
        '/kw/' => array($ar_home, $en_home),
        '/kw/en/' => array($ar_home, $en_home),
        '/kw/about-us/' => array($ar_home . 'about-us/', $en_home . 'about/'),
        '/kw/en/about/' => array($ar_home . 'about-us/', $en_home . 'about/'),
        '/kw/contact-us/' => array($ar_home . 'contact-us/', $en_home . 'contact/'),
        '/kw/en/contact/' => array($ar_home . 'contact-us/', $en_home . 'contact/'),
        '/kw/privacy-policy/' => array($ar_home . 'privacy-policy/', $en_home . 'privacy/'),
        '/kw/en/privacy/' => array($ar_home . 'privacy-policy/', $en_home . 'privacy/'),
    );
    $out = '';
    if (isset($pairs[$norm])) {
        $out .= '<link rel="alternate" hreflang="ar" href="' . esc_url($pairs[$norm][0]) . '">' . "\n";
        $out .= '<link rel="alternate" hreflang="en" href="' . esc_url($pairs[$norm][1]) . '">' . "\n";
        $out .= '<link rel="alternate" hreflang="x-default" href="' . esc_url($pairs[$norm][0]) . '">' . "\n";
        return $out;
    }
    if (strpos($norm, '/kw/en/') === 0) {
        $self = 'https://www.rukn-eltatawer.com' . $norm;
        $out .= '<link rel="alternate" hreflang="en" href="' . esc_url($self) . '">' . "\n";
        $out .= '<link rel="alternate" hreflang="x-default" href="' . esc_url($self) . '">' . "\n";
        return $out;
    }
    return $out;
}

function rukn_kw_norm_path($path)
{
    $norm = '/' . trim((string) $path, '/') . '/';
    return preg_replace('~/+~', '/', $norm);
}

add_filter('rank_math/frontend/canonical', 'rukn_kw_canonical', 99);
add_filter('get_canonical_url', 'rukn_kw_canonical', 99);
function rukn_kw_canonical($url)
{
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    $path = rukn_kw_norm_path($path);
    if (preg_match('#^/kw/en(/|$)#', $path)) {
        return 'https://www.rukn-eltatawer.com' . $path;
    }
    $url = is_string($url) ? $url : '';
    $url = preg_replace('~^https://rukn-eltatawer\.com/kw~', 'https://www.rukn-eltatawer.com/kw', $url);
    if ($url === '' || $url === 'https://www.rukn-eltatawer.com/kw/') {
        return 'https://www.rukn-eltatawer.com' . ($path === '//' ? '/kw/' : $path);
    }
    return $url;
}

function rukn_kw_en_map()
{
    return array(
        '' => 3819,
        'about' => 3821,
        'about-us' => 3821,
        'about-us-2' => 3821,
        'contact' => 3823,
        'contact-us' => 3823,
        'contact-us-2' => 3823,
        'privacy' => 3825,
        'privacy-policy' => 3825,
        'privacy-policy-2' => 3825,
        'service' => 3819,
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
        'service/hawalli' => 3863,
        'service/farwaniya' => 3865,
        'service/ahmadi' => 3867,
        'service/jahra' => 3869,
        'service/mubarak-al-kabeer' => 3871,
    );
}

function rukn_kw_en_canonical_paths()
{
    static $rev = null;
    if ($rev !== null) {
        return $rev;
    }
    $skip = array(
        'about-us',
        'about-us-2',
        'contact-us',
        'contact-us-2',
        'privacy-policy',
        'privacy-policy-2',
        'service',
        'service/privacy-policy',
    );
    $rev = array();
    foreach (rukn_kw_en_map() as $slug => $id) {
        if (in_array($slug, $skip, true) || isset($rev[(int) $id])) {
            continue;
        }
        $rev[(int) $id] = $slug === '' ? '/kw/en/' : '/kw/en/' . $slug . '/';
    }
    $rev[3819] = '/kw/en/';
    $rev[3821] = '/kw/en/about/';
    $rev[3823] = '/kw/en/contact/';
    $rev[3825] = '/kw/en/privacy/';
    $rev[3827] = '/kw/en/services/';
    return $rev;
}

add_filter('page_link', 'rukn_kw_force_en_permalink', 20, 2);
function rukn_kw_force_en_permalink($link, $post_id)
{
    $rev = rukn_kw_en_canonical_paths();
    $id = (int) $post_id;
    if (isset($rev[$id])) {
        return 'https://www.rukn-eltatawer.com' . $rev[$id];
    }
    return $link;
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

add_action('template_redirect', 'rukn_kw_redirects', 0);
function rukn_kw_redirects()
{
    if (is_admin()) {
        return;
    }
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    if (preg_match('#/kw/english(/|$)#', $path)) {
        $rest = trim((string) preg_replace('#^.*?/kw/english/?#', '', $path), '/');
        $map = array(
            'about-us-2' => 'about',
            'about-us' => 'about',
            'contact-us-2' => 'contact',
            'contact-us' => 'contact',
            'privacy-policy-2' => 'privacy',
            'privacy-policy' => 'privacy',
        );
        if (isset($map[$rest])) {
            $rest = $map[$rest];
        }
        wp_safe_redirect(home_url('/en/' . ($rest !== '' ? $rest . '/' : '')), 301);
        exit;
    }
    if (preg_match('#^/kw/services(/|$)#', $path)) {
        wp_safe_redirect(home_url('/'), 301);
        exit;
    }
    if (preg_match('#/kw/en(/|$)#', $path)) {
        $rel = trim((string) preg_replace('#^.*?/kw/en/?#', '', $path), '/');
        $aliases = array(
            'about-us-2' => 'about',
            'about-us' => 'about',
            'contact-us-2' => 'contact',
            'contact-us' => 'contact',
            'privacy-policy-2' => 'privacy',
            'privacy-policy' => 'privacy',
            'service' => '',
            'service/privacy-policy' => 'privacy',
        );
        if (isset($aliases[$rel])) {
            $rest = $aliases[$rel];
            wp_safe_redirect(home_url('/en/' . ($rest !== '' ? $rest . '/' : '')), 301);
            exit;
        }
    }
}

add_filter('wp_get_nav_menu_items', 'rukn_kw_fix_en_menu', 99, 3);
function rukn_kw_fix_en_menu($items, $menu, $args)
{
    if (!is_array($items)) {
        return $items;
    }
    foreach ($items as $item) {
        if (isset($item->title) && $item->title === 'English') {
            $item->url = home_url('/en/');
        }
        if (isset($item->url) && is_string($item->url)) {
            $item->url = str_replace('/kw/english/', '/kw/en/', $item->url);
            $item->url = str_replace('/en/about-us-2/', '/en/about/', $item->url);
            $item->url = str_replace('/en/contact-us-2/', '/en/contact/', $item->url);
            $item->url = str_replace('/en/service/privacy-policy/', '/en/privacy/', $item->url);
        }
    }
    return $items;
}

add_filter('rank_math/sitemap/exclude_post_type', 'rukn_kw_exclude_cpt_sitemaps', 10, 2);
function rukn_kw_exclude_cpt_sitemaps($exclude, $post_type)
{
    if (in_array($post_type, array('services', 'reviews', 'faqs', 'pricing', 'portfolio', 'before_after'), true)) {
        return true;
    }
    return $exclude;
}

add_filter('rank_math/sitemap/entry', 'rukn_kw_sitemap_entry', 10, 2);
function rukn_kw_sitemap_entry($url, $type = '')
{
    if (!is_array($url) || empty($url['loc'])) {
        return $url;
    }
    $path = rukn_kw_norm_path((string) parse_url($url['loc'], PHP_URL_PATH));
    if (preg_match('#^/kw/services(/|$)#', $path)) {
        return false;
    }
    $drop = array(
        '/kw/en/about-us-2/',
        '/kw/en/about-us/',
        '/kw/en/contact-us-2/',
        '/kw/en/contact-us/',
        '/kw/en/privacy-policy-2/',
        '/kw/en/privacy-policy/',
        '/kw/en/service/',
        '/kw/en/service/privacy-policy/',
    );
    if (in_array($path, $drop, true)) {
        return false;
    }
    if (($type === 'post' || $type === 'posts') && ($path === '/kw/' || $path === '/kw/en/')) {
        return false;
    }
    $url['loc'] = preg_replace('~^https://rukn-eltatawer\.com/kw~', 'https://www.rukn-eltatawer.com/kw', $url['loc']);
    return $url;
}

add_action('template_redirect', 'rukn_kw_buffer_glue', 1);
function rukn_kw_buffer_glue()
{
    if (is_admin()) {
        return;
    }
    ob_start('rukn_kw_buffer_glue_cb');
}
function rukn_kw_buffer_glue_cb($html)
{
    if (!is_string($html)) {
        return $html;
    }
    $html = str_replace('m@rukn-eltatawer.comالتغطية', 'm@rukn-eltatawer.com التغطية', $html);
    $html = str_replace('الكويتالبريد', 'الكويت البريد', $html);
    $html = str_replace('/kw/english/', '/kw/en/', $html);
    $html = str_replace('"currency":"AED"', '"currency":"KWD"', $html);
    $html = str_replace("'currency':'AED'", "'currency':'KWD'", $html);
    $html = str_replace('data-currency="AED"', 'data-currency="KWD"', $html);
    $html = str_replace('<small>AED</small>', '<small>KWD</small>', $html);
    $html = str_replace('"taxRate":"5"', '"taxRate":"0"', $html);
    $html = str_replace('"taxRate":5', '"taxRate":0', $html);
    $html = preg_replace('~href="tel:\+971[^"]*"~', 'href="https://wa.me/971586634710"', $html);
    $html = preg_replace('~"telephone"\s*:\s*"\+971[^"]*"~', '"telephone":""', $html);
    $html = preg_replace_callback(
        '~<title>(.*?)</title>~is',
        static function ($m) {
            return '<title>' . esc_html(rukn_kw_clean_title(wp_strip_all_tags($m[1]))) . '</title>';
        },
        $html
    );
    $html = preg_replace_callback(
        '~(<meta[^>]+(?:property|name)=["\'](?:og:title|twitter:title)["\'][^>]+content=["\'])([^"\']*)(["\'])~i',
        static function ($m) {
            return $m[1] . esc_attr(rukn_kw_clean_title($m[2])) . $m[3];
        },
        $html
    );
    $html = preg_replace('~<link[^>]+hreflang=["\'][^"\']+["\'][^>]*>\s*~i', '', $html);
    $canon = rukn_kw_canonical('');
    $html = preg_replace(
        '~<link[^>]+rel=["\']canonical["\'][^>]*>~i',
        '<link rel="canonical" href="' . esc_url($canon) . '">',
        $html
    );
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    $tags = trim(rukn_kw_hreflang_tags($path));
    if ($tags !== '') {
        $html = preg_replace(
            '~(<link rel="canonical"[^>]*>)~i',
            '$1' . "\n" . $tags,
            $html,
            1
        );
    }
    return $html;
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
        if (!empty($item['meta']) && is_array($item['meta'])) {
            foreach ($item['meta'] as $key => $val) {
                update_post_meta($id, $key, $val);
            }
        }
    }
    update_option('rukn_kw_meta_apply', '0', false);
}

add_action('wp_head', 'rukn_kw_article_css', 40);
function rukn_kw_article_css()
{
    if (!function_exists('is_singular') || !is_singular('post')) {
        return;
    }
    echo '<style id="rukn-kw-article">.rukn-wrap{color:#0A1A33;line-height:1.85;font-size:17px}.rukn-hero{background:linear-gradient(135deg,#0A1F4E 0%,#1269eb 70%,#1FB5A3 140%);color:#fff;border-radius:18px;padding:22px 18px;margin:16px 0 22px}.rukn-hero .hero-label{display:inline-block;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25);border-radius:999px;padding:4px 12px;font-size:13px;margin:0 0 10px}.rukn-hero p{color:#f4f7ff;margin:0 0 10px}.rukn-hero-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}.rukn-btn{display:inline-flex;align-items:center;gap:8px;background:#fff;color:#0A1F4E;text-decoration:none;border-radius:12px;padding:11px 16px;font-weight:700;min-height:44px}.rukn-btn-wa{background:#1FB5A3;color:#fff}.rukn-grid{display:grid;grid-template-columns:1fr;gap:12px;margin:14px 0}@media(min-width:720px){.rukn-grid.cols-3{grid-template-columns:1fr 1fr 1fr}.rukn-grid.cols-2{grid-template-columns:1fr 1fr}}.rukn-card,.rukn-step{background:#fff;border:1px solid #d7e3f7;border-radius:16px;padding:16px;box-shadow:0 8px 24px rgba(10,31,78,.06)}.rukn-card>i,.rukn-step .num{color:#1269eb}.rukn-card h3,.rukn-step h3{margin:8px 0 6px;color:#0A1F4E;font-size:18px}.rukn-step{display:flex;gap:12px;align-items:flex-start}.rukn-step .num{min-width:42px;height:42px;border-radius:12px;background:#e8f1ff;display:flex;align-items:center;justify-content:center;font-weight:800}.responsive-table{overflow-x:auto;margin:12px 0 20px;border:1px solid #d7e3f7;border-radius:14px}.responsive-table table{width:100%;border-collapse:collapse;min-width:280px}.responsive-table th{background:#0A1F4E;color:#fff;text-align:right;padding:10px}.responsive-table td{padding:10px;border-top:1px solid #e6eef8}.rukn-cta{background:#0A1F4E;color:#fff;border-radius:18px;padding:20px;margin:22px 0}.rukn-cta h2{color:#fff;margin:8px 0;font-size:22px}.author-box{background:#f4f8ff;border:1px solid #d7e3f7;border-radius:12px;padding:10px 14px;margin:0 0 16px;font-size:14px}</style>';
}
