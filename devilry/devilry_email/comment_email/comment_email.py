# -*- coding: utf-8 -*-
import logging
import django_rq

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext, gettext_lazy

from devilry.devilry_account.models import (
    PeriodPermissionGroup,
    PermissionGroup,
    PermissionGroupUser,
    SubjectPermissionGroup
)
from devilry.devilry_comment.models import Comment
from devilry.devilry_email.utils import (
    build_feedbackfeed_absolute_url,
    get_examiner_users_in_group,
    get_student_users_in_group
)
from devilry.devilry_message.utils.subject_generator import \
    SubjectTextGenerator

logger = logging.getLogger(__name__)


class CommentSubjectTextGenerator(SubjectTextGenerator):
    """
    This class generates a subject through method `get_standard_subject`. We need
    this to generate a subject for the preferred translation of a user.
    """
    def __init__(self, comment, is_receipt=False):
        self.comment = comment
        self.is_receipt = is_receipt
        super(CommentSubjectTextGenerator, self).__init__()

    def get_subject_text(self):
        """
        Get a standard subject text based on the role of the comment poster.
        """
        if self.is_receipt:
            after_deadline = self.comment.published_datetime > self.comment.feedback_set.deadline_datetime
            if after_deadline:
                subject_text = gettext_lazy('You added a new comment AFTER THE DEADLINE for %(assignment_name)s') % {
                    'assignment_name': self.comment.feedback_set.group.parentnode.long_name
                }
            else:
                subject_text = gettext_lazy('You added a new delivery/comment for %(assignment_name)s') % {
                    'assignment_name': self.comment.feedback_set.group.parentnode.long_name
                }
            return subject_text
        if self.comment.user_role == Comment.USER_ROLE_STUDENT:
            if self.comment.published_datetime > self.comment.feedback_set.deadline_datetime:
                return gettext('A student added a new comment AFTER THE DEADLINE for %(assignment_name)s') % {
                    'assignment_name': self.comment.feedback_set.group.parentnode.long_name
                }
            return gettext('A student added a new delivery/comment for %(assignment_name)s') % {
                'assignment_name': self.comment.feedback_set.group.parentnode.long_name
            }
        elif self.comment.user_role == Comment.USER_ROLE_EXAMINER:
            return gettext('An examiner added a new comment for %(assignment_name)s') % {
                'assignment_name': self.comment.feedback_set.group.parentnode.long_name
            }
        return gettext('An admin added a new comment for %(assignment_name)s') % {
            'assignment_name': self.comment.feedback_set.group.parentnode.long_name
        }


def get_comment(comment_id):
    from devilry.devilry_group.models import GroupComment
    try:
        return GroupComment.objects.get(id=comment_id)
    except:
        logger.error('Mail: Something went wrong. GroupComment with ID#{} does not exist'.format(comment_id))


def get_subject_and_period_admins_users(group):
    """
    Get all User objects where the user is :class:`~.devilry.devilry_core.models.Subject`
    or :class:`~.devilry.devilry_core.models.Period` admins for the assignment group.
    """
    period_permissiongroups = PeriodPermissionGroup.objects \
        .filter(period=group.parentnode.period) \
        .filter(permissiongroup__grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN) \
        .values_list('permissiongroup_id', flat=True)

    subject_permissiongroups = SubjectPermissionGroup.objects \
        .filter(subject=group.parentnode.subject) \
        .filter(permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN) \
        .values_list('permissiongroup_id', flat=True)

    permissiongroups = PermissionGroup.objects \
        .filter(models.Q(id__in=period_permissiongroups) | models.Q(id__in=subject_permissiongroups))

    admin_users = PermissionGroupUser.objects \
        .filter(permissiongroup__in=permissiongroups) \
        .values_list('user', flat=True)

    users = get_user_model().objects.filter(id__in=admin_users).exclude(is_superuser=True)

    return users


def send_comment_email(comment, user_list, feedbackfeed_url, crinstance_id, domain_scheme, subject_generator=None, has_examiner=True):
    """
    Do not use this directly. Use ``send_examiner_comment_email`` or ``send_student_comment_email``.

    Args:
        comment: :class:`~.devilry.devilry_group.models.GroupComment`.

        user_list: A list of :class:`~.devilry.devilry_account.models.User` objects.

        feedbackfeed_url: Absolute url to the delivery feed.

        crinstance_id: devilry_group crinstance, used for building commentfile download urls.

        domain_scheme: Domain scheme, e.g: www.example.com.

        to_users_devilry_role: Email targeted against ('examiner' or 'student'). Used for anonymization.

        subject: Can be given a customized subject, if ``None``, a standard subject is created based on who
            created the comment.

        has_examiner: Boolean which defaults to True. Sets extra info in email if False
    """
    from devilry.devilry_message.models import Message
    template_name = 'devilry_email/comment_email/comment.txt'

    if len(user_list) == 0:
        return

    #: New implementation
    template_dictionary = {
        'comment': comment,
        'domain_scheme': domain_scheme,
        'crinstance_id': crinstance_id,
        'url': feedbackfeed_url,
        'has_examiner': has_examiner
    }
    if not subject_generator:
        subject_generator = CommentSubjectTextGenerator(comment=comment)

    user_ids = [user.id for user in user_list]

    message = Message(
        virtual_message_receivers={'user_ids': user_ids},
        context_type=Message.CONTEXT_TYPE_CHOICES.COMMENT_DELIVERY.value,
        metadata={
            'comment_id': comment.id,
            'feedbackset_id': comment.feedback_set_id,
            'assignment_group_id': comment.feedback_set.group_id,
            'assignment_id': comment.feedback_set.group.parentnode_id
        },
        message_type=['email']
    )
    message.full_clean()
    message.save()

    message.prepare_and_send(
        subject_generator=subject_generator,
        template_name=template_name,
        template_context=template_dictionary
    )


def send_examiner_comment_email(comment_id, domain_url_start, before_original_deadline=True):
    """
    Send email to examiner users.

    The email content will be the same for all examiners.

    If no examiner-users exists for the assignment group, :class:`~.devilry.devilry_core.models.Subject`
    and :class:`~.devilry.devilry_core.models.Period` admins connected to the assignemnt are sat
    as recipients of the email and extra info is added in the template.

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
    if before_original_deadline and comment.text == '':
        return

    absolute_url = build_feedbackfeed_absolute_url(
        domain_scheme=domain_url_start, group_id=comment.feedback_set.group.id, instance_id='devilry_group_examiner')

    examiner_users_in_group_queryset = get_examiner_users_in_group(group=comment.feedback_set.group)
    has_examiner = examiner_users_in_group_queryset.exists()
    recipients = list(examiner_users_in_group_queryset.exclude(id=comment.user.id))

    if not recipients:
        if not has_examiner:
            # No examiners assigned to the group. Set recipients to the subject-
            # and period-admin users so they receive an e-mail informing that the
            # group has no examiners assigned.
            if comment.text.strip() == '':
                # Do not spam admins with notifications for comments without any text.
                return
            absolute_url = build_feedbackfeed_absolute_url(
                domain_scheme=domain_url_start, group_id=comment.feedback_set.group.id, instance_id='devilry_group_admin')
            recipients = list(get_subject_and_period_admins_users(group=comment.feedback_set.group))
        else:
            # Group has an examiner, but no recipients.
            # This happens when the group has one examiner and the user is also the comment-poster.
            return

    send_comment_email(
        comment=comment,
        user_list=recipients,
        feedbackfeed_url=absolute_url,
        crinstance_id='devilry_group_examiner',
        domain_scheme=domain_url_start,
        has_examiner=has_examiner
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
    recipients = list(get_student_users_in_group(group=comment.feedback_set.group).exclude(id=comment.user.id))

    send_comment_email(
        comment=comment,
        user_list=recipients,
        feedbackfeed_url=absolute_url,
        domain_scheme=domain_url_start,
        crinstance_id='devilry_group_student'
    )

    if from_student_poster:
        send_comment_email(
            comment=comment,
            feedbackfeed_url=absolute_url,
            user_list=[comment.user],
            domain_scheme=domain_url_start,
            crinstance_id='devilry_group_student',
            subject_generator=CommentSubjectTextGenerator(comment=comment, is_receipt=True)
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
