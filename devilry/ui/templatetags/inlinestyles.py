from django.template.defaultfilters import stringfilter
from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
@stringfilter
def emphasize(s):
    return mark_safe(u"<em>%s</em>" % s)

@register.filter
@stringfilter
def strong(s):
    return mark_safe(u"<strong>%s</strong>" % s)

@register.filter
@stringfilter
def big(s):
    return mark_safe(u"<big>%s</big>" % s)
