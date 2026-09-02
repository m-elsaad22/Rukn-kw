if (!defined('ABSPATH')) {
    return;
}

if (!defined('RUKN_KW_PHONE')) {
    define('RUKN_KW_PHONE', '+971586634710');
    define('RUKN_KW_WA', '971586634710');
    define('RUKN_KW_EMAIL', 'm@rukn-eltatawer.com');
}

if (!defined('RUKN_KW_HOME')) {
    define('RUKN_KW_HOME', home_url('/'));
}

/**
 * Rukn El Tatawer — Kuwait SEO + localization layer.
 * Serves sitemap/robots, unique titles, hreflang, Kuwait copy, and crawler-visible phones.
 */

function rukn_kw_is_en_request()
{
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    return (bool) preg_match('#/kw/en(/|$)#', $path);
}

function rukn_kw_path()
{
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    $path = '/' . trim($path, '/') . '/';
    $path = preg_replace('#/+#', '/', $path);
    return $path;
}

function rukn_kw_hreflang_pair()
{
    $pairs = array(
        '/kw/' => '/kw/en/',
        '/kw/about-us/' => '/kw/en/about-us/',
        '/kw/contact-us/' => '/kw/en/contact-us/',
        '/kw/privacy-policy/' => '/kw/en/privacy-policy/',
        '/kw/en/' => '/kw/',
        '/kw/en/about-us/' => '/kw/about-us/',
        '/kw/en/contact-us/' => '/kw/contact-us/',
        '/kw/en/privacy-policy/' => '/kw/privacy-policy/',
    );
    $path = rukn_kw_path();
    if (isset($pairs[$path])) {
        return array($path, $pairs[$path]);
    }
    return array($path, null);
}

function rukn_kw_abs($path)
{
    return 'https://rukn-eltatawer.com' . $path;
}

add_filter('rewrite_rules_array', 'rukn_kw_drop_theme_en_rules', 99);
function rukn_kw_drop_theme_en_rules($rules)
{
    if (!is_array($rules)) {
        return $rules;
    }
    foreach ($rules as $pattern => $query) {
        if (strpos((string) $query, 'kayan_lang=en') !== false) {
            unset($rules[$pattern]);
        }
    }
    return $rules;
}

add_action('parse_request', 'rukn_kw_force_en_pagename', 99);
function rukn_kw_force_en_pagename($wp)
{
    if (is_admin()) {
        return;
    }
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    if (!preg_match('#^/kw/en(/|$)#', $path)) {
        return;
    }
    $rel = trim((string) preg_replace('#^/kw/en/?#', '', $path), '/');
    $wp->query_vars = array(
        'pagename' => $rel === '' ? 'en' : 'en/' . $rel,
    );
}

add_filter('request', 'rukn_kw_force_en_request', 99);
function rukn_kw_force_en_request($qv)
{
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    if (!preg_match('#^/kw/en(/|$)#', $path)) {
        return $qv;
    }
    $rel = trim((string) preg_replace('#^/kw/en/?#', '', $path), '/');
    return array(
        'pagename' => $rel === '' ? 'en' : 'en/' . $rel,
    );
}

function rukn_kw_seo_context()
{
    $is_en = rukn_kw_is_en_request();
    $title = '';
    $desc = '';
    $type = 'website';
    $canonical = '';

    if (function_exists('is_front_page') && is_front_page() && !is_paged() && !$is_en) {
        $title = 'ركن التطور الكويت | كشف تسربات، عزل، تكييف وصيانة في كل المحافظات';
        $desc = 'شركة ركن التطور للخدمات المنزلية في الكويت: كشف تسربات بدون تكسير، عزل الأسطح، التكييف، السباكة، التنظيف ومكافحة الحشرات في العاصمة وحولي والفروانية والأحمدي والجهراء ومبارك الكبير. معاينة ثم عرض سعر مكتوب بالدينار الكويتي.';
        $canonical = rukn_kw_abs('/kw/');
    } elseif (function_exists('is_singular') && is_singular()) {
        $id = get_queried_object_id();
        $rm_t = get_post_meta($id, 'rank_math_title', true);
        $rm_d = get_post_meta($id, 'rank_math_description', true);
        $post_title = get_the_title($id);
        $excerpt = wp_strip_all_tags(get_the_excerpt($id));
        if (!is_string($excerpt) || $excerpt === '') {
            $excerpt = wp_trim_words(wp_strip_all_tags(get_post_field('post_content', $id)), 32);
        }
        $title = $rm_t ? $rm_t : ($post_title . ' | ركن التطور الكويت');
        $desc = $rm_d ? $rm_d : $excerpt;
        $canonical = get_permalink($id);
        $type = (get_post_type($id) === 'post') ? 'article' : 'website';
        if ($is_en && (!$rm_t || $rm_t === $post_title)) {
            $title = $post_title . ' | Rukn El Tatawer Kuwait';
        }
    } elseif (function_exists('is_category') && is_category()) {
        $term = get_queried_object();
        $title = 'خدمات ' . $term->name . ' في الكويت | ركن التطور';
        $desc = 'دليل خدمات ' . $term->name . ' من ركن التطور في محافظات الكويت الست، مع معاينة وتشخيص قبل التنفيذ وعرض سعر بالدينار الكويتي.';
        $canonical = get_term_link($term);
        if (is_wp_error($canonical)) {
            $canonical = '';
        }
    } elseif (function_exists('is_home') && is_home()) {
        $title = 'مدونة ركن التطور الكويت | نصائح الصيانة والتنظيف والتكييف';
        $desc = 'مقالات عملية عن صيانة المنازل في الكويت: التسربات، العزل، التكييف، التنظيف ومكافحة الحشرات حسب المحافظة.';
        $canonical = rukn_kw_abs('/kw/blog/');
    } else {
        $title = wp_get_document_title();
        $desc = get_bloginfo('description');
        $canonical = home_url(add_query_arg(array(), $GLOBALS['wp']->request));
    }

    $title = html_entity_decode(wp_strip_all_tags((string) $title), ENT_QUOTES, 'UTF-8');
    $desc = html_entity_decode(wp_strip_all_tags((string) $desc), ENT_QUOTES, 'UTF-8');
    $desc = preg_replace('/\s+/u', ' ', $desc);
    if (function_exists('mb_substr')) {
        $desc = mb_substr($desc, 0, 170);
    } else {
        $desc = substr($desc, 0, 170);
    }

    return array(
        'title' => $title,
        'desc' => $desc,
        'type' => $type,
        'canonical' => is_string($canonical) ? $canonical : '',
        'en' => $is_en,
        'image' => 'https://www.rukn-eltatawer.com/wp-content/uploads/icon/setting.png',
    );
}

add_action('init', 'rukn_kw_intercept_crawl_files', 0);
add_action('template_redirect', 'rukn_kw_intercept_crawl_files', 0);
function rukn_kw_intercept_crawl_files()
{
    if (is_admin()) {
        return;
    }
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    // Old English hub slug. Keep a 301 so existing links do not 404.
    if (preg_match('#^/kw/english(/|$)#', $path)) {
        $dest = preg_replace('#/kw/english#', '/kw/en', $path, 1);
        wp_redirect(rukn_kw_abs($dest), 301);
        exit;
    }
    $path = rtrim($path, '/');
    if (preg_match('#/kw/robots\.txt$#', $path)) {
        rukn_kw_output_robots();
    }
    if (preg_match('#/kw/(sitemap_index|sitemap)\.xml$#', $path)) {
        rukn_kw_output_sitemap_index();
    }
    if (preg_match('#/kw/post-sitemap(\d+)?\.xml$#', $path, $m)) {
        rukn_kw_output_post_sitemap(max(1, (int) ($m[1] ?? 1)));
    }
    if (preg_match('#/kw/page-sitemap\.xml$#', $path)) {
        rukn_kw_output_page_sitemap();
    }
    if (preg_match('#/kw/category-sitemap\.xml$#', $path)) {
        rukn_kw_output_category_sitemap();
    }
}

function rukn_kw_xml_header()
{
    status_header(200);
    nocache_headers();
    header('Content-Type: application/xml; charset=UTF-8');
    echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
}

function rukn_kw_output_robots()
{
    status_header(200);
    nocache_headers();
    header('Content-Type: text/plain; charset=UTF-8');
    echo "User-agent: *\n";
    echo "Allow: /\n";
    echo "Disallow: /kw/wp-admin/\n";
    echo "Disallow: /kw/wp-login.php\n";
    echo "Sitemap: https://rukn-eltatawer.com/kw/sitemap_index.xml\n";
    exit;
}

function rukn_kw_output_sitemap_index()
{
    global $wpdb;
    $post_count = (int) $wpdb->get_var("SELECT COUNT(ID) FROM {$wpdb->posts} WHERE post_type='post' AND post_status='publish'");
    $chunks = max(1, (int) ceil($post_count / 200));
    $last_post = $wpdb->get_var("SELECT post_modified_gmt FROM {$wpdb->posts} WHERE post_type='post' AND post_status='publish' ORDER BY post_modified_gmt DESC LIMIT 1");
    $last_page = $wpdb->get_var("SELECT post_modified_gmt FROM {$wpdb->posts} WHERE post_type='page' AND post_status='publish' ORDER BY post_modified_gmt DESC LIMIT 1");
    rukn_kw_xml_header();
    echo '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
    echo '<sitemap><loc>' . esc_url(rukn_kw_abs('/kw/page-sitemap.xml')) . '</loc><lastmod>' . esc_html(mysql2date('c', $last_page ?: current_time('mysql', true), false)) . '</lastmod></sitemap>' . "\n";
    for ($i = 1; $i <= $chunks; $i++) {
        $loc = $i === 1 ? '/kw/post-sitemap.xml' : '/kw/post-sitemap' . $i . '.xml';
        echo '<sitemap><loc>' . esc_url(rukn_kw_abs($loc)) . '</loc><lastmod>' . esc_html(mysql2date('c', $last_post ?: current_time('mysql', true), false)) . '</lastmod></sitemap>' . "\n";
    }
    echo '<sitemap><loc>' . esc_url(rukn_kw_abs('/kw/category-sitemap.xml')) . '</loc><lastmod>' . esc_html(mysql2date('c', $last_post ?: current_time('mysql', true), false)) . '</lastmod></sitemap>' . "\n";
    echo '</sitemapindex>';
    exit;
}

function rukn_kw_urlset_open()
{
    echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' . "\n";
}

function rukn_kw_url_row($loc, $lastmod, $freq = 'weekly', $priority = '0.6', $alternates = array())
{
    echo '<url>';
    echo '<loc>' . esc_url($loc) . '</loc>';
    if ($lastmod) {
        echo '<lastmod>' . esc_html($lastmod) . '</lastmod>';
    }
    echo '<changefreq>' . esc_html($freq) . '</changefreq>';
    echo '<priority>' . esc_html($priority) . '</priority>';
    foreach ($alternates as $lang => $href) {
        echo '<xhtml:link rel="alternate" hreflang="' . esc_attr($lang) . '" href="' . esc_url($href) . '"/>';
    }
    echo "</url>\n";
}

function rukn_kw_output_post_sitemap($page = 1)
{
    global $wpdb;
    $offset = ($page - 1) * 200;
    $rows = $wpdb->get_results($wpdb->prepare(
        "SELECT post_name, post_modified_gmt FROM {$wpdb->posts} WHERE post_type='post' AND post_status='publish' ORDER BY post_modified_gmt DESC LIMIT 200 OFFSET %d",
        $offset
    ));
    rukn_kw_xml_header();
    rukn_kw_urlset_open();
    if (is_array($rows)) {
        foreach ($rows as $row) {
            rukn_kw_url_row(
                rukn_kw_abs('/kw/' . $row->post_name . '/'),
                mysql2date('c', $row->post_modified_gmt, false),
                'weekly',
                '0.7'
            );
        }
    }
    echo '</urlset>';
    exit;
}

function rukn_kw_output_page_sitemap()
{
    global $wpdb;
    $rows = $wpdb->get_results("SELECT ID, post_name, post_parent, post_modified_gmt FROM {$wpdb->posts} WHERE post_type='page' AND post_status='publish' ORDER BY post_parent ASC, ID ASC");
    rukn_kw_xml_header();
    rukn_kw_urlset_open();
    rukn_kw_url_row(rukn_kw_abs('/kw/'), gmdate('c'), 'daily', '1.0', array(
        'ar-KW' => rukn_kw_abs('/kw/'),
        'en-KW' => rukn_kw_abs('/kw/en/'),
        'x-default' => rukn_kw_abs('/kw/'),
    ));
    if (is_array($rows)) {
        foreach ($rows as $row) {
            $permalink = get_permalink((int) $row->ID);
            if (!$permalink) {
                continue;
            }
            $is_en = (bool) preg_match('#/kw/en(/|$)#', $permalink);
            $alts = array();
            $map = array(
                'about-us' => array(rukn_kw_abs('/kw/about-us/'), rukn_kw_abs('/kw/en/about-us/')),
                'contact-us' => array(rukn_kw_abs('/kw/contact-us/'), rukn_kw_abs('/kw/en/contact-us/')),
                'privacy-policy' => array(rukn_kw_abs('/kw/privacy-policy/'), rukn_kw_abs('/kw/en/privacy-policy/')),
                'en' => array(rukn_kw_abs('/kw/'), rukn_kw_abs('/kw/en/')),
            );
            if (isset($map[$row->post_name])) {
                $alts = array(
                    'ar-KW' => $map[$row->post_name][0],
                    'en-KW' => $map[$row->post_name][1],
                    'x-default' => $map[$row->post_name][0],
                );
            }
            rukn_kw_url_row($permalink, mysql2date('c', $row->post_modified_gmt, false), 'weekly', $is_en ? '0.8' : '0.9', $alts);
        }
    }
    echo '</urlset>';
    exit;
}

function rukn_kw_output_category_sitemap()
{
    $terms = get_terms(array('taxonomy' => 'category', 'hide_empty' => true));
    rukn_kw_xml_header();
    rukn_kw_urlset_open();
    if (!is_wp_error($terms)) {
        foreach ($terms as $term) {
            if ((int) $term->term_id === 1) {
                continue;
            }
            $link = get_term_link($term);
            if (is_wp_error($link)) {
                continue;
            }
            rukn_kw_url_row($link, gmdate('c'), 'weekly', '0.5');
        }
    }
    echo '</urlset>';
    exit;
}

add_action('template_redirect', 'rukn_kw_start_buffer', 1);
function rukn_kw_start_buffer()
{
    if (is_admin() || wp_doing_ajax() || (defined('REST_REQUEST') && REST_REQUEST) || is_feed()) {
        return;
    }
    $ctx = rukn_kw_seo_context();
    ob_start(function ($html) use ($ctx) {
        return rukn_kw_filter_html($html, $ctx);
    });
}

function rukn_kw_filter_html($html, $ctx)
{
    if (!is_string($html) || $html === '' || strpos($html, '<html') === false) {
        return $html;
    }

    $phone = RUKN_KW_PHONE;
    $wa = RUKN_KW_WA;
    $wa_href = 'https://wa.me/' . $wa . '?text=' . rawurlencode($ctx['en'] ? 'Hello, I need a home service in Kuwait from Rukn El Tatawer' : 'مرحباً! أريد طلب خدمة من ركن التطور - الكويت');
    $phone_disp = '+971 58 663 4710';

    $html = str_replace(
        array(
            '{PHONE_RUKN_KUWAIT}',
            '{WHATSAPP_RUKN_KUWAIT}',
            '[[رقم الهاتف/واتساب]]',
            '[[عدد المشاريع]]',
            '[[سنة التأسيس]]',
            'اختر الإمارة',
            'خريطة الإمارات',
            'دبي، الإمارات العربية المتحدة',
            'دبي، الإمارات',
            'تغطية 8 مدينة',
        ),
        array(
            $phone,
            $wa,
            $phone_disp,
            '16+',
            '2018',
            'اختر المحافظة',
            'خريطة الكويت',
            'مدينة الكويت، الكويت',
            'مدينة الكويت، الكويت',
            'تغطية 8 مدن',
        ),
        $html
    );

    $html = str_replace('/kw/english/', '/kw/en/', $html);

    $html = preg_replace('#Thank you for reading this post, don\'t forget to subscribe!#i', '', $html);
    $html = preg_replace('#href="tel:"#', 'href="tel:' . $phone . '"', $html);
    $html = preg_replace('#href="https://wa\.me/"#', 'href="' . $wa_href . '"', $html);
    $html = preg_replace('#href="https://wa\.me/\?#', 'href="' . $wa_href . '&', $html);
    $html = preg_replace('#src="https://maps\.google\.com/maps\?q=Dubai,United\+Arab\+Emirates[^"]*"#i', 'src="https://maps.google.com/maps?q=Kuwait+City,Kuwait&amp;z=11&amp;output=embed"', $html);
    $html = preg_replace('#data-count="(\d+)">0#', 'data-count="$1">$1', $html);

    $html = preg_replace_callback('#<script type="application/ld\+json">\s*(\{.*?\})\s*</script>#is', function ($m) {
        $j = json_decode($m[1], true);
        if (!is_array($j)) {
            return $m[0];
        }
        $type = isset($j['@type']) ? $j['@type'] : '';
        $name = isset($j['name']) ? $j['name'] : '';
        $tel = isset($j['telephone']) ? $j['telephone'] : '';
        if ($type === 'LocalBusiness' && ($name === '' || $tel === '')) {
            return '';
        }
        if (isset($j['aggregateRating']) && is_array($j['aggregateRating'])) {
            $rv = $j['aggregateRating']['ratingValue'] ?? '';
            if ($rv === '' || $rv === null) {
                unset($j['aggregateRating']);
                return '<script type="application/ld+json">' . wp_json_encode($j, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>';
            }
        }
        return $m[0];
    }, $html);

    $seen_h1 = false;
    $html = preg_replace_callback('#<h1(\b[^>]*)>(.*?)</h1>#is', function ($m) use (&$seen_h1) {
        if (!$seen_h1) {
            $seen_h1 = true;
            return $m[0];
        }
        return '<h2' . $m[1] . '>' . $m[2] . '</h2>';
    }, $html);

    $lang = $ctx['en'] ? 'en-KW' : 'ar-KW';
    $html = preg_replace('#<html\b[^>]*>#i', '<html lang="' . $lang . '" dir="' . ($ctx['en'] ? 'ltr' : 'rtl') . '">', $html, 1);

    $title = $ctx['title'];
    $desc = $ctx['desc'];
    $canon = $ctx['canonical'];
    $og_type = $ctx['type'];
    $img = $ctx['image'];
    $locale = $ctx['en'] ? 'en_KW' : 'ar_KW';

    if ($title) {
        if (preg_match('#<title\b[^>]*>.*?</title>#is', $html)) {
            $html = preg_replace('#<title\b[^>]*>.*?</title>#is', '<title>' . esc_html($title) . '</title>', $html, 1);
        } else {
            $html = preg_replace('#</head>#i', '<title>' . esc_html($title) . '</title></head>', $html, 1);
        }
    }

    $meta_block = '';
    $meta_block .= '<meta name="description" content="' . esc_attr($desc) . '" />' . "\n";
    $meta_block .= '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />' . "\n";
    $meta_block .= '<meta name="googlebot" content="index, follow" />' . "\n";
    if ($canon) {
        $meta_block .= '<link rel="canonical" href="' . esc_url($canon) . '" />' . "\n";
    }
    $meta_block .= '<link rel="sitemap" type="application/xml" href="' . esc_url(rukn_kw_abs('/kw/sitemap_index.xml')) . '" />' . "\n";

    list($self, $alt) = rukn_kw_hreflang_pair();
    if ($alt) {
        $ar = (strpos($self, '/kw/en/') === 0) ? $alt : $self;
        $en = (strpos($self, '/kw/en/') === 0) ? $self : $alt;
        $meta_block .= '<link rel="alternate" hreflang="ar-KW" href="' . esc_url(rukn_kw_abs($ar)) . '" />' . "\n";
        $meta_block .= '<link rel="alternate" hreflang="en-KW" href="' . esc_url(rukn_kw_abs($en)) . '" />' . "\n";
        $meta_block .= '<link rel="alternate" hreflang="x-default" href="' . esc_url(rukn_kw_abs($ar)) . '" />' . "\n";
    }

    $meta_block .= '<meta property="og:locale" content="' . esc_attr($locale) . '" />' . "\n";
    $meta_block .= '<meta property="og:type" content="' . esc_attr($og_type) . '" />' . "\n";
    $meta_block .= '<meta property="og:site_name" content="' . ($ctx['en'] ? 'Rukn El Tatawer Kuwait' : 'ركن التطور الكويت') . '" />' . "\n";
    $meta_block .= '<meta property="og:title" content="' . esc_attr($title) . '" />' . "\n";
    $meta_block .= '<meta property="og:description" content="' . esc_attr($desc) . '" />' . "\n";
    if ($canon) {
        $meta_block .= '<meta property="og:url" content="' . esc_url($canon) . '" />' . "\n";
    }
    $meta_block .= '<meta property="og:image" content="' . esc_url($img) . '" />' . "\n";
    $meta_block .= '<meta name="twitter:card" content="summary_large_image" />' . "\n";
    $meta_block .= '<meta name="twitter:title" content="' . esc_attr($title) . '" />' . "\n";
    $meta_block .= '<meta name="twitter:description" content="' . esc_attr($desc) . '" />' . "\n";
    $meta_block .= '<meta name="theme-color" content="#0A1F4E" />' . "\n";

    $html = preg_replace('#<meta name="description"[^>]*>#i', '', $html);
    $html = preg_replace('#<meta name=[\'"]robots[\'"][^>]*>#i', '', $html);
    $html = preg_replace('#<link rel=[\'"]canonical[\'"][^>]*>#i', '', $html);
    $html = preg_replace('#<meta property="og:[^"]+"[^>]*>#i', '', $html);
    $html = preg_replace('#<meta name="twitter:[^"]+"[^>]*>#i', '', $html);
    $html = preg_replace('#<link rel="alternate" hreflang="[^"]+"[^>]*>#i', '', $html);

    $html = preg_replace('#</head>#i', $meta_block . '</head>', $html, 1);

    if ($ctx['en']) {
        $en_nav = '<nav class="menu">'
            . '<a href="' . esc_url(rukn_kw_abs('/kw/en/')) . '">Home</a>'
            . '<a href="' . esc_url(rukn_kw_abs('/kw/en/services/')) . '">Services</a>'
            . '<a href="' . esc_url(rukn_kw_abs('/kw/en/about-us/')) . '">About</a>'
            . '<a href="' . esc_url(rukn_kw_abs('/kw/en/contact-us/')) . '">Contact</a>'
            . '<a href="' . esc_url(rukn_kw_abs('/kw/')) . '">العربية</a>'
            . '</nav>';
        $html = preg_replace('#<nav class="menu">.*?</nav>#is', $en_nav, $html, 1);
    } else {
        $html = preg_replace(
            '#(<nav class="menu">)(.*?)(</nav>)#is',
            '$1$2<a href="' . esc_url(rukn_kw_abs('/kw/en/')) . '">English</a>$3',
            $html,
            1
        );
    }

    return $html;
}

add_action('wp_head', function () {
    if (is_admin()) {
        return;
    }
    $is_en = rukn_kw_is_en_request();
    $desc_ar = 'شركة ركن التطور للخدمات المنزلية المتكاملة في الكويت: كشف تسربات المياه، عزل الأسطح، الصيانة العامة، التكييف، التنظيف ومكافحة الحشرات في كل المحافظات.';
    $desc_en = 'Rukn El Tatawer provides home services across Kuwait: leak detection, roof insulation, AC, plumbing, cleaning and pest control in every governorate.';
    echo '<script type="application/ld+json">' . wp_json_encode(array(
        '@context' => 'https://schema.org',
        '@type' => 'HomeAndConstructionBusiness',
        '@id' => RUKN_KW_HOME . '#business',
        'name' => $is_en ? 'Rukn El Tatawer Kuwait' : 'ركن التطور - الكويت',
        'alternateName' => array('Rukn El Tatawer', 'ركن التطور'),
        'description' => $is_en ? $desc_en : $desc_ar,
        'url' => RUKN_KW_HOME,
        'telephone' => RUKN_KW_PHONE,
        'email' => RUKN_KW_EMAIL,
        'image' => 'https://www.rukn-eltatawer.com/wp-content/uploads/icon/setting.png',
        'currenciesAccepted' => 'KWD',
        'paymentAccepted' => 'Cash, KNET',
        'address' => array(
            '@type' => 'PostalAddress',
            'addressLocality' => $is_en ? 'Kuwait City' : 'مدينة الكويت',
            'addressRegion' => $is_en ? 'Al Asimah' : 'العاصمة',
            'addressCountry' => 'KW',
        ),
        'areaServed' => array(
            array('@type' => 'AdministrativeArea', 'name' => $is_en ? 'Kuwait' : 'الكويت'),
            array('@type' => 'AdministrativeArea', 'name' => $is_en ? 'Capital Governorate' : 'محافظة العاصمة'),
            array('@type' => 'AdministrativeArea', 'name' => $is_en ? 'Hawalli Governorate' : 'محافظة حولي'),
            array('@type' => 'AdministrativeArea', 'name' => $is_en ? 'Farwaniya Governorate' : 'محافظة الفروانية'),
            array('@type' => 'AdministrativeArea', 'name' => $is_en ? 'Ahmadi Governorate' : 'محافظة الأحمدي'),
            array('@type' => 'AdministrativeArea', 'name' => $is_en ? 'Jahra Governorate' : 'محافظة الجهراء'),
            array('@type' => 'AdministrativeArea', 'name' => $is_en ? 'Mubarak Al-Kabeer Governorate' : 'محافظة مبارك الكبير'),
        ),
        'openingHoursSpecification' => array(
            '@type' => 'OpeningHoursSpecification',
            'dayOfWeek' => array('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
            'opens' => '00:00',
            'closes' => '23:59',
        ),
        'priceRange' => 'KWD',
        'sameAs' => array('https://wa.me/' . RUKN_KW_WA),
    ), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>' . "\n";
}, 99);

add_action('wp_footer', function () {
    if (is_admin()) {
        return;
    }
    $phone = RUKN_KW_PHONE;
    $wa = RUKN_KW_WA;
    $is_en = rukn_kw_is_en_request();
    $msg = rawurlencode($is_en ? 'Hello, I need a home service in Kuwait from Rukn El Tatawer' : 'مرحباً! أريد طلب خدمة من ركن التطور - الكويت');
    echo '<script>
window.RuknCS = window.RuknCS || {};
window.RuknCS.call_show = true;
window.RuknCS.wa_show = true;
window.RuknCS.call_number = ' . wp_json_encode($phone) . ';
window.RuknCS.wa_number = ' . wp_json_encode($wa) . ';
(function(){
  var phone = ' . wp_json_encode($phone) . ';
  var waHref = "https://wa.me/" + ' . wp_json_encode($wa) . ' + "?text=' . $msg . '";
  function fix(){
    document.querySelectorAll("a[href^=\'tel:\']").forEach(function(a){ a.href="tel:"+phone; });
    document.querySelectorAll("a[href*=\'wa.me\'],a[href*=\'api.whatsapp\']").forEach(function(a){ a.href=waHref; });
    document.querySelectorAll(".fmap-addr-row span").forEach(function(s){
      if(/دبي|الإمارات|Dubai|United Arab/i.test(s.textContent||"")) s.textContent="مدينة الكويت، الكويت";
    });
    document.querySelectorAll(".fmap-frame").forEach(function(f){
      var src=f.getAttribute("src")||"";
      if(/Dubai|United\\+Arab/i.test(src)){
        f.setAttribute("src","https://maps.google.com/maps?q=Kuwait+City,Kuwait&z=11&output=embed");
      }
    });
    document.querySelectorAll("[data-count]").forEach(function(el){
      var n = el.getAttribute("data-count");
      if(n && (el.textContent||"").trim()==="0") el.textContent = n;
    });
  }
  function replacePlaceholders(){
    var map = {
      "[[عدد المشاريع]]": "16+",
      "[[سنة التأسيس]]": "2018",
      "[[رقم الهاتف/واتساب]]": "+971 58 663 4710",
      "اختر الإمارة": "اختر المحافظة"
    };
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
    var node;
    while ((node = walker.nextNode())) {
      var t = node.nodeValue;
      if (!t) continue;
      var next = t;
      Object.keys(map).forEach(function(k){ if (next.indexOf(k) !== -1) next = next.split(k).join(map[k]); });
      if (next !== t) node.nodeValue = next;
    }
  }
  function boot(){ fix(); replacePlaceholders(); }
  if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",boot);}
  else {boot();}
})();
</script>';
}, 99);

add_filter('the_content', function ($content) {
    if (!is_string($content) || $content === '') {
        return $content;
    }
    $content = str_replace(
        array('{PHONE_RUKN_KUWAIT}', '{WHATSAPP_RUKN_KUWAIT}', '[[رقم الهاتف/واتساب]]', 'Thank you for reading this post, don\'t forget to subscribe!'),
        array(RUKN_KW_PHONE, RUKN_KW_WA, '+971 58 663 4710', ''),
        $content
    );
    $icon = 'https://www.rukn-eltatawer.com/wp-content/uploads/icon/cleaning-services.png';
    $content = preg_replace('/src="(service-[^"]+\\.webp)"/i', 'src="' . $icon . '"', $content);
    $content = preg_replace('#<h1(\b[^>]*)>#i', '<h2$1>', $content);
    $content = preg_replace('#</h1>#i', '</h2>', $content);
    return $content;
}, 20);

add_filter('document_title_parts', function ($parts) {
    if (is_front_page() && !rukn_kw_is_en_request()) {
        $parts['title'] = 'ركن التطور الكويت | كشف تسربات، عزل، تكييف وصيانة في كل المحافظات';
        unset($parts['tagline'], $parts['site']);
    }
    return $parts;
}, 99);
