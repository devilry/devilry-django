from docutils.writers import html4css1
from docutils.core import publish_parts

from django.template.defaultfilters import stringfilter
from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
@stringfilter
def rst_to_html(rst):
    """
    Works just like the 'restructuredtext'-filter, but adds 'title' and
    'subtitle' from input, so they are ignored in output.
    """
    # Add a title and subtitle to prevent the restructuredtext filter
    # from making the first two heading into title and subtitle
    rst = ":::::\nTITLE\n:::::\nSUBTITLE\n:::::::::::\n" + rst

    parts = publish_parts(rst, writer=html4css1.Writer(),
            settings_overrides={})
    #print parts['html_title']
    #print parts['html_subtitle']
    return mark_safe(parts["fragment"])
rst_to_html.needs_autoescape = False
