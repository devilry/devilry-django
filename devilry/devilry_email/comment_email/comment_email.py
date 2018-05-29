# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy

import logging
import django_rq

from devilry.devilry_comment.models import Comment
from devilry.utils.devilry_email import send_templated_message
from devilry.devilry_email.utils import get_student_users_in_group, get_examiner_users_in_group, \
    build_feedbackfeed_absolute_url


logger = logging.getLogger(__name__)


def get_standard_subject_text(comment):
    """
    Get a standard subject text based on the role of the comment poster.
    """
    if comment.user_role == Comment.USER_ROLE_STUDENT:
        if comment.published_datetime > comment.feedback_set.deadline_datetime:
            return ugettext_lazy('A student added a new comment AFTER THE DEADLINE for %(assignment_name)s') % {
                'assignment_name': comment.feedback_set.group.parentnode.long_name
            }
        return ugettext_lazy('A student added a new delivery/comment for %(assignment_name)s') % {
            'assignment_name': comment.feedback_set.group.parentnode.long_name
        }
    elif comment.user_role == Comment.USER_ROLE_EXAMINER:
        return ugettext_lazy('An examiner added a new comment for %(assignment_name)s') % {
            'assignment_name': comment.feedback_set.group.parentnode.long_name
        }
    return ugettext_lazy('An admin added a new comment for %(assignment_name)s') % {
        'assignment_name': comment.feedback_set.group.parentnode.long_name
    }


def get_comment(comment_id):
    from devilry.devilry_group.models import GroupComment
    try:
        return GroupComment.objects.get(id=comment_id)
    except:
        logger.error('Mail: Something went wrong. GroupComment with ID#{} does not exist'.format(comment_id))


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


def send_comment_email(comment, user_list, feedbackfeed_url, to_users_devilry_role, subject=None):
    """
    Do not use this directly. Use ``send_examiner_comment_email`` or ``send_student_comment_email``.

    Args:
        group: AssignmentGroup.
        published_datetime: Publishing datetime of the comment.
        user_list: List of user objects.
        feedbackfeed_url: Url to the feedback feed for the users.

    """
    from devilry.apps.core.group_user_lookup import GroupUserLookup
    assignment = comment.feedback_set.group.parentnode
    group = comment.feedback_set.group
    if not subject:
        subject = ugettext_lazy('New comment in group for %(assignment_name)s') % {
            'assignment_name': assignment.long_name
        }
    templated_name = 'devilry_email/comment_email/comment.txt'
    for user in user_list:
        group_user_lookup = GroupUserLookup(
            assignment=assignment,
            group=group,
            requestuser=user,
            requestuser_devilryrole=to_users_devilry_role)
        template_dictionary = {
            'comment_user_name': group_user_lookup.get_long_name_from_user(
                user=comment.user, user_role=comment.user_role),
            'comment': comment,
            'url': feedbackfeed_url
        }
        send_templated_message(subject, templated_name, template_dictionary, user, is_html=True)


def send_examiner_comment_email(comment_id, domain_url_start):
    """
    Send email to examiner users.

    The email content will be the same for all examiners.

    How do the mails differ?

    Student comments::
        Email subjects:
            - Uploaded before the deadline:
                ``A student added a new delivery/comment for <assignment name>``

            - Uploaded after the deadline:
                ``A student added a new comment AFTER THE DEADLINE for <assignment_name>``

    Comments from other examiners::
        Email subject:
            ``An examiner added a new comment for <assignment name>``

    Comments from admins::
        Email subject:
            ``An admin added a new comment for <assignment name>``
    """
    comment = get_comment(comment_id=comment_id)
    absolute_url = build_feedbackfeed_absolute_url(
        domain_scheme=domain_url_start, group_id=comment.feedback_set.group.id, instance_id='devilry_group_examiner')
    examiner_users = list(get_examiner_users_not_comment_poster(group=comment.feedback_set.group, exclude_user=comment.user))
    send_comment_email(
        comment=comment,
        user_list=examiner_users,
        feedbackfeed_url=absolute_url,
        to_users_devilry_role='examiner',
        subject=get_standard_subject_text(comment=comment)
    )


def send_student_comment_email(comment_id, domain_url_start, from_student_poster=False):
    """
    Send email to student users.

    If `from_student_poster` is ``True``, send a receipt to the student that posted the comment.

    A student will get a single mail for uploaded comments to an
    :class:`~.devilry.core.apps.models.assignment.AssignmentGroup` based on the whether the it the student that
    uploaded the comment, or the comment was uploaded by another student on the group.

    The email content will be the same for all students.

    How do the mails differ?

    Student comments::
        The student that creates a new comment will receives a receipt with one of the following subjects:
            - Uploaded before the deadline:
                ``You added a new delivery/comment for <assignment name>``

            - Uploaded after the deadline:
                ``You added a new comment AFTER THE DEADLINE for <assignment name>``

        General emails to students in group will have one of the following subjects:
            - Uploaded before the deadline:
                ``A student added a new delivery/comment for <assignment name>``

            - Uploaded after the deadline:
                ``A student added a new comment AFTER THE DEADLINE for <assignment_name>``

    Comments from examiners::
        Email subject:
            ``An examiner added a new comment for <assignment name>``

    Comments from admins::
        Email subject:
            ``An admin added a new comment for <assignment name>``
    """
    comment = get_comment(comment_id=comment_id)
    absolute_url = build_feedbackfeed_absolute_url(
        domain_scheme=domain_url_start, group_id=comment.feedback_set.group.id)
    student_users = list(get_student_users_not_comment_poster(group=comment.feedback_set.group, exclude_user=comment.user))
    after_deadline = comment.published_datetime > comment.feedback_set.deadline_datetime
    send_comment_email(
        comment=comment,
        user_list=student_users,
        feedbackfeed_url=absolute_url,
        to_users_devilry_role='student',
        subject=get_standard_subject_text(comment=comment)
    )
    if after_deadline:
        subject_text = ugettext_lazy('You added a new comment AFTER THE DEADLINE for %(assignment_name)s') % {
            'assignment_name': comment.feedback_set.group.parentnode.long_name
        }
    else:
        subject_text = ugettext_lazy('You added a new delivery/comment for %(assignment_name)s') % {
            'assignment_name': comment.feedback_set.group.parentnode.long_name
        }
    if from_student_poster:
        send_comment_email(
            comment=comment,
            feedbackfeed_url=absolute_url,
            user_list=[comment.user],
            to_users_devilry_role='student',
            subject=subject_text
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
    if 'from_student_poster' in kwargs:
        kwargs.pop('from_student_poster')
    queue.enqueue(send_examiner_comment_email, **kwargs)
