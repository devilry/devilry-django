from datetime import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from devilry.utils.devilry_email import send_templated_message
from .assignment_group import AssignmentGroup


class GroupInviteQuerySet(models.query.QuerySet):
    def filter_accepted(self):
        return self.filter(accepted=True)

    def filter_rejected(self):
        return self.filter(accepted=False)

    def filter_no_response(self):
        return self.filter(accepted=None)

    def filter_unanswered_received_invites(self, user):
        return self.filter_no_response().filter(sent_to=user)

    def filter_unanswered_sent_invites(self, group):
        return self.filter_no_response().filter(group=group)


class GroupInviteManager(models.Manager):
    def get_queryset(self):
        return GroupInviteQuerySet(self.model, using=self._db)

    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def all(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def filter_accepted(self):
        return self.get_queryset().filter_accepted()

    def filter_rejected(self):
        return self.get_queryset().filter_rejected()

    def filter_no_response(self):
        return self.get_queryset().filter_no_response()

    def filter_unanswered_received_invites(self, user):
        return self.get_queryset().filter_unanswered_received_invites(user)

    def filter_unanswered_sent_invites(self, group):
        return self.get_queryset().filter_unanswered_sent_invites(group)


class GroupInvite(models.Model):
    """
    Represents a group invite sent by a student to invite another
    student to join their AssignmentGroup.

    To send an invite::

        invite = GroupInvite(
            group=myassignmentgroup,
            sent_by=somestudent, # Typically request.user
            sent_to=anotherstudent
        )
        invite.full_clean() # MUST be called to validate that the invite is allowed
        invite.save()
        invite.send_invite_notification()

    To accept/reject an invite (sets the appropriate attributes and sends a notification)::

        invite.respond(accepted=True)
    """
    group = models.ForeignKey(AssignmentGroup)
    sent_datetime = models.DateTimeField(default=datetime.now)
    sent_by = models.ForeignKey(User, related_name='groupinvite_sent_by_set')
    sent_to = models.ForeignKey(User, related_name='groupinvite_sent_to_set')

    accepted = models.NullBooleanField(default=None)
    responded_datetime = models.DateTimeField(
        default=None, blank=True, null=True)

    objects = GroupInviteManager()

    class Meta:
        app_label = 'core'



    @staticmethod
    def send_invite_to_choices_queryset(group):
        """
        Returns a queryset of users that can be invited to the given group.

        Will we all relatedstudents on the period, excluding:
        - Students with an unanswered invite to the group.
        - Students already in the group.
        """
        students_in_group = [c.student.id for c in group.candidates.all()]
        students_invited_to_group = [invite.sent_to.id \
            for invite in GroupInvite.objects.filter_unanswered_sent_invites(group)]
        users = User.objects.filter(relatedstudent__period=group.period)\
            .exclude(id__in=students_in_group)\
            .exclude(id__in=students_invited_to_group)\
            .order_by('devilryuserprofile__full_name', 'username')\
            .select_related('devilryuserprofile')
        return users



    def get_sent_to_groups_queryset(self):
        """
        Returns a queryset matching all groups where the ``sent_to`` user is a candidate.
        """
        return AssignmentGroup.objects.filter_is_candidate(self.sent_to).filter(
                parentnode=self.group.parentnode)

    def clean(self):
        if self.accepted and not self.responded_datetime:
            self.responded_datetime = datetime.now()
        if self.sent_by and not self.group.candidates.filter(student=self.sent_by).exists():
            raise ValidationError('The user sending an invite must be a Candiate on the group.')
        if self.sent_to and self.group.candidates.filter(student=self.sent_to).exists():
            raise ValidationError(_(u'The student is already a member of the group.'))
        if GroupInvite.objects.filter_no_response()\
                .filter(group=self.group, sent_to=self.sent_to)\
                .exclude(id=self.id).exists():
            raise ValidationError(_('The student is already invited to join the group, but they have not responded yet'))

        assignment = self.group.assignment
        if assignment.students_can_create_groups:
            if assignment.students_can_not_create_groups_after and assignment.students_can_not_create_groups_after < datetime.now():
                raise ValidationError(_('Creating project groups without administrator approval is not allowed on this assignment anymore. Please contact you course administrator if you think this is wrong.'))
        else:
            raise ValidationError(_('This assignment does not allow students to form project groups on their own.'))

        period = assignment.period
        if not period.relatedstudent_set.filter(user=self.sent_to).exists():
            raise ValidationError(_('The invited student is not registered on this subject.'))

        if self.accepted != None:
            groups = list(self.get_sent_to_groups_queryset())
            if len(groups) > 1:
                raise ValidationError(_('The invited student is in more than one project group on this assignment, and can not join your group.'))
            elif len(groups) == 1:
                if groups[0].candidates.count() > 1:
                    raise ValidationError(_('The invited student is already in a project group.'))

    def respond(self, accepted):
        """
        Accept or reject the invite. If accepted, the user is added to the group
        using this algorithm::

            If the student is in a group on the assignment:
                Join that group with the group that sent the invite.
            Else:
                Add the student as a candidate on the group that sent the invite.

        In any case, a notification email is sent to the user that sent the
        invite.
        """
        self.accepted = accepted
        self.responded_datetime = datetime.now()
        self.full_clean()
        self.save()
        self._send_response_notification()
        if accepted:
            self._accept()

    def _accept(self):
        try:
            existing_group = self.get_sent_to_groups_queryset().get()
        except AssignmentGroup.DoesNotExist:
            self.group.candidates.create(student=self.sent_to)
        else:
            existing_group.merge_into(self.group)

    def _send_response_notification(self):
        sent_to_displayname = self.sent_to.devilryuserprofile.get_displayname()
        if self.accepted:
            subject = _('{user} accepted your project group invite').format(user=sent_to_displayname)
            template_name = 'devilry_core/groupinvite_accepted.django.txt'
        else:
            subject = _('{user} rejected your project group invite').format(user=sent_to_displayname)
            template_name = 'devilry_core/groupinvite_rejected.django.txt'
        assignment = self.group.assignment
        send_templated_message(subject, template_name, {
            'sent_to_displayname': sent_to_displayname,
            'assignment': assignment.long_name,
            'subject': assignment.subject.long_name
        }, self.sent_by)

    def send_invite_notification(self, request):
        """
        Called to send the invite notification. Should be called
        right after creating the invite. Not called in save() to
        make message sending less coupled (to avoid any issues
        with testing and bulk creation of invites).

        :param request:
            A Django HttpRequest object. The only method used is
            the build_absolute_uri() method.

        :raise ValueError:
            If ``accepted==None``, or ``id==None``.
        """
        if self.accepted != None:
            raise ValueError('Can not send notification for an accepted GroupInvite.')
        elif self.id == None:
            raise ValueError('Can not send notification for an unsaved GroupInvite.')
        sent_by_displayname = self.sent_by.devilryuserprofile.get_displayname()
        assignment = self.group.assignment
        subject = _('Project group invite for {assignment}').format(assignment=assignment.get_path())
        template_name = 'devilry_core/groupinvite_invite.django.txt'
        url = request.build_absolute_uri(reverse('devilry_student_groupinvite_respond', kwargs={'invite_id': self.id}))
        send_templated_message(subject, template_name, {
            'sent_by_displayname': sent_by_displayname,
            'assignment': assignment.long_name,
            'subject': assignment.subject.long_name,
            'url': url
        }, self.sent_to)
