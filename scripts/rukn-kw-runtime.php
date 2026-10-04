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

add_action('wp_head', 'rukn_kw_head_min', 1);
function rukn_kw_head_min()
{
 $title = wp_get_document_title();
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
 $pairs = rukn_kw_hreflang_pair($path);
 if ($pairs) {
  echo '<link rel="alternate" hreflang="ar" href="' . esc_url($pairs[0]) . '">' . "\n";
  echo '<link rel="alternate" hreflang="en" href="' . esc_url($pairs[1]) . '">' . "\n";
  echo '<link rel="alternate" hreflang="x-default" href="' . esc_url($pairs[0]) . '">' . "\n";
 }
 echo '<style id="rukn-kw-hide-tel">a[href^="tel:"]{display:none!important}</style>' . "\n";
}

function rukn_kw_hreflang_pair($path)
{
 $norm = '/' . trim((string) $path, '/') . '/';
 $norm = preg_replace('~/+~', '/', $norm);
 $ar = 'https://www.rukn-eltatawer.com/kw/';
 $en = 'https://www.rukn-eltatawer.com/kw/en/';
 $map = array(
  '/kw/' => array($ar, $en),
  '/kw/en/' => array($ar, $en),
  '/kw/about-us/' => array($ar . 'about-us/', $en . 'about/'),
  '/kw/en/about/' => array($ar . 'about-us/', $en . 'about/'),
  '/kw/contact-us/' => array($ar . 'contact-us/', $en . 'contact/'),
  '/kw/en/contact/' => array($ar . 'contact-us/', $en . 'contact/'),
  '/kw/privacy-policy/' => array($ar . 'privacy-policy/', $en . 'privacy/'),
  '/kw/en/privacy/' => array($ar . 'privacy-policy/', $en . 'privacy/'),
  '/kw/en/services/' => array($ar, $en . 'services/'),
  '/kw/en/service/' => array($ar, $en),
 );
 return isset($map[$norm]) ? $map[$norm] : ($norm === '/kw/' || strpos($norm, '/kw/en/') === 0 ? array($ar, $en) : null);
}

add_filter('rank_math/frontend/canonical', 'rukn_kw_canonical', 99);
add_filter('get_canonical_url', 'rukn_kw_canonical', 99);
function rukn_kw_canonical($url)
{
 $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
 $path = preg_replace('~/+~', '/', '/' . trim($path, '/') . '/');
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

add_action('template_redirect', 'rukn_kw_redirect_english', 0);
function rukn_kw_redirect_english()
{
 $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
 if (!preg_match('#/kw/english(/|$)#', $path)) {
  return;
 }
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
 $target = home_url('/en/' . ($rest !== '' ? $rest . '/' : ''));
 wp_safe_redirect($target, 301);
 exit;
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
  }
 }
 return $items;
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
 $canon = rukn_kw_canonical('');
 $html = preg_replace(
  '~<link[^>]+rel=["\']canonical["\'][^>]*>~i',
  '<link rel="canonical" href="' . esc_url($canon) . '">',
  $html
 );
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
