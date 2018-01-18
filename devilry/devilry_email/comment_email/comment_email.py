from pprint import pprint

from django.utils.translation import ugettext_lazy

import django_rq

from devilry.utils.devilry_email import send_templated_message
from devilry.devilry_email.utils import get_student_users_in_group, get_examiner_users_in_group, \
    build_feedbackfeed_absolute_url


def get_student_users_not_comment_poster(group, exclude_user=None):
    """
    Get all student users in assignment group, and exclude the user that created the comment.
    """
    queryset = get_student_users_in_group(group=group)
    if not exclude_user:
        return queryset
    return queryset.exclude(id=exclude_user.id)


def get_examiner_users_not_comment_poster(group, exclude_user=None):
    """
    Get all examiner users in assignment group, and exclude the user that created the comment.
    """
    queryset = get_examiner_users_in_group(group=group)
    if not exclude_user:
        return queryset
    return queryset.exclude(id=exclude_user.id)


def send_comment_email(group, published_datetime, user_list, feedbackfeed_url):
    """
    Do not use this directly. Use ``send_examiner_comment_email`` or ``send_student_comment_email``.

    Args:
        group: AssignmentGroup.
        published_datetime: Publishing datetime of the comment.
        user_list: List of user objects.
        feedbackfeed_url: Url to the feedback feed for the users.

    """
    assignment_name = group.parentnode.long_name
    subject = ugettext_lazy('New comment in group for %(assignment_name)s') % {'assignment_name': assignment_name}
    templated_name = 'devilry_email/comment_email/comment.txt'
    template_dictionary = {
        'assignment_name': assignment_name,
        'commented_datetime': published_datetime,
        'url': feedbackfeed_url
    }
    send_templated_message(subject, templated_name, template_dictionary, *user_list)


def send_examiner_comment_email(group_id, comment_user_id, published_datetime, domain_url_start):
    """
    Send email to examiner users.
    """
    from devilry.apps.core.models import AssignmentGroup
    from django.contrib.auth import get_user_model
    group = AssignmentGroup.objects.get(id=group_id)
    comment_user = get_user_model().objects.get(id=comment_user_id)
    absolute_url = build_feedbackfeed_absolute_url(
        domain_scheme=domain_url_start, group_id=group.id, instance_id='devilry_group_examiner')
    examiner_users = list(get_examiner_users_not_comment_poster(group=group, exclude_user=comment_user))
    send_comment_email(
        group=group,
        published_datetime=published_datetime,
        user_list=examiner_users,
        feedbackfeed_url=absolute_url
    )


def send_student_comment_email(group_id, comment_user_id, published_datetime, domain_url_start):
    """
    Send email to student users.
    """
    from devilry.apps.core.models import AssignmentGroup
    from django.contrib.auth import get_user_model
    group = AssignmentGroup.objects.get(id=group_id)
    comment_user = get_user_model().objects.get(id=comment_user_id)
    absolute_url = build_feedbackfeed_absolute_url(
        domain_scheme=domain_url_start, group_id=group_id)
    student_users = list(get_student_users_not_comment_poster(group=group, exclude_user=comment_user))
    send_comment_email(
        group=group,
        published_datetime=published_datetime,
        user_list=student_users,
        feedbackfeed_url=absolute_url
    )


def bulk_send_comment_email_to_students(**kwargs):
    """
    Bulk send emails to students in group.
    """
    queue = django_rq.get_queue(name='email')
    queue.enqueue(send_student_comment_email, **kwargs)


def bulk_send_comment_email_to_examiners(**kwargs):
    """
    Bulk send emails to examiners in group.
    """
    queue = django_rq.get_queue(name='email')
    queue.enqueue(send_examiner_comment_email, **kwargs)


def bulk_send_comment_email_to_students_and_examiners(**kwargs):
    """
    Bulk send emails to students and examiners in group.
    """
    queue = django_rq.get_queue(name='email')
    queue.enqueue(send_student_comment_email, **kwargs)
    queue.enqueue(send_examiner_comment_email, **kwargs)
