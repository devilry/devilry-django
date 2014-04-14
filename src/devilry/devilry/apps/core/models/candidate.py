import itertools
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

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

    #: A optional candidate id. This can be anything as long as it is not
    #: more than 30 characters. When the assignment is anonymous, this is
    #: the "name" shown to examiners instead of the username of the
    #: student.
    candidate_id = models.CharField(
        max_length=30,
        blank=True, null=True,
        help_text='An optional candidate id. This can be anything as long as it is less than 30 characters.')

    etag = models.DateTimeField(auto_now_add=True)

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(assignment_group__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def __unicode__(self):
        return 'id={id} student={student}'.format(id=self.id, student=self.student)

    @property
    def full_name(self):
        """
        Returns the full name of the student.
        """
        return self.student.devilryuserprofile.full_name

    def get_candidate_id_or_fallback(self):
        """
        Get the :obj:`.candidate_id`, or fall back to "Candidate ID not defined"
        translated to the current language.
        """
        return self.candidate_id or _("Candidate ID not defined")

    @property
    def identifier(self):
        """
        If the assignment is anonymous, return :meth:`.get_candidate_id_or_fallback`,
        if not, return the username of the student.
        """
        anonymous = self.assignment_group.parentnode.anonymous
        if anonymous:
            return self.get_candidate_id_or_fallback()
        else:
            return self.student.username

    @property
    def displayname(self):
        """
        Return a name for the candidate, preferrably the full name, but use the
        username if that is not available.
        """
        if self.full_name:
            return self.full_name
        else:
            return self.student.username
