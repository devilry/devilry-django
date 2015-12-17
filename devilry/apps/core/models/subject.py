from __future__ import print_function
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from abstract_is_candidate import AbstractIsCandidate
from abstract_is_examiner import AbstractIsExaminer
from basenode import BaseNode
from custom_db_fields import ShortNameField, LongNameField
from devilry.devilry_account.models import User, SubjectPermissionGroup
from model_utils import Etag
from node import Node


class SubjectQuerySet(models.QuerySet):
    def filter_is_admin(self, user):
        subjectids_where_is_admin_queryset = SubjectPermissionGroup.objects \
            .filter(permissiongroup__users=user).values_list('subject_id', flat=True)
        return self.filter(id__in=subjectids_where_is_admin_queryset)


class Subject(models.Model, BaseNode, AbstractIsExaminer, AbstractIsCandidate, Etag):
    """

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Node`_.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        `Node`_.

    .. attribute:: short_name

        A django.db.models.SlugField_ with max 20 characters. Only numbers,
        letters, '_' and '-'. Unlike all other children of
        :class:`BaseNode`, Subject.short_name is **unique**. This is mainly
        to avoid the overhead of having to recurse all the way to the top of
        the node hierarchy for every unique path.

    .. attribute:: periods

        A set of :class:`periods <devilry.apps.core.models.Period>` for this subject.

    .. attribute:: etag

       A DateTimeField containing the etag for this object.

    """
    objects = SubjectQuerySet.as_manager()

    class Meta:
        app_label = 'core'
        ordering = ['short_name']
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    short_name = ShortNameField(unique=True)
    long_name = LongNameField()
    parentnode = models.ForeignKey(Node, related_name='subjects')
    admins = models.ManyToManyField(User, blank=True)
    etag = models.DateTimeField(auto_now_add=True)

    @classmethod
    def q_is_admin(cls, user_obj):
        return \
            Q(admins__pk=user_obj.pk) | \
            Q(parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def get_path(self):
        """ Only returns :attr:`short_name` for subject since it is
        guaranteed to be unique. """
        return self.short_name

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(periods__assignments__publishing_time__lt=now)
        if not active:
            q &= ~Q(periods__end_time__gte=now)
        if not old:
            q &= ~Q(periods__end_time__lt=now)
        return q

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(periods__assignments__assignmentgroups__examiners__user=user_obj)

    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(periods__assignments__assignmentgroups__candidates__student=user_obj)

    def is_empty(self):
        """
        Returns ``True`` if this Subject does not contain any periods.
        """
        return self.periods.count() == 0
