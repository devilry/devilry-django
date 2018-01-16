import posixpath
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy

from django_cradmin.crinstance import reverse_cradmin_url
from devilry.apps.core.models import Examiner, Candidate
from devilry.utils.devilry_email import send_templated_message


def get_student_users_in_group(group):
    user_queryset = get_user_model().objects \
        .filter(id__in=group.candidates.values_list('relatedstudent__user', flat=True))
    return [user for user in user_queryset]


def send_feedback_email(feedback_set, points, domain_url_start):
    """
    Send a feedback mail to all students in and :class:`~.devilry.apps.core.models.AssignmentGroup` for
    a :class:`~.devilry.devilry_group.models.FeedbackSet`.

    Args:
        feedback_set: The feedback_set that was corrected.
        points: Points given on the ``FeedbackSet``.
        user: The user that corrected the ``FeedbackSet``.
    """
    assignment = feedback_set.group.parentnode
    subject = ugettext_lazy('Feedback for %(assignment_name)s') % {'assignment_name': assignment.long_name}
    template_name = 'devilry_email/feedback_email/assignment_feedback_student.txt'

    # Build absolute url
    domain_url_start = domain_url_start.rstrip('/')
    absolute_url = '{}{}'.format(
        domain_url_start,
        reverse_cradmin_url(instanceid='devilry_group_student', appname='feedbackfeed', roleid=feedback_set.group_id)
    )
    student_users = get_student_users_in_group(feedback_set.group)
    send_templated_message(subject, template_name, {
        'assignment': feedback_set.group.parentnode,
        'devilryrole': 'student',
        'points': points,
        'deadline_datetime': feedback_set.deadline_datetime,
        'corrected_datetime': feedback_set.grading_published_datetime,
        'url': absolute_url
    }, *student_users)


def bulk_feedback_mail(feedbackset_id_list, domain_url_start):
    """
    Starts an RQ task that sends a mail users in  a group for FeedbackSet.

    Args:
        feedbackset_id_list: A list of :class:`~.devilry.devilry_group.models.FeedbackSet`
        request: A ``DjangoHttpRequest`` object needed to build an absolute URI.
    """
    from devilry.devilry_group.models import FeedbackSet
    feedbackset_queryset = FeedbackSet.objects\
        .select_related('group', 'group__parentnode', 'group__parentnode__parentnode')\
        .filter(id__in=feedbackset_id_list)
    for feedback_set in feedbackset_queryset:
        send_feedback_email(
            feedback_set=feedback_set,
            points=feedback_set.grading_points,
            domain_url_start=domain_url_start
        )
