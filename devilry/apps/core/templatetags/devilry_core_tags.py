import bleach
from django import template
from django.utils.translation import ugettext_lazy as _
from devilry.utils import datetimeutils

register = template.Library()


@register.filter
def devilry_user_displayname(user):
    if not user:
        return ''
    return user.get_full_name()


@register.filter
def format_is_passing_grade(is_passing_grade):
    if is_passing_grade:
        return _('passed')
    else:
        return _('failed')


@register.filter
def devilry_feedback_shortformat(staticfeedback):
    if not staticfeedback:
        return ''
    if staticfeedback.grade in ('Passed', 'Failed'):
        return staticfeedback.grade
    else:
        return u'{} ({})'.format(
            staticfeedback.grade,
            format_is_passing_grade(staticfeedback.is_passing_grade))


@register.filter
def devilry_escape_html(html):
    """
    Escape all html in the given ``html``.
    """
    return bleach.clean(html)


@register.filter
def devilry_isoformat_datetime(datetimeobject):
    """
    Isoformat the given ``datetimeobject`` as ``YYYY-MM-DD hh:mm``.
    """
    return datetimeutils.isoformat_noseconds(datetimeobject)


@register.inclusion_tag('devilry_core/templatetags/single-candidate-long-displayname.django.html')
def devilry_single_candidate_long_displayname(assignment, candidate, devilryrole):
    """
    Returns the candidate wrapped in HTML formatting tags perfect for showing
    the user inline in a verbose manner.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.assignment.Assignment` object.
            The ``assignment`` should be the assignment where the candidate belongs.
        candidate: A :class:`devilry.apps.core.models.candidate.Candidate` object.
        devilryrole: See
            :meth:`devilry.apps.core.models.assignment.Assignment.students_must_be_anonymized_for_devilryrole`.
    """
    return {
        'candidate': candidate,
        'anonymous': assignment.students_must_be_anonymized_for_devilryrole(
            devilryrole=devilryrole)
    }


@register.inclusion_tag('devilry_core/templatetags/single-candidate-short-displayname.django.html')
def devilry_single_candidate_short_displayname(assignment, candidate, devilryrole):
    """
    Returns the candidate wrapped in HTML formatting tags perfect for showing
    the user inline in a non-verbose manner.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.assignment.Assignment` object.
            The ``assignment`` should be the assignment where the candidate belongs.
        candidate: A :class:`devilry.apps.core.models.candidate.Candidate` object.
        devilryrole: See
            :meth:`devilry.apps.core.models.assignment.Assignment.students_must_be_anonymized_for_devilryrole`.
    """
    return {
        'candidate': candidate,
        'anonymous': assignment.students_must_be_anonymized_for_devilryrole(
            devilryrole=devilryrole)
    }


@register.inclusion_tag('devilry_core/templatetags/single-examiner-long-displayname.django.html')
def devilry_single_examiner_long_displayname(assignment, examiner, devilryrole):
    """
    Returns the examiner wrapped in HTML formatting tags perfect for showing
    the user inline in a verbose manner.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.assignment.Assignment` object.
            The ``assignment`` should be the assignment where the examiner belongs.
        examiner: A :class:`devilry.apps.core.models.examiner.Examiner` object.
        devilryrole: See
            :meth:`devilry.apps.core.models.assignment.Assignment.examiners_must_be_anonymized_for_devilryrole`.
    """
    return {
        'examiner': examiner,
        'anonymous': assignment.examiners_must_be_anonymized_for_devilryrole(
            devilryrole=devilryrole)
    }


@register.inclusion_tag('devilry_core/templatetags/single-examiner-short-displayname.django.html')
def devilry_single_examiner_short_displayname(assignment, examiner, devilryrole):
    """
    Returns the examiner wrapped in HTML formatting tags perfect for showing
    the user inline in a non-verbose manner.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.assignment.Assignment` object.
            The ``assignment`` should be the assignment where the examiner belongs.
        examiner: A :class:`devilry.apps.core.models.examiner.Examiner` object.
        devilryrole: See
            :meth:`devilry.apps.core.models.assignment.Assignment.examiners_must_be_anonymized_for_devilryrole`.
    """
    return {
        'examiner': examiner,
        'anonymous': assignment.examiners_must_be_anonymized_for_devilryrole(
            devilryrole=devilryrole)
    }


@register.inclusion_tag('devilry_core/templatetags/multiple-candidates-long-displayname.django.html')
def devilry_multiple_candidates_long_displayname(assignment, candidates, devilryrole):
    """
    Returns the candidates wrapped in HTML formatting tags perfect for showing
    the candidates inline in a verbose manner.

    Typically used for showing all the candidates in an
    :class:`devilry.apps.core.models.assignment_group.AssignmentGroup`.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.assignment.Assignment` object.
            The ``assignment`` should be the assignment where the candidates belongs.
        candidates: An iterable of :class:`devilry.apps.core.models.candidates.Candidate` objects.
        devilryrole: See
            :meth:`devilry.apps.core.models.assignment.Assignment.students_must_be_anonymized_for_devilryrole`.
    """
    return {
        'assignment': assignment,
        'candidates': candidates,
        'devilryrole': devilryrole,
    }


@register.inclusion_tag('devilry_core/templatetags/multiple-candidates-short-displayname.django.html')
def devilry_multiple_candidates_short_displayname(assignment, candidates, devilryrole):
    """
    Returns the candidates wrapped in HTML formatting tags perfect for showing
    the candidates inline in a non-verbose manner.

    Typically used for showing all the candidates in an
    :class:`devilry.apps.core.models.assignment_group.AssignmentGroup`.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.assignment.Assignment` object.
            The ``assignment`` should be the assignment where the candidates belongs.
        candidates: An iterable of :class:`devilry.apps.core.models.candidates.Candidate` objects.
        devilryrole: See
            :meth:`devilry.apps.core.models.assignment.Assignment.students_must_be_anonymized_for_devilryrole`.
    """
    return {
        'assignment': assignment,
        'candidates': candidates,
        'devilryrole': devilryrole,
    }


@register.inclusion_tag('devilry_core/templatetags/multiple-examiners-long-displayname.django.html')
def devilry_multiple_examiners_long_displayname(assignment, examiners, devilryrole):
    """
    Returns the examiners wrapped in HTML formatting tags perfect for showing
    the examiners inline in a verbose manner.

    Typically used for showing all the examiners in an
    :class:`devilry.apps.core.models.assignment_group.AssignmentGroup`.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.assignment.Assignment` object.
            The ``assignment`` should be the assignment where the examiners belongs.
        examiners: An iterable of :class:`devilry.apps.core.models.examiners.Examiner` objects.
        devilryrole: See
            :meth:`devilry.apps.core.models.assignment.Assignment.examiners_must_be_anonymized_for_devilryrole`.
    """
    return {
        'assignment': assignment,
        'examiners': examiners,
        'devilryrole': devilryrole,
    }


@register.inclusion_tag('devilry_core/templatetags/multiple-examiners-short-displayname.django.html')
def devilry_multiple_examiners_short_displayname(assignment, examiners, devilryrole):
    """
    Returns the examiners wrapped in HTML formatting tags perfect for showing
    the examiners inline in a non-verbose manner.

    Typically used for showing all the examiners in an
    :class:`devilry.apps.core.models.assignment_group.AssignmentGroup`.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.assignment.Assignment` object.
            The ``assignment`` should be the assignment where the examiners belongs.
        examiners: An iterable of :class:`devilry.apps.core.models.examiners.Examiner` objects.
        devilryrole: See
            :meth:`devilry.apps.core.models.assignment.Assignment.examiners_must_be_anonymized_for_devilryrole`.
    """
    return {
        'assignment': assignment,
        'examiners': examiners,
        'devilryrole': devilryrole,
    }
