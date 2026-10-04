add_action("wp_head", function() {
 $title = wp_get_document_title(),
 $desc = get_bloginfo("description"),
 (function_exists("is_singular") && is_singular()) and ($rm = (string) get_post_meta(get_queried_object_id(), "rank_math_description", true)) and $rm !== "" and $desc = $rm,
 echo "<title>".esc_html($title)."</title>\n<meta name=\"description\" content=\"".esc_attr($desc)."\">\n<meta property=\"og:title\" content=\"".esc_attr($title)."\">\n<meta property=\"og:description\" content=\"".esc_attr($desc)."\">\n"
})
