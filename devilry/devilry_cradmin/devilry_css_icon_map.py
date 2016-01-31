from django_cradmin import css_icon_map


FONT_AWESOME = css_icon_map.FONT_AWESOME.copy()
FONT_AWESOME.update({
    'devilry-breadcrumb-suffix': 'fa fa-angle-right',
    'devilry-pageheader-back': 'fa fa-angle-left',
    'devilry-link-forward': 'fa fa-angle-right',
})
