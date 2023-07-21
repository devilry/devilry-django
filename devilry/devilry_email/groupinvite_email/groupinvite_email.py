from django.utils.translation import pgettext_lazy

from devilry.devilry_message.utils.subject_generator import \
    SubjectTextGenerator


def _get_groupinvite(groupinvite_id):
    from devilry.apps.core.models import GroupInvite
    return GroupInvite.objects \
        .select_related(
            'sent_by',
            'sent_to',
            'group',
            'group__parentnode',
            'group__parentnode__parentnode',
            'group__parentnode__parentnode__parentnode'
        ) \
        .get(id=groupinvite_id)

def _send_message(receiver_user, context_type, metadata, subject_generator, template_name, template_context):
    from devilry.devilry_message.models import Message

    # Create message
    message = Message(
        virtual_message_receivers={'user_ids': [receiver_user.id]},
        context_type=context_type,
        metadata={**metadata},
        message_type=['email']
    )
    message.full_clean()
    message.save()

    # Prepare and send message
    message.prepare_and_send(
        subject_generator=subject_generator,
        template_name=template_name,
        template_context={**template_context}
    )


def send_accepted_email(groupinvite_id):
    from devilry.devilry_message.models import Message

    class AcceptSubjectTextGenerator(SubjectTextGenerator):
        def __init__(self, invited_user):
            self.invited_user = invited_user
            super().__init__()

        def get_subject_text(self):
            return pgettext_lazy(
                'group invite',
                '{user} accepted your project group invite'
            ).format(
                user=self.invited_user.get_full_name()
            )

    groupinvite = _get_groupinvite(groupinvite_id=groupinvite_id)
    assignment = groupinvite.group.parentnode
    subject = groupinvite.group.parentnode.parentnode.parentnode

    _send_message(
        receiver_user=groupinvite.sent_by,
        context_type=Message.CONTEXT_TYPE_CHOICES.GROUP_INVITE_ACCEPTED.value,
        metadata={
            'groupinvite_id': groupinvite.id,
            'sent_by_user_id': groupinvite.sent_by.id,
            'sent_to_user_id': groupinvite.sent_to.id
        },
        subject_generator=AcceptSubjectTextGenerator(invited_user=groupinvite.sent_to),
        template_name='devilry_email/groupinvite_email/accepted.txt',
        template_context={
            'sent_to_displayname': groupinvite.sent_to.get_displayname(),
            'assignment': assignment.long_name,
            'subject': subject.long_name
        }
    )


def send_rejected_email(groupinvite_id):
    from devilry.devilry_message.models import Message

    class RejectSubjectTextGenerator(SubjectTextGenerator):
        def __init__(self, invited_user):
            self.invited_user = invited_user
            super().__init__()

        def get_subject_text(self):
            return pgettext_lazy(
                'group invite',
                '{user} rejected your project group invite'
            ).format(
                user=self.invited_user.get_full_name()
            )

    groupinvite = _get_groupinvite(groupinvite_id=groupinvite_id)
    assignment = groupinvite.group.parentnode
    subject = groupinvite.group.parentnode.parentnode.parentnode

    _send_message(
        receiver_user=groupinvite.sent_by,
        context_type=Message.CONTEXT_TYPE_CHOICES.GROUP_INVITE_REJECTED.value,
        metadata={
            'groupinvite_id': groupinvite.id,
            'sent_by_user_id': groupinvite.sent_by.id,
            'sent_to_user_id': groupinvite.sent_to.id
        },
        subject_generator=RejectSubjectTextGenerator(invited_user=groupinvite.sent_to),
        template_name='devilry_email/groupinvite_email/rejected.txt',
        template_context={
            'sent_to_displayname': groupinvite.sent_to.get_displayname(),
            'assignment': assignment.long_name,
            'subject': subject.long_name
        }
    )


def send_invite_email(groupinvite_id, url):
    from devilry.devilry_message.models import Message

    class InvitationSubjectTextGenerator(SubjectTextGenerator):
        def __init__(self, assignment):
            self.assignment = assignment
            super().__init__()

        def get_subject_text(self):
            return pgettext_lazy(
                'group invite',
                'Project group invite for {assignment}'
            ).format(
                assignment=self.assignment.get_path()
            )
    groupinvite = _get_groupinvite(groupinvite_id=groupinvite_id)
    assignment = groupinvite.group.parentnode
    subject = groupinvite.group.parentnode.parentnode.parentnode

    _send_message(
        receiver_user=groupinvite.sent_to,
        context_type=Message.CONTEXT_TYPE_CHOICES.GROUP_INVITE_INVITATION.value,
        metadata={
            'groupinvite_id': groupinvite.id,
            'sent_by_user_id': groupinvite.sent_by.id,
            'sent_to_user_id': groupinvite.sent_to.id
        },
        subject_generator=InvitationSubjectTextGenerator(assignment=assignment),
        template_name='devilry_email/groupinvite_email/invite.txt',
        template_context={
            'sent_by_displayname': groupinvite.sent_by.get_displayname(),
            'assignment': assignment.long_name,
            'subject': subject.long_name,
            'url': url
        }
    )
