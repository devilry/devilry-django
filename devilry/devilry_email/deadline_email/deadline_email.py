from django.utils.translation import gettext_lazy

import django_rq
from cradmin_legacy.crinstance import reverse_cradmin_url

from devilry.devilry_message.models import Message
from devilry.devilry_message.utils.subject_generator import SubjectTextGenerator
from devilry.devilry_email.utils import get_student_users_in_group


class DeadlineSubjectTextGenerator(SubjectTextGenerator):
    def __init__(self, assignment, deadline_type=None):
        self.assignment = assignment
        self.deadline_type = deadline_type
        super(DeadlineSubjectTextGenerator, self).__init__()

    def get_subject_text(self):
        if not self.deadline_type:
            raise ValueError('Missing mailtype')
        if self.deadline_type == 'new_attempt':
            return gettext_lazy('New attempt for %(assignment_name)s') % {
                'assignment_name': self.assignment.long_name}
        if self.deadline_type == 'moved':
            return gettext_lazy('Deadline moved for %(assignment_name)s') % {
                'assignment_name': self.assignment.long_name}


def send_deadline_email(assignment, feedback_sets, domain_url_start, deadline_type, template_name):
    """
    Send email to users on a set of :class:`~.devilry.devilry_group.models.FeedbackSet`s that have
    had their deadline moved or been given a new attempt.

    Here's what this method does, step-by-step:
        1. Creates a :class:`~.devilry.devilry_message.models.Message` for each
           `FeedbackSet`.
        2. Calls :meth:`~.devilry.devilry_message.models.Message.prepare_and_send` which
           generates and sends an email to each user.

    Args:
        assignment: An instance of :class:`~.devilry.apps.core.models.Assignment`
            where deadlines changed.
        feedback_sets: An iterable containing :class:`~.devilry.devilry_group.models.FeedbackSet`s
            that have their deadlines changed.
        domain_url_start: The domain address, e.g: "www.example.com".
        template_name: Name (path) to template the message should be generated from.
        deadline_type: The type of deadline change (moved deadline or a new attempt).
    """
    if deadline_type == 'new_attempt':
        message_context_type = Message.CONTEXT_TYPE_CHOICES.NEW_ATTEMPT.value
    elif deadline_type == 'moved':
        message_context_type = Message.CONTEXT_TYPE_CHOICES.DEADLINE_MOVED.value
    else:
        message_context_type = Message.CONTEXT_TYPE_CHOICES.OTHER.value
    subject_generator = DeadlineSubjectTextGenerator(assignment=assignment, deadline_type=deadline_type)

    for feedback_set in feedback_sets:
        student_users = list(get_student_users_in_group(feedback_set.group))
        if len(student_users) == 0:
            return
        user_ids = [user.id for user in student_users]

        domain_url_start = domain_url_start.rstrip('/')
        absolute_url = '{}{}'.format(
            domain_url_start,
            reverse_cradmin_url(instanceid='devilry_group_student', appname='feedbackfeed', roleid=feedback_set.group_id)
        )
        template_dictionary = {
            'assignment_name': assignment.long_name,
            'deadline': feedback_set.deadline_datetime,
            'url': absolute_url
        }

        # Create message object and save it.
        message = Message(
            virtual_message_receivers={'user_ids': user_ids},
            context_type=message_context_type,
            metadata={
                'deadline': feedback_set.deadline_datetime.isoformat(),
                'feedbackset_id': feedback_set.id,
                'assignment_group_id': feedback_set.group_id,
                'assignment_id': assignment.id
            },
            message_type=['email']
        )
        message.full_clean()
        message.save()

        # Prepare receivers and send.
        message.prepare_and_send(
            subject_generator=subject_generator,
            template_name=template_name,
            template_context=template_dictionary
        )


def bulk_deadline_email(assignment_id, feedbackset_id_list, domain_url_start, template_name, deadline_type):
    """
    Fetches necessary data, and calls :meth:`.send_deadline_email`. Works as an interface
    for :meth:`bulk_send_new_attempt_email` and :meth:`bulk_send_deadline_moved_email`.

    Args:
        assignment_id: The ID of an :class:`~.devilry.apps.core.models.Assignment`
            where deadlines changed.
        feedbackset_id_list: The :class:`~.devilry.devilry_group.models.FeedbackSet`s
        that have their deadlines changed.
        domain_url_start: The domain address, e.g: "www.example.com".
        template_name: Name (path) to template the message should be generated from.
        deadline_type: The type of deadline change (moved deadline or a new attempt).
    """
    from devilry.devilry_group.models import FeedbackSet
    from devilry.apps.core.models import Assignment
    assignment = Assignment.objects.get(id=assignment_id)
    feedbackset_queryset = FeedbackSet.objects \
        .select_related('group', 'group__parentnode', 'group__parentnode__parentnode') \
        .filter(id__in=feedbackset_id_list)
    send_deadline_email(
        assignment=assignment,
        feedback_sets=feedbackset_queryset,
        domain_url_start=domain_url_start,
        template_name=template_name,
        deadline_type=deadline_type
    )


def bulk_send_new_attempt_email(**kwargs):
    """
    Queue RQ job for sending out notifications to users when they
    have been given a new attempt.

    Adds :meth:`bulk_deadline_email` to the RQ-queue.
    """
    kwargs.update({
        'template_name': 'devilry_email/deadline_email/new_attempt.txt',
        'deadline_type': 'new_attempt'
    })
    queue = django_rq.get_queue(name='email')
    queue.enqueue(bulk_deadline_email, **kwargs)


def bulk_send_deadline_moved_email(**kwargs):
    """
    Queue RQ job for sending out notifications to users when their
    deadline is moved.

    Adds :meth:`bulk_deadline_email` to the RQ-queue.
    """
    kwargs.update({
        'template_name': 'devilry_email/deadline_email/deadline_moved.txt',
        'deadline_type': 'moved'
    })
    queue = django_rq.get_queue(name='email')
    queue.enqueue(bulk_deadline_email, **kwargs)
