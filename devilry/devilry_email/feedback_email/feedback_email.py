from django.utils import translation
from django.utils.translation import ugettext_lazy

import django_rq
from django_cradmin.crinstance import reverse_cradmin_url
from devilry.utils.devilry_email import send_templated_message
from devilry.devilry_email.utils import get_student_users_in_group, activate_translation_for_user


def get_subject(assignment, feedback_type=None):
    if not feedback_type:
        raise ValueError('Missing mailtype')
    if feedback_type == 'feedback_created':
        return ugettext_lazy('Feedback for %(assignment_name)s') % {'assignment_name': assignment.long_name}
    if feedback_type == 'feedback_edited':
        return ugettext_lazy('Feedback updated for %(assignment_name)s') % {'assignment_name': assignment.long_name}


def send_feedback_email(feedback_set, points, domain_url_start, feedback_type):
    """
    Send a feedback mail to all students in and :class:`~.devilry.apps.core.models.AssignmentGroup` for
    a :class:`~.devilry.devilry_group.models.FeedbackSet`.

    Args:
        feedback_set: The feedback_set that was corrected.
        points: Points given on the ``FeedbackSet``.
        user: The user that corrected the ``FeedbackSet``.
        subject: The email subject.
    """
    from devilry.apps.core.models import Assignment
    template_name = 'devilry_email/feedback_email/assignment_feedback_student.txt'

    # Build absolute url
    domain_url_start = domain_url_start.rstrip('/')
    absolute_url = '{}{}'.format(
        domain_url_start,
        reverse_cradmin_url(instanceid='devilry_group_student', appname='feedbackfeed', roleid=feedback_set.group_id)
    )
    student_users = list(get_student_users_in_group(feedback_set.group))
    for student_user in student_users:
        current_language = translation.get_language()
        activate_translation_for_user(user=student_user)
        subject = get_subject(assignment=feedback_set.group.parentnode, feedback_type=feedback_type)
        assignment_queryset = Assignment.objects\
            .prefetch_point_to_grade_map()\
            .filter(id=feedback_set.group.parentnode.id)
        template_dictionary = {
            'assignment': assignment_queryset.get(),
            'devilryrole': 'student',
            'points': points,
            'deadline_datetime': feedback_set.deadline_datetime,
            'corrected_datetime': feedback_set.grading_published_datetime,
            'url': absolute_url
        }
        send_templated_message(subject, template_name, template_dictionary, student_user, is_html=True)
        translation.activate(current_language)


def send_feedback_edited_email(**kwargs):
    """
    Send feedback updated email. With customized subject for edited feedback.
    """
    kwargs.update({
        'feedback_type': 'feedback_edited'
    })
    send_feedback_email(**kwargs)


def send_feedback_created_email(**kwargs):
    """
    Send feedback created email. With customized subject for newly published feedback.
    """
    kwargs.update({
        'feedback_type': 'feedback_created'
    })
    send_feedback_email(**kwargs)


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
        send_feedback_created_email(
            feedback_set=feedback_set,
            points=feedback_set.grading_points,
            domain_url_start=domain_url_start
        )


def bulk_send_email(**kwargs):
    """
    Queues bulk sending of emails to students.

    This method only handles the queueing, and calls :func:`.bulk_feedback_mail` as the RQ task.

    Args:
        **kwargs: Arguments required by :func:`.bulk_feedback_mail`.
    """
    queue = django_rq.get_queue(name='email')
    queue.enqueue(bulk_feedback_mail, **kwargs)
