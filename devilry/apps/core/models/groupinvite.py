from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import Candidate
from devilry.devilry_account.models import User
from devilry.utils.devilry_email import send_templated_message
from .assignment_group import AssignmentGroup


class GroupInviteQuerySet(models.QuerySet):
    def filter_accepted(self):
        """
        Filter all :class:`.GroupInvite` objects that has been accepted
        """
        return self.filter(accepted=True)

    def filter_rejected(self):
        """
        Filter all :class:`.GroupInvite` objects that has been rejected
        """
        return self.filter(accepted=False)

    def filter_no_response(self):
        """
        Filter all :class:`.GroupInvite` objects that has not been responded.
        """
        return self.filter(accepted=None)

    def filter_unanswered_received_invites(self, user):
        """
        Filter all :class:`.GroupInvite` objects that has not been responded by ``user``
        Args:
            user: :class:`devilry_account.User` the user that got invitations
        """
        return self.filter_no_response().filter(sent_to=user)

    def filter_unanswered_sent_invites(self, group):
        """
        Filter all :class:`.GroupInvite` objects on ``group``
        Args:
            group: :class:`core.AssignmentGroup`
        """
        return self.filter_no_response().filter(group=group)

    def filter_allowed_to_create_groups(self):
        """
        Filter all :class:`.GroupInvite` objects where the :class:`core.Assignment` allows to create group
        """
        return self.filter(
            models.Q(
                models.Q(group__parentnode__students_can_create_groups=True) &
                models.Q(group__parentnode__students_can_not_create_groups_after__gt=timezone.now())
            ) |
            models.Q(
                models.Q(group__parentnode__students_can_create_groups=True) &
                models.Q(group__parentnode__students_can_not_create_groups_after__isnull=True)
            )
        )


class GroupInviteManager(models.Manager):
    pass


class GroupInvite(models.Model):
    """
    Represents a group invite sent by a student to invite another
    student to join their AssignmentGroup.

    Example:
        invite = GroupInvite(
            group=myassignmentgroup,
            sent_by=somestudent, # Typically request.user
            sent_to=anotherstudent
        )
        invite.full_clean() # MUST be called to validate that the invite is allowed
        invite.save()
        invite.send_invite_notification()

    To accept/reject an invite (sets the appropriate attributes and sends a notification)
    invite.respond(accepted=True)
    """
    group = models.ForeignKey(AssignmentGroup)
    sent_datetime = models.DateTimeField(default=timezone.now)
    sent_by = models.ForeignKey(User, related_name='groupinvite_sent_by_set')
    sent_to = models.ForeignKey(User, related_name='groupinvite_sent_to_set')

    accepted = models.NullBooleanField(default=None)
    responded_datetime = models.DateTimeField(
        default=None, blank=True, null=True)

    objects = GroupInviteManager.from_queryset(GroupInviteQuerySet)()

    class Meta:
        app_label = 'core'

    @staticmethod
    def send_invite_to_choices_queryset(group):
        """
        Returns a queryset of :class:`core.Candidate` that can be invited to the given group.

        Will be excluded:
        - Students already in the group.
        - Already in a group with more than 1 candidates
        - Candidates with pending invitations on ``group``
        """
        # Exclude users with pending invitations
        excluded_users = User.objects.filter(
            models.Q(groupinvite_sent_to_set__accepted=None) | models.Q(groupinvite_sent_to_set__accepted=True),
            groupinvite_sent_to_set__group=group
        )

        return Candidate.objects.filter(
            assignment_group__parentnode__students_can_create_groups=True,
            assignment_group__parentnode=group.parentnode,
            assignment_group__cached_data__candidate_count=1
        ).exclude(
            models.Q(assignment_group_id=group.id) | models.Q(relatedstudent__user__in=excluded_users)
        ).select_related('relatedstudent__user', 'assignment_group__parentnode')\
            .order_by('relatedstudent__user__fullname', 'relatedstudent__user__shortname')

    @staticmethod
    def validate_candidate_id_sent_to(group, candidate_id):
        """
        Checks whether a candidate join the ``group``
        Args:
            group: :class:`core.AssignmentGroup` group to join
            candidate_id: :attr:`core.Candidate.id` id of candidate

        Returns:
            :class:`devilry_account.User` returns the user related to the candidate

        Raises:
            ValidationError - If the user is not eligible to join
        """
        try:
            return GroupInvite.send_invite_to_choices_queryset(group)\
                .get(id=candidate_id)\
                .relatedstudent.user
        except Candidate.DoesNotExist:
            raise ValidationError(ugettext_lazy('The selected student is not eligible to join the group.'))

    def clean(self):
        if self.accepted and not self.responded_datetime:
            self.responded_datetime = timezone.now()
        if self.sent_by and not self.group.candidates.filter(relatedstudent__user=self.sent_by).exists():
            raise ValidationError(ugettext_lazy('The user sending an invite must be a Candiate on the group.'))
        if self.sent_to and self.group.candidates.filter(relatedstudent__user=self.sent_to).exists():
            raise ValidationError(ugettext_lazy('The student is already a member of the group.'))
        if GroupInvite.objects.filter_no_response() \
                .filter(group=self.group, sent_to=self.sent_to) \
                .exclude(id=self.id).exists():
            raise ValidationError(
                ugettext_lazy('The student is already invited to join the group, but they have not responded yet.'))

        assignment = self.group.assignment
        if assignment.students_can_create_groups:
            if assignment.students_can_not_create_groups_after and \
                            assignment.students_can_not_create_groups_after < timezone.now():
                raise ValidationError(ugettext_lazy(
                    'Creating project groups without administrator approval is not '
                    'allowed on this assignment anymore. Please contact you course '
                    'administrator if you think this is wrong.'))
        else:
            raise ValidationError(
                ugettext_lazy('This assignment does not allow students to form project groups on their own.'))

        if not Assignment.objects.filter(id=assignment.id).filter_user_is_candidate(self.sent_to):
            raise ValidationError(ugettext_lazy('The invited student is not registered on this assignment.'))

        if self.accepted:
            sent_to_group = AssignmentGroup.objects.filter(parentnode=assignment) \
                .filter_user_is_candidate(self.sent_to) \
                .first()
            if sent_to_group.cached_data.candidate_count > 1:
                raise ValidationError(ugettext_lazy(
                    'The invited student is already in a project group with more than 1 students.'))

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
        if self.accepted:
            raise ValidationError(ugettext_lazy('This invite has already been accepted.'))
        if self.accepted is not None and not self.accepted:
            raise ValidationError(ugettext_lazy('This invite has already been declined.'))
        self.accepted = accepted
        self.responded_datetime = timezone.now()
        self.full_clean()
        self.save()
        self._send_response_notification()
        if accepted:
            self._accept()

    def _accept(self):
        """
        Merging assignment groups
        """
        source = AssignmentGroup.objects.filter_user_is_candidate(self.sent_to) \
            .filter(parentnode=self.group.parentnode) \
            .get()
        with transaction.atomic():
            source.merge_into(self.group)

    def _send_response_notification(self):
        sent_to_displayname = self.sent_to.get_full_name()
        if self.accepted:
            subject = ugettext_lazy('{user} accepted your project group invite').format(user=sent_to_displayname)
            template_name = 'devilry_core/groupinvite_accepted.django.txt'
        else:
            subject = ugettext_lazy('{user} rejected your project group invite').format(user=sent_to_displayname)
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

        Args:
            request:
                A Django HttpRequest object. The only method used is
                the build_absolute_uri() method.

        Raises:
            ValueError If ``accepted==None``, or ``id==None``.

        """
        if self.accepted is not None:
            raise ValueError(ugettext_lazy('Can not send notification for an accepted GroupInvite.'))
        elif self.id is None:
            raise ValueError(ugettext_lazy('Can not send notification for an unsaved GroupInvite.'))
        sent_by_displayname = self.sent_by.get_displayname()
        assignment = self.group.assignment
        subject = ugettext_lazy('Project group invite for {assignment}').format(assignment=assignment.get_path())
        template_name = 'devilry_core/groupinvite_invite.django.txt'
        url = request.build_absolute_uri(reverse('devilry_student_groupinvite_respond', kwargs={'invite_id': self.id}))
        send_templated_message(subject, template_name, {
            'sent_by_displayname': sent_by_displayname,
            'assignment': assignment.long_name,
            'subject': assignment.subject.long_name,
            'url': url
        }, self.sent_to)
