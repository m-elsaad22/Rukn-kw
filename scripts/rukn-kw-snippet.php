if (!defined('ABSPATH')) { return; }

if (!defined('RUKN_KW_PHONE')) {
    define('RUKN_KW_PHONE', '+971586634710');
    define('RUKN_KW_WA', '971586634710');
    define('RUKN_KW_EMAIL', 'm@rukn-eltatawer.com');
}

add_action('wp_head', function () {
    if (is_admin()) { return; }
    $desc = 'شركة ركن التطور للخدمات المنزلية المتكاملة في الكويت: كشف تسربات المياه، عزل الأسطح، الصيانة العامة، التكييف، التنظيف ومكافحة الحشرات في كل المحافظات.';
    echo '<script type="application/ld+json">' . wp_json_encode(array(
        '@context' => 'https://schema.org',
        '@type' => 'HomeAndConstructionBusiness',
        'name' => 'ركن التطور - الكويت',
        'description' => $desc,
        'url' => home_url('/'),
        'telephone' => RUKN_KW_PHONE,
        'email' => RUKN_KW_EMAIL,
        'image' => 'https://www.rukn-eltatawer.com/wp-content/uploads/icon/setting.png',
        'address' => array(
            '@type' => 'PostalAddress',
            'addressLocality' => 'مدينة الكويت',
            'addressRegion' => 'العاصمة',
            'addressCountry' => 'KW',
        ),
        'areaServed' => array('الكويت', 'العاصمة', 'حولي', 'الفروانية', 'الأحمدي', 'الجهراء', 'مبارك الكبير'),
        'openingHours' => 'Mo-Su 00:00-23:59',
        'priceRange' => 'KWD',
        'sameAs' => array('https://wa.me/' . RUKN_KW_WA),
    ), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>' . "\n";
}, 99);

add_action('wp_footer', function () {
    if (is_admin()) { return; }
    $phone = RUKN_KW_PHONE;
    $wa = RUKN_KW_WA;
    $msg = rawurlencode('مرحباً! أريد طلب خدمة من ركن التطور - الكويت');
    echo '<script>
window.RuknCS = window.RuknCS || {};
window.RuknCS.call_show = true;
window.RuknCS.wa_show = true;
window.RuknCS.call_number = ' . json_encode($phone) . ';
window.RuknCS.wa_number = ' . json_encode($wa) . ';
window.RuknCS.wa_message = "مرحباً! أريد طلب خدمة من ركن التطور - الكويت";
(function(){
  var phone = ' . json_encode($phone) . ';
  var waHref = "https://wa.me/" + ' . json_encode($wa) . ' + "?text=' . $msg . '";
  function fix(){
    document.querySelectorAll("a[href^=\'tel:\']").forEach(function(a){ a.href="tel:"+phone; });
    document.querySelectorAll("a[href*=\'wa.me\'],a[href*=\'api.whatsapp\']").forEach(function(a){ a.href=waHref; });
    document.querySelectorAll(".fmap-addr-row span").forEach(function(s){
      if(/دبي|الإمارات|Dubai/i.test(s.textContent||"")) s.textContent="مدينة الكويت، الكويت";
    });
    document.querySelectorAll(".fmap-frame").forEach(function(f){
      var src=f.getAttribute("src")||"";
      if(/Dubai|United\\+Arab/i.test(src)){
        f.setAttribute("src","https://maps.google.com/maps?q=Kuwait+City,Kuwait&z=11&output=embed");
      }
    });
  }
  function replacePlaceholders(){
    var map = {
      "[[عدد المشاريع]]": "16+",
      "[[سنة التأسيس]]": "2026",
      "[[رقم الهاتف/واتساب]]": "+971 58 663 4710"
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
        array('{PHONE_RUKN_KUWAIT}', '{WHATSAPP_RUKN_KUWAIT}', '[[رقم الهاتف/واتساب]]'),
        array(RUKN_KW_PHONE, RUKN_KW_WA, '+971 58 663 4710'),
        $content
    );
    $icon = 'https://www.rukn-eltatawer.com/wp-content/uploads/icon/cleaning-services.png';
    $content = preg_replace('/src="(service-[^"]+\\.webp)"/i', 'src="' . $icon . '"', $content);
    return $content;
}, 20);
