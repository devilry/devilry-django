from django.utils.translation import gettext_lazy

import django_rq
from cradmin_legacy.crinstance import reverse_cradmin_url

from devilry.devilry_message.models import Message
from devilry.devilry_message.utils.subject_generator import SubjectTextGenerator
from devilry.devilry_email.utils import get_student_users_in_group


class FeedbackSubjectTextGenerator(SubjectTextGenerator):
    def __init__(self, assignment, feedback_type=None):
        self.assignment = assignment
        self.feedback_type = feedback_type
        super(FeedbackSubjectTextGenerator, self).__init__()

    def get_subject_text(self):
        if not self.feedback_type:
            raise ValueError('Missing mailtype')
        if self.feedback_type == 'feedback_created':
            return gettext_lazy('Feedback for %(assignment_name)s') % {
                'assignment_name': self.assignment.long_name}
        if self.feedback_type == 'feedback_edited':
            return gettext_lazy('Feedback updated for %(assignment_name)s') % {
                'assignment_name': self.assignment.long_name}


def send_feedback_email(assignment, feedback_sets, domain_url_start, feedback_type):
    """
    Send a feedback mail to all students in and :class:`~.devilry.apps.core.models.AssignmentGroup` for
    a :class:`~.devilry.devilry_group.models.FeedbackSet`.

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
        feedback_type: The type of feedback, is it a new grading or has the grading been update.

    """
    from devilry.apps.core.models import Assignment
    template_name = 'devilry_email/feedback_email/assignment_feedback_student.txt'

    if feedback_type == 'feedback_created':
        message_context_type = Message.CONTEXT_TYPE_CHOICES.FEEDBACK.value
    elif feedback_type == 'feedback_edited':
        message_context_type = Message.CONTEXT_TYPE_CHOICES.FEEDBACK_UPDATED.value
    else:
        message_context_type = Message.CONTEXT_TYPE_CHOICES.OTHER.value
    subject_generator = FeedbackSubjectTextGenerator(assignment=assignment, feedback_type=feedback_type)

    assignment = Assignment.objects \
        .prefetch_point_to_grade_map() \
        .filter(id=assignment.id)\
        .get()

    for feedback_set in feedback_sets:
        student_users = list(get_student_users_in_group(feedback_set.group))
        if len(student_users) == 0:
            return
        user_ids = [user.id for user in student_users]

        # Build absolute url
        domain_url_start = domain_url_start.rstrip('/')
        absolute_url = '{}{}'.format(
            domain_url_start,
            reverse_cradmin_url(
                instanceid='devilry_group_student',
                appname='feedbackfeed',
                roleid=feedback_set.group_id))
        template_dictionary = {
            'assignment': assignment,
            'devilryrole': 'student',
            'points': feedback_set.grading_points,
            'deadline_datetime': feedback_set.deadline_datetime,
            'corrected_datetime': feedback_set.grading_published_datetime,
            'url': absolute_url
        }

        # Create message object and save it.
        message = Message(
            virtual_message_receivers={'user_ids': user_ids},
            context_type=message_context_type,
            metadata={
                'points': feedback_set.grading_points,
                'grading_published_atetime': feedback_set.grading_published_datetime.isoformat(),
                'feedbackset_id': feedback_set.id,
                'assignment_group_id': feedback_set.group_id,
                'assignment_id': feedback_set.group.parentnode_id
            },
            message_type=['email']
        )
        message.full_clean()
        message.save()

        # Prepare receivers and send.
        message.prepare_and_send(
            subject_generator=subject_generator,
            template_name=template_name,
            template_context=template_dictionary)


def bulk_feedback_mail(assignment_id, feedbackset_id_list, domain_url_start, feedback_type=None):
    """
    Fetches necessary data, and calls :meth:`.send_feedback_email`. Works as an interface
    for :meth:`bulk_send_feedback_created_email` and :meth:`bulk_send_feedback_edited_email`.

    Args:
        assignment_id: The :class:`~.devilry.apps.core.models.Assignment` the feedbacks where given on.
        feedbackset_id_list: A list of :class:`~.devilry.devilry_group.models.FeedbackSet`
        domain_url_start: Domain url.
        feedback_type: The type of feedback, is it a new grading or has the grading been update.
    """
    from devilry.devilry_group.models import FeedbackSet
    from devilry.apps.core.models import Assignment
    feedbackset_queryset = FeedbackSet.objects\
        .select_related('group', 'group__parentnode', 'group__parentnode__parentnode')\
        .filter(id__in=feedbackset_id_list)
    assignment = Assignment.objects.get(id=assignment_id)
    send_feedback_email(
        assignment=assignment,
        feedback_sets=feedbackset_queryset,
        domain_url_start=domain_url_start,
        feedback_type=feedback_type
    )


def bulk_send_feedback_created_email(**kwargs):
    """
    Queue RQ job for sending out notifications to users when receive
    feedback.

    Adds :meth:`bulk_feedback_mail` to the RQ-queue.
    """
    kwargs.update({
        'feedback_type': 'feedback_created'
    })
    queue = django_rq.get_queue(name='email')
    queue.enqueue(bulk_feedback_mail, **kwargs)


def bulk_send_feedback_edited_email(**kwargs):
    """
    Queue RQ job for sending out notifications to users when their feedback
    has been edited.

    Adds :meth:`bulk_feedback_mail` to the RQ-queue.
    """
    kwargs.update({
        'feedback_type': 'feedback_edited'
    })
    queue = django_rq.get_queue(name='email')
    queue.enqueue(bulk_feedback_mail, **kwargs)
