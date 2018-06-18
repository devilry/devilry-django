# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models


def generate_model_name(obj):
    return '{}_{}'.format(obj._meta.app_label, obj.__class__.__name__.lower())


class TempMergeIdManager(models.Manager):
    """
    Manager for :class:`~.devilry.devilry_merge_v3database.models.TempMergeId`.
    """
    def create_from_instances(self, merge_to_obj, merge_from_obj):
        """
        Create entry for the models saved in the `migrate to` database and the `migrated from`.

        Args:
            merge_to_obj: The object saved in the database to merge to.
            merge_from_obj: The object from the database to merge from.

        Return:
            :class:`~.devilry.devilry_merge_v3database.models.TempMergeId`: Saved instance.
        """

        model_name_migrate_to = generate_model_name(obj=merge_to_obj)
        model_name_migrate_from = generate_model_name(obj=merge_from_obj)
        if model_name_migrate_to != model_name_migrate_from:
            raise ValidationError('Must be models of same type: {} != {}'.format(
                model_name_migrate_to, model_name_migrate_from))

        temp_merge_id = TempMergeId(
            to_id=merge_to_obj.id,
            from_id=merge_from_obj.id,
            model_name=model_name_migrate_to
        )
        temp_merge_id.full_clean()
        temp_merge_id.save()
        return temp_merge_id


class TempMergeIdQuerySet(models.QuerySet):
    """
    QuerySet for :class:`devilry_merge_v3database.models.TempMergeId`.
    """
    def get_from_label_and_merge_from_obj_id(self, model_name, from_id):
        """
        Get TempMergeId from model and the model from the merging database.
        """
        return self.get(model_name=model_name, from_id=from_id)


class TempMergeId(models.Model):
    """
    Table that defines a link between two databases, the database to merge into, and the database to
    merge from. We need this since some models does not have an applicable super key in the current state
    when they are migrated.

    This table should be before the management script is run.
    """
    objects = TempMergeIdManager.from_queryset(TempMergeIdQuerySet)()

    #: ID of the model in the database it was migrated to.
    to_id = models.PositiveIntegerField()

    #: ID of the model in the database it was migrated from.
    from_id = models.PositiveIntegerField()

    #: Name of the model.
    model_name = models.CharField(
        max_length=255,
        blank=False, null=False)

    class Meta:
        unique_together = ('to_id', 'from_id', 'model_name')
