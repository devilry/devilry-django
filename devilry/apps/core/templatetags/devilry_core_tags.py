import re

from django.conf import settings
from django import template
from django.utils.translation import gettext_lazy

from devilry.apps.core.models import Assignment
from devilry.utils import datetimeutils

register = template.Library()


class DevilrySingleLineNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        return re.sub('(\s|\\xa0)+', ' ', output).strip()


@register.tag
def devilrysingleline(parser, token):
    nodelist = parser.parse(('enddevilrysingleline',))
    parser.delete_first_token()
    return DevilrySingleLineNode(nodelist)


@register.filter
def devilry_user_displayname(user):
    if not user:
        return ''
    return user.get_full_name()


@register.filter
def format_is_passing_grade(is_passing_grade):
    if is_passing_grade:
        return gettext_lazy('passed')
    else:
        return gettext_lazy('failed')


@register.filter
def devilry_feedback_shortformat(staticfeedback):
    if not staticfeedback:
        return ''
    if staticfeedback.grade in ('Passed', 'Failed'):
        return staticfeedback.grade
    else:
        return '{} ({})'.format(
            staticfeedback.grade,
            format_is_passing_grade(staticfeedback.is_passing_grade))


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
        assignment: A :class:`devilry.apps.core.models.Assignment` object.
            The ``assignment`` should be the assignment where the candidate belongs.
        candidate: A :class:`devilry.apps.core.models.Candidate` object.
        devilryrole: See
            :meth:`devilry.apps.core.models.Assignment.students_must_be_anonymized_for_devilryrole`.
    """
    return {
        'candidate': candidate,
        'anonymous': assignment.students_must_be_anonymized_for_devilryrole(
            devilryrole=devilryrole),
        'anonymous_name': candidate.get_anonymous_name(assignment=assignment)
    }


@register.inclusion_tag('devilry_core/templatetags/single-candidate-short-displayname.django.html')
def devilry_single_candidate_short_displayname(assignment, candidate, devilryrole):
    """
    Returns the candidate wrapped in HTML formatting tags perfect for showing
    the user inline in a non-verbose manner.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.Assignment` object.
            The ``assignment`` should be the assignment where the candidate belongs.
        candidate: A :class:`devilry.apps.core.models.Candidate` object.
        devilryrole: See
            :meth:`devilry.apps.core.models.Assignment.students_must_be_anonymized_for_devilryrole`.
    """
    return {
        'candidate': candidate,
        'anonymous': assignment.students_must_be_anonymized_for_devilryrole(
            devilryrole=devilryrole),
        'anonymous_name': candidate.get_anonymous_name(assignment=assignment)
    }


@register.inclusion_tag('devilry_core/templatetags/single-examiner-long-displayname.django.html')
def devilry_single_examiner_long_displayname(assignment, examiner, devilryrole):
    """
    Returns the examiner wrapped in HTML formatting tags perfect for showing
    the user inline in a verbose manner.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.Assignment` object.
            The ``assignment`` should be the assignment where the examiner belongs.
        examiner: A :class:`devilry.apps.core.models.Examiner` object.
        devilryrole: See
            :meth:`devilry.apps.core.models.Assignment.examiners_must_be_anonymized_for_devilryrole`.
    """
    return {
        'examiner': examiner,
        'anonymous': assignment.examiners_must_be_anonymized_for_devilryrole(
            devilryrole=devilryrole)
    }


@register.inclusion_tag('devilry_core/templatetags/single-examiner-long-displayname-plain.django.html')
def devilry_single_examiner_long_displayname_plain(assignment, examiner, devilryrole):
    """
    Same as :meth:`.devilry_single_examiner_long_displayname` but returns the examiner without styling.
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
        assignment: A :class:`devilry.apps.core.models.Assignment` object.
            The ``assignment`` should be the assignment where the examiner belongs.
        examiner: A :class:`devilry.apps.core.models.Examiner` object.
        devilryrole: See
            :meth:`devilry.apps.core.models.Assignment.examiners_must_be_anonymized_for_devilryrole`.
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
    :class:`devilry.apps.core.models_group.AssignmentGroup`.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.Assignment` object.
            The ``assignment`` should be the assignment where the candidates belongs.
        candidates: An iterable of :class:`devilry.apps.core.models.Candidate` objects.
        devilryrole: See
            :meth:`devilry.apps.core.models.Assignment.students_must_be_anonymized_for_devilryrole`.
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
    :class:`devilry.apps.core.models_group.AssignmentGroup`.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.Assignment` object.
            The ``assignment`` should be the assignment where the candidates belongs.
        candidates: An iterable of :class:`devilry.apps.core.models.Candidate` objects.
        devilryrole: See
            :meth:`devilry.apps.core.models.Assignment.students_must_be_anonymized_for_devilryrole`.
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
    :class:`devilry.apps.core.models_group.AssignmentGroup`.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.Assignment` object.
            The ``assignment`` should be the assignment where the examiners belongs.
        examiners: An iterable of :class:`devilry.apps.core.models.Examiner` objects.
        devilryrole: See
            :meth:`devilry.apps.core.models.Assignment.examiners_must_be_anonymized_for_devilryrole`.
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
    :class:`devilry.apps.core.models_group.AssignmentGroup`.

    Handles anonymization based on ``assignment.anonymizationmode`` and ``devilryrole``.

    Args:
        assignment: A :class:`devilry.apps.core.models.Assignment` object.
            The ``assignment`` should be the assignment where the examiners belongs.
        examiners: An iterable of :class:`devilry.apps.core.models.Examiner` objects.
        devilryrole: See
            :meth:`devilry.apps.core.models.Assignment.examiners_must_be_anonymized_for_devilryrole`.
    """
    return {
        'assignment': assignment,
        'examiners': examiners,
        'devilryrole': devilryrole,
    }


@register.inclusion_tag('devilry_core/templatetags/groupstatus.django.html')
def devilry_groupstatus(group):
    """
    Get the status for the given AssignmentGroup.

    The output is one of the following texts wrapped in some ``<span>`` elements
    with appropriate css classes:

    - ``"waiting for feedback"``
    - ``"waiting for deliveries"``
    - ``"corrected"``

    .. note:: We normally do not show the corrected status, but instead show
        the grade using :func:`.devilry_grade_full`, at least in listings
        and other places where space is premium.

    Assumes the AssignmentGroup queryset is annotated with:

    - :meth:`~devilry.apps.core.models.AssignmentGroupQuerySet.annotate_with_is_waiting_for_feedback`
    - :meth:`~devilry.apps.core.models.AssignmentGroupQuerySet.annotate_with_is_waiting_for_deliveries`
    - :meth:`~devilry.apps.core.models.AssignmentGroupQuerySet.annotate_with_is_corrected`

    Args:
        group: A An :class:`devilry.apps.core.models.AssignmentGroup` object.

    """
    return {
        'group': group
    }


@register.inclusion_tag('devilry_core/templatetags/grade-short.django.html')
def devilry_grade_short(assignment, points):
    """
    Renders a grade as in its shortest form - no information about passed or failed,
    only the grade text (E.g.: "passed", "8/10", "A").

    Args:
        assignment: An :class:`devilry.apps.core.models.Assignment` object.
        points: The points to render the grade for.
    """
    return {
        'assignment': assignment,
        'grade': assignment.points_to_grade(points=points),
        'is_passing_grade': assignment.points_is_passing_grade(points=points),
    }


@register.inclusion_tag('devilry_core/templatetags/grade-full.django.html')
def devilry_grade_full(assignment, points, devilryrole):
    """
    Renders a grade as in its long form - including information about passed or failed.
    Examples::

        "passed"
        "8/10 (passed)"
        "F (failed)"

    If the ``students_can_see_points`` attribute of the assignment is
    set to ``True``, students are allowed to see the points behind
    a grade, so we include the points. Examples::

        "passed (10/10)"
        "failed (0/10)"
        "8/10 (passed)"
        "F (failed - 10/100)"
        "A (passed - 97/100)"

    Args:
        assignment: An :class:`devilry.apps.core.models.Assignment` object.
        points (int): The points to render the grade for.
        devilryrole (str): Must be one of the choices documented in
            :meth:`devilry.apps.core.models.Assignment.examiners_must_be_anonymized_for_devilryrole`.
    """
    include_is_passing_grade = assignment.points_to_grade_mapper != Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED
    include_points = assignment.points_to_grade_mapper != Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS
    if devilryrole == 'student' and not assignment.students_can_see_points:
        include_points = False

    return {
        'assignment': assignment,
        'grade': assignment.points_to_grade(points=points),
        'points': points,
        'is_passing_grade': assignment.points_is_passing_grade(points=points),
        'include_is_passing_grade': include_is_passing_grade,
        'include_points': include_points,
    }

@register.inclusion_tag('devilry_core/templatetags/grade-full-plain.django.html')
def devilry_grade_full_plain(assignment, points, devilryrole):
    """
    Renders a grade as in its long form - including information about passed or failed without styling.
    """
    include_is_passing_grade = assignment.points_to_grade_mapper != Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED
    include_points = assignment.points_to_grade_mapper != Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS
    if devilryrole == 'student' and not assignment.students_can_see_points:
        include_points = False

    return {
        'assignment': assignment,
        'grade': assignment.points_to_grade(points=points),
        'points': points,
        'is_passing_grade': assignment.points_is_passing_grade(points=points),
        'include_is_passing_grade': include_is_passing_grade,
        'include_points': include_points,
    }


@register.inclusion_tag('devilry_core/templatetags/comment-summary.django.html')
def devilry_comment_summary(group):
    """
    Renders a comment summary for the given AssignmentGroup.

    Assumes that the AssignmentGroup has been annotated with:

    - :meth:`~devilry.apps.core.models.AssignmentGroupQuerySet.annotate_with_number_of_private_groupcomments_from_user`.
    - :meth:`~devilry.apps.core.models.AssignmentGroupQuerySet.annotate_with_number_of_private_imageannotationcomments_from_user`.

    Args:
        group: An :class:`devilry.apps.core.models.AssignmentGroup` object annotated
            as explained above.
    """
    return {
        'group': group
    }


@register.inclusion_tag('devilry_core/templatetags/period-tags-on-period.django.html')
def devilry_period_tags_on_period(period, period_tags):
    return {
        'period': period,
        'period_tags': period_tags
    }


@register.inclusion_tag('devilry_core/templatetags/relatedexaminers-on-period-tag.django.html')
def devilry_relatedexaminers_on_period_tag(period_tag):
    """
    Renders the :class:`devilry.apps.core.models.relateduser.RelatedExaminer` in a comma separated format if there
    are any examiners, else it renders ``NO EXAMINERS``.

    Args:
        period_tag: a :class:`~.devilry.apps.core.models.period_tag.PeriodTag` instance.
    """
    return {
        'relatedexaminers': period_tag.relatedexaminers.all(),
        'num_relatedexaminers': period_tag.relatedexaminers.count()
    }


@register.inclusion_tag('devilry_core/templatetags/relatedstudents-on-period-tag.django.html')
def devilry_relatedstudents_on_period_tag(period_tag):
    """
    Renders the :class:`devilry.apps.core.models.relateduser.RelatedStudent` in a comma separated format if there
    are any students, else it renders ``NO STUDENTS``.

    Args:
        period_tag: a :class:`~.devilry.apps.core.models.period_tag.PeriodTag` object.
    """
    return {
        'relatedstudents': period_tag.relatedstudents.all(),
        'num_relatedstudents': period_tag.relatedstudents.count()
    }


@register.inclusion_tag('devilry_core/templatetags/relatedusers-on-period-tag.django.html')
def devilry_relatedusers_on_period_tag(period_tag):
    """
    Renders the :class:`devilry.apps.core.models.RelatedExaminer` and :class:`devilry.apps.core.models.RelatedStudent`
    comma separated.

    Uses tags :func:`.devilry_relatedexaminers_on_period_tag` and :func:`.devilry_relatedstudents_on_period_tag`.

    Args:
        period_tag: a :class:`devilry.apps.core.models.period_tag.PeriodTag` object.
    """
    return {
        'period_tag': period_tag
    }


@register.simple_tag
def devilry_test_css_class(suffix):
    """
    Adds a CSS class for automatic tests. CSS classes added using this
    template tag is only included when the the :setting:`DEVILRY_INCLUDE_TEST_CSS_CLASSES`
    setting is set to ``True``.

    To use this template tag, you provide a ``suffix`` as input,
    and the output will be `` test-<suffix> ``. Notice that we
    include space before and after the css class - this means that you do not need to
    add any extra spaces within your class-attribute to make room for the
    automatic test only css class.

    Examples:

        Use the template tag to add test only css classes:

        .. code-block:: django

            {% load cradmin_tags %}

            <p class="paragraph paragraph--large{% devilry_test_css_class 'introduction' %}">
                The introduction
            </p>

        Ensure that your test settings have ``DEVILRY_INCLUDE_TEST_CSS_CLASSES = True``.

        Write tests based on the test css class::

            from django import test
            import htmls

            class TestCase(test.TestCase):

                def test_introduction(self):
                    response = some_code_to_get_response()
                    selector = htmls.S(response.content)
                    with self.assertEqual(
                        'The introduction',
                        selector.one('test-introduction')

    Args:
        suffix: The suffix for your css class. The actual css class will be `` test-<suffix> ``.
    """
    include_test_css_classes = getattr(settings, 'DEVILRY_INCLUDE_TEST_CSS_CLASSES', False)
    if include_test_css_classes:
        return '  test-{}  '.format(suffix)
    else:
        return ''
