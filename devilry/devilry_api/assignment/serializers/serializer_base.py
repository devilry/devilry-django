# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from rest_framework import serializers

from devilry.apps.core.models.assignment_group import Assignment


class PeriodId(serializers.IntegerField):

    def get_attribute(self, instance):
        """
        Get related period id

        Args:
            instance: :obj:`~apps.core.Assignment`

        Returns:
            id of related period

        """
        return instance.parentnode.id


class BaseAssignmentSerializer(serializers.ModelSerializer):
    #: Related subject short name.
    subject_short_name = serializers.SerializerMethodField()

    #: Related period short_name
    period_short_name = serializers.SerializerMethodField()

    #: Related period id
    period_id = PeriodId(required=True)

    class Meta:
        model = Assignment
        fields = [
            'id',
            'period_id',
            'long_name',
            'short_name',
            'period_short_name',
            'subject_short_name',
            'publishing_time',
            'anonymizationmode']

    def get_period_short_name(self, instance):
        """
        Returns short name of related :obj:`~apps.core.Period`.
        Args:
            instance: :obj:`~apps.core.Assignment`

        Returns:
            :attr:`~apps.core.Period.short_name`

        """
        return instance.parentnode.short_name

    def get_subject_short_name(self, instance):
        """
        Returns short name of related :obj:`~apps.core.Subject`.
        Args:
            instance: :obj:`~apps.core.Assignment`

        Returns:
            :attr:`~apps.core.Subject.short_name`

        """
        return instance.parentnode.parentnode.short_name
