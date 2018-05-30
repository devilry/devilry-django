from django.utils import translation
from django.utils.translation import ugettext_lazy

import django_rq
from django_cradmin.crinstance import reverse_cradmin_url
from devilry.utils.devilry_email import send_templated_message
from devilry.devilry_email.utils import get_student_users_in_group, activate_translation_for_user


def get_subject(assignment, deadline_type=None):
    if not deadline_type:
        raise ValueError('Missing mailtype')
    if deadline_type == 'new_attempt':
        return ugettext_lazy('New attempt for %(assignment_name)s') % {'assignment_name': assignment.long_name}
    if deadline_type == 'moved':
        return ugettext_lazy('Deadline moved for %(assignment_name)s') % {'assignment_name': assignment.long_name}


def send_deadline_email(feedback_set, domain_url_start, deadline_type, template_name):
    """
    Send email about a new attempt given to a group.

    General function for sending deadline related emails.
    """
    assignment = feedback_set.group.parentnode
    domain_url_start = domain_url_start.rstrip('/')
    absolute_url = '{}{}'.format(
        domain_url_start,
        reverse_cradmin_url(instanceid='devilry_group_student', appname='feedbackfeed', roleid=feedback_set.group_id)
    )
    student_users = list(get_student_users_in_group(feedback_set.group))
    for student_user in student_users:
        current_language = translation.get_language()
        activate_translation_for_user(user=student_user)
        subject = get_subject(assignment=assignment, deadline_type=deadline_type)
        template_dictionary = {
            'assignment_name': assignment.long_name,
            'deadline': feedback_set.deadline_datetime,
            'url': absolute_url
        }
        send_templated_message(subject, template_name, template_dictionary, student_user, is_html=True)
        translation.activate(current_language)


def send_new_attempt_email(**kwargs):
    """
    Sets custom template and subject for mail sending regarding new attempts.
    """
    template_name = 'devilry_email/deadline_email/new_attempt.txt'
    send_deadline_email(deadline_type='new_attempt', template_name=template_name, **kwargs)


def send_deadline_moved_email(**kwargs):
    """
    Sets custom template and subject for mail sending regarding moved deadline.
    """
    template_name = 'devilry_email/deadline_email/deadline_moved.txt'
    send_deadline_email(deadline_type='moved', template_name=template_name, **kwargs)


def bulk_new_attempt_mail(feedbackset_id_list, domain_url_start):
    """
    Handle bulk sending of email to students in a group.
    """
    from devilry.devilry_group.models import FeedbackSet
    feedbackset_queryset = FeedbackSet.objects \
        .select_related('group', 'group__parentnode', 'group__parentnode__parentnode') \
        .filter(id__in=feedbackset_id_list)
    for feedback_set in feedbackset_queryset:
        send_new_attempt_email(
            feedback_set=feedback_set,
            domain_url_start=domain_url_start
        )


def bulk_deadline_moved_mail(feedbackset_id_list, domain_url_start):
    from devilry.devilry_group.models import FeedbackSet
    feedbackset_queryset = FeedbackSet.objects \
        .select_related('group', 'group__parentnode', 'group__parentnode__parentnode') \
        .filter(id__in=feedbackset_id_list)
    for feedback_set in feedbackset_queryset:
        send_deadline_moved_email(
            feedback_set=feedback_set,
            domain_url_start=domain_url_start
        )


def bulk_send_new_attempt_email(**kwargs):
    """
    Queue RQ job for sending out notifications to users when they are given a new attempt.
    """
    queue = django_rq.get_queue(name='email')
    queue.enqueue(bulk_new_attempt_mail, **kwargs)


def bulk_send_deadline_moved_email(**kwargs):
    """
    Queue RQ job for sending out notifications to users when they are given a new attempt.
    """
    queue = django_rq.get_queue(name='email')
    queue.enqueue(bulk_deadline_moved_mail, **kwargs)
