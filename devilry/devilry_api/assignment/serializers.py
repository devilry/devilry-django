# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from rest_framework import serializers

from devilry.apps.core.models.assignment_group import Assignment


class AssignmentModelSerializer(serializers.ModelSerializer):
    subject_short_name = serializers.SerializerMethodField()
    period_short_name = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id',
            'long_name',
            'short_name',
            'period_short_name',
            'subject_short_name',
            'publishing_time',
            'anonymizationmode']

    def get_period_short_name(self, instance):
        return instance.parentnode.short_name

    def get_subject_short_name(self, instance):
        return instance.parentnode.parentnode.short_name
