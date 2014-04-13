import itertools
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from model_utils import Etag
from abstract_is_admin import AbstractIsAdmin
from node import Node
from devilryuserprofile import DevilryUserProfile


class CandidateManager(models.Manager):
    """
    The Manager for :class:`.Candidate`.
    """
    def bulkadd_candidates_to_groups(self, groups, grouped_candidates):
        """
        Bulk add candidates to groups.
        
        :param groups:
            Iterable of :class:`devilry.apps.core.models.AssignmentGroup` objects.
        :param grouped_candidates:
            Iterable of candidates. Each item in the iterable contains an iterable
            of candidates that you want to add to the group at the same index in
            the ``groups`` iterable.

        Example::

            Candidate.objects.bulkadd_candidates_to_groups(
                groups=AssignmentGroup.create_x_groups(3),
                grouped_candidates=[
                    [Candidate(student=user1), Candidate(student=user2)],
                    [Candidate(student=user3)],
                    [Candidate(student=user4), Candidate(student=user5), Candidate(student=user6)]
                ]
            )

        :return: ``None``. We do not perform a query to get the created candidates because
            we assume the most common scenario is to not do anything more with the candidates
            right after they have been created.
        """
        if len(groups) != len(grouped_candidates):
            raise ValueError('groups and grouped_candidates must be the same length')
        candidates_to_create = []
        for group, candidates_in_group in itertools.izip(groups, grouped_candidates):
            if len(candidates_in_group) == 1:
                candidates_in_group[0].only_candidate_in_group = group
            for candidate in candidates_in_group:
                candidate.assignment_group = group
                candidates_to_create.append(candidate)
        self.bulk_create(candidates_to_create)


class Candidate(models.Model, Etag, AbstractIsAdmin):
    """
    A Candidate (student with metadata) on an :class:`.AssignmentGroup`.
    """
    objects = CandidateManager()

    class Meta:
        app_label = 'core'

    #: A student (a foreign key to a User).
    student = models.ForeignKey(User)

    #: The `AssignmentGroup`_ where this groups belongs.
    assignment_group = models.ForeignKey('AssignmentGroup',
        related_name='candidates')

    #: If this is the first candidate in the :obj:`~.Candidate.assignment_group`,
    #: this field is set to the same value as :obj:`~.Candidate.assignment_group`.
    only_candidate_in_group = models.OneToOneField('AssignmentGroup',
        related_name='only_candidate', null=True, blank=True)

    #: A optional candidate id. This can be anything as long as it is not
    #: more than 30 characters. When the assignment is anonymous, this is
    #: the "name" shown to examiners instead of the username of the
    #: student.
    candidate_id = models.CharField(max_length=30, blank=True, null=True, help_text='An optinal candidate id. This can be anything as long as it is less than 30 characters.')

    #: The candidate_id if this is a candidate on an anonymous assignment, and username if not.
    identifier = models.CharField(max_length=30,
                                  help_text='The candidate_id if this is a candidate on an anonymous assignment, and username if not.')
    full_name = models.CharField(max_length=300, blank=True, null=True,
                                 help_text='None if this is a candidate on an anonymous assignment, and full name if not.')
    email = models.CharField(max_length=300, blank=True, null=True,
                                 help_text='None if this is a candidate on an anonymous assignment, and email address if not.')
    etag = models.DateTimeField(auto_now_add=True)

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(assignment_group__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def __unicode__(self):
        return 'id={id} identifier={identifier}'.format(id=self.id, identifier=self.identifier)

    def update_identifier(self, anonymous):
        if anonymous:
            self.full_name = None
            self.email = None
            if not self.candidate_id:
                self.identifier = "candidate-id missing"
            else:
                self.identifier = self.candidate_id
        else:
            self.email = self.student.email
            self.full_name = self.student.devilryuserprofile.full_name
            self.identifier = self.student.username

    def save(self, *args, **kwargs):
        anonymous = kwargs.pop('anonymous', self.assignment_group.parentnode.anonymous)
        self.update_identifier(anonymous)
        super(Candidate, self).save(*args, **kwargs)

    @property
    def displayname(self):
        """
        Return a name for the candidate, preferrably the full name, but use the
        ``identifier`` if that is not available.
        """
        if self.full_name:
            return self.full_name
        else:
            return self.identifier


def sync_candidate_with_user_on_change(sender, **kwargs):
    """
    Signal handler which is invoked when a User is saved.
    """
    user = kwargs['instance']
    for candidate in Candidate.objects.filter(student=user):
        candidate.save()

post_save.connect(sync_candidate_with_user_on_change,
                  sender=User)


def sync_candidate_with_userprofile_on_change(sender, **kwargs):
    """
    Signal handler which is invoked when a DevilryUserProfile is saved.
    """
    userprofile = kwargs['instance']
    for candidate in Candidate.objects.filter(student=userprofile.user):
        candidate.save()

post_save.connect(sync_candidate_with_userprofile_on_change,
                  sender=DevilryUserProfile)
