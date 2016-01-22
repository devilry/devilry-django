from django_cradmin import css_icon_map


FONT_AWESOME = css_icon_map.FONT_AWESOME.copy()
FONT_AWESOME.update({
    'devilry-breadcrumb-suffix': 'fa fa-chevron-right',
    'devilry-pageheader-back': 'fa fa-chevron-left',
})
