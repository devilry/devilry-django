try:
    import django.forms.renderers  # noqa
except ImportError:
    _has_template_based_form_rendering = False
else:
    _has_template_based_form_rendering = True


def has_template_based_form_rendering():
    return _has_template_based_form_rendering
