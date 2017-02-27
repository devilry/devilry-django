from __future__ import unicode_literals

from django.db import models

from devilry.apps.core.models import Period
from devilry.apps.core.models import RelatedStudent, RelatedExaminer


class PeriodTagQuerySet(models.QuerySet):
    """
    Model manager for :class:`.PeriodTag`.
    """
    def get_all_distinct_tags_on_period(self, period):
        """
        Get a QuerySet of all distinct :obj:`~.PeriodTag`s on ``period``.
        Orders by :attr.PeriodTag.prefix` and :attr:`~.PeriodTag.tag`

        Args:
            period: Get distinct tags for.

        Returns:
            (QuerySet): :class:`.PeriodTag`.
        """
        return self.filter(period=period).\
            order_by('prefix', 'tag')\
            .distinct()

    def get_all_editable_tags(self):
        """
        Get a QuerySet of all :obj:`~.PeriodTag`s that are editable.
        I.e, :attr:`.PeriodTag.prefix` is blank.

        Returns:
            (QuerySet): :class:`.PeriodTag`.
        """
        return self.filter(prefix='')

    def get_all_hidden_tags(self):
        """
        Get a QuerySet of all :obj:`.PeriodTag`s with :class:`.PeriodTag.is_hidden=True`

        Returns:
            (QuerySet): :class:`.PeriodTag`.
        """
        return self.filter(is_hidden=True)


class PeriodTag(models.Model):
    """
    A :class:`.PeriodTag` represents a form of grouping on a period for
    :class:`~.devilry.app.core.models.relateduser.RelatedStudent`s and
    :class:`~.devilry.app.core.models.relateduser.RelatedExaminer`s
    """
    objects = PeriodTagQuerySet.as_manager()

    class Meta:
        unique_together = [
            ('prefix', 'tag')
        ]

    #: The period(semester) for the tag.
    period = models.ForeignKey(Period)

    #: Used by import scripts.
    #: If tags are imported from another system, the prefix should be used.
    #: If the prefix is used, the tag cannot(should not) be edited.
    #: If the prefix is blank, the tag is editable.
    prefix = models.CharField(blank=True, default='', max_length=30)

    #: A tag unique for the period.
    #: If the prefix is blank, the tag itself is unique, else
    #: the combination of the prefix and the tag is unique.
    tag = models.CharField(db_index=True, max_length=30)

    #: A tag can be set to hidden for filtering purposes.
    #: I.g, you don't want to remove a tag yet, but you do not want it
    #: to be visible either.
    is_hidden = models.BooleanField(default=False)

    #: When the tag was created.
    created_datetime = models.DateTimeField(auto_now_add=True)

    #: When the tag was last modified.
    #: This is for tags that can be modified.
    modified_datetime = models.DateTimeField(null=True, blank=True)

    #: ManyToMany field for :class:`~.devilry.apps.core.models.RelatedExaminer`.
    relatedexaminers = models.ManyToManyField(RelatedExaminer)

    #: ManyToMany field for :class:`~.devilry.apps.core.models.RelatedStudent`
    relatedstudents = models.ManyToManyField(RelatedStudent)
