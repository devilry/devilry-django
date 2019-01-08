from django.utils.translation import ugettext_lazy

import django_rq
from django_cradmin.crinstance import reverse_cradmin_url

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
            return ugettext_lazy('New attempt for %(assignment_name)s') % {
                'assignment_name': self.assignment.long_name}
        if self.deadline_type == 'moved':
            return ugettext_lazy('Deadline moved for %(assignment_name)s') % {
                'assignment_name': self.assignment.long_name}


def send_deadline_email(feedback_sets, domain_url_start, deadline_type, template_name):
    """
    Send email about a new attempt given to a group.

    General function for sending deadline related emails.
    """
    student_users = []
    for feedback_set in feedback_sets:
        student_users.extend(list(get_student_users_in_group(feedback_set.group)))

    if len(student_users) == 0:
        return

    assignment = feedback_set.group.parentnode
    domain_url_start = domain_url_start.rstrip('/')
    absolute_url = '{}{}'.format(
        domain_url_start,
        reverse_cradmin_url(instanceid='devilry_group_student', appname='feedbackfeed', roleid=feedback_set.group_id)
    )

    subject_generator = DeadlineSubjectTextGenerator(assignment=assignment, deadline_type=deadline_type)
    template_dictionary = {
        'assignment_name': assignment.long_name,
        'deadline': feedback_set.deadline_datetime,
        'url': absolute_url
    }

    user_ids = [user.id for user in student_users]
    if deadline_type == 'new_attempt':
        message_context_type = Message.CONTEXT_TYPE_CHOICES.NEW_ATTEMPT.value
    elif deadline_type == 'moved':
        message_context_type = Message.CONTEXT_TYPE_CHOICES.DEADLINE_MOVED.value
    else:
        message_context_type = Message.CONTEXT_TYPE_CHOICES.OTHER.value

    message = Message(
        virtual_message_receivers={'user_ids': user_ids},
        context_type=message_context_type,
        metadata={
            'deadline': feedback_set.deadline_datetime.isoformat(),
            'feedbackset_id': feedback_set.id,
            'assignment_group_id': feedback_set.group_id,
            'assignment_id': feedback_set.group.parentnode_id
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
    send_new_attempt_email(
        feedback_sets=feedbackset_queryset,
        domain_url_start=domain_url_start
    )


def bulk_deadline_moved_mail(feedbackset_id_list, domain_url_start):
    from devilry.devilry_group.models import FeedbackSet
    feedbackset_queryset = FeedbackSet.objects \
        .select_related('group', 'group__parentnode', 'group__parentnode__parentnode') \
        .filter(id__in=feedbackset_id_list)
    send_deadline_moved_email(
        feedback_sets=feedbackset_queryset,
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
