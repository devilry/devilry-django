from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from abstract_is_candidate import AbstractIsCandidate
from abstract_is_examiner import AbstractIsExaminer
from basenode import BaseNode
from custom_db_fields import ShortNameField, LongNameField
from devilry.devilry_account.models import User, SubjectPermissionGroup, PeriodPermissionGroup
from devilry.utils import devilry_djangoaggregate_functions
from model_utils import Etag
from node import Node


class SubjectQuerySet(models.QuerySet):
    def filter_user_is_admin(self, user):
        """
        Filter the queryset to only include :class:`.Subject` objects where the
        given ``user`` is in a :class:`.devilry.devilry_account.models.SubjectPermissionGroup`.

        Args:
            user: A User object.
        """
        if user.is_superuser:
            return self.all()
        else:
            subjectids_where_is_admin_queryset = SubjectPermissionGroup.objects \
                .filter(permissiongroup__users=user).values_list('subject_id', flat=True)
            return self.filter(id__in=subjectids_where_is_admin_queryset)

    def __get_subjectids_where_user_is_periodadmin(self, user):
        subjectids_where_is_periodadmin_queryset = PeriodPermissionGroup.objects \
            .filter(models.Q(permissiongroup__users=user))\
            .values_list('period__parentnode_id', flat=True)\
            .distinct()
        return subjectids_where_is_periodadmin_queryset

    def filter_user_is_admin_for_any_periods_within_subject(self, user):
        """
        Filter the queryset to only include :class:`.Subject` objects where the
        given ``user`` is in a :class:`.devilry.devilry_account.models.PeriodPermissionGroup`
        for a period within a subject.

        Args:
            user: A User object.
        """
        if user.is_superuser:
            return self.all()
        else:
            queryset = (self.filter_user_is_admin(user) |
                        self.filter(id__in=self.__get_subjectids_where_user_is_periodadmin(user=user)))
            return queryset.distinct()

    def annotate_with_has_active_period(self):
        """
        Annotate with ``has_active_period`` - ``True`` if the subject contains
        any active periods.
        """
        now = timezone.now()
        whenquery = models.Q(periods__start_time__lt=now, periods__end_time__gt=now)
        return self.annotate(
                has_active_period=devilry_djangoaggregate_functions.BooleanCount(
                        models.Case(
                                models.When(whenquery, then=1))
                )
        )

    def prefetch_active_period_objects(self):
        """
        Prefetch active periods in the ``active_period_objects`` attribute.

        The ``active_period_objects`` attribute is a ``list`` of
        :class:`devilry.apps.core.models.Period` objects ordered by
        ``start_time`` in ascending order.

        Examples:

            Make a queryset using with active peridods prefetched::

                from devilry.apps.core.models import Period
                queryset = Period.objects.prefetch_active_period_objects()

            Work with the queryset::

                for period in queryset.first().active_period_objects:
                    print(period.short_name)

            Get the last active period for a subject (see :meth:`.Subject.last_active_period`)::

                last_active_period = queryset.first().last_active_period
        """
        from devilry.apps.core.models import Period
        return self.prefetch_related(
            models.Prefetch('periods',
                            queryset=Period.objects.filter_active().order_by('start_time'),
                            to_attr='active_period_objects'))


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
    parentnode = models.ForeignKey(Node, related_name='subjects',
                                   null=True, blank=True)
    admins = models.ManyToManyField(User, blank=True)
    etag = models.DateTimeField(auto_now_add=True)

    def get_path(self):
        """ Only returns :attr:`short_name` for subject since it is
        guaranteed to be unique. """
        return self.short_name

    @property
    def last_active_period(self):
        """
        Get the last active :class:`devilry.apps.core.models.Period`.

        Only works if the queryset used to fetch the Subject is
        uses :meth:`.SubjectQuerySet.prefetch_active_periodobjects`
        """
        if not hasattr(self, 'active_period_objects'):
            raise AttributeError('The last_active_period property requires '
                                 'SubjectQuerySet.prefetch_active_period_objects()')
        if self.active_period_objects:
            return self.active_period_objects[-1]
        else:
            return None
