from django.template.defaultfilters import stringfilter
from django import template
from django.utils.safestring import mark_safe

from ..templatetags_helpers import truncate_filename


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

@register.filter
@stringfilter
def trunc_filename(filename, length):
    """ Trunkcate a ``filename`` to the given ``length``.  """
    return truncate_filename(filename, length)

@register.filter
def student_status(group_or_delivery):
    """ Returns the localized status for a student of a assignmentgroup or
    delivery wrapped in a span with the appropriate css class. """
    return mark_safe(u"<span class='%s'>%s</span>" % (
        group_or_delivery.get_status_student_cssclass(),
        group_or_delivery.get_localized_student_status()))

@register.filter
def status(group_or_delivery):
    """ Returns the localized status for a examiner or admin of a
    assignmentgroup or delivery wrapped in a span with the appropriate css
    class. """
    return mark_safe(u"<span class='%s'>%s</span>" % (
        group_or_delivery.get_status_cssclass(),
        group_or_delivery.get_localized_status()))
