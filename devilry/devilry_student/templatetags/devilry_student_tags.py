from django import template
from django.template.loader import render_to_string
from django.template.defaultfilters import stringfilter
from django.utils.translation import gettext_lazy

register = template.Library()


@register.simple_tag
def devilry_student_shortgrade(feedback):
    """
    Takes a :class:`devilry.apps.models.StaticFeedback` and renders it as a
    short oneliner that includes the grade and information about if the grade is
    passed or failed.

    Handles the grades ``Passed`` and ``Failed`` as synonyms for
    ``is_passing_grade``, so we only render a translation of ``Passed`` or
    ``Failed``, instead of both ``is_passing_grade`` and ``Grade``. This avoids
    ugly strings like: ``Passed (Passed)``.
    """
    return render_to_string('devilry_student/devilry_student_shortgrade_tag.django.html', {
        'feedback': feedback
    })


@register.filter(name='devilry_humanize_groupstatus')
@stringfilter
def devilry_humanize_groupstatus(status):
    if status == 'waiting-for-feedback':
        return gettext_lazy("Waiting for feedback")
    elif status == 'waiting-for-deliveries':
        return gettext_lazy("Waiting for deliveries or for deadline to expire")
    elif status == 'no-deadlines':
        return gettext_lazy("No deadlines")
    elif status == 'corrected':
        return gettext_lazy("Corrected")
    elif status == 'closed-without-feedback':
        return gettext_lazy("Closed without feedback")
    return status
