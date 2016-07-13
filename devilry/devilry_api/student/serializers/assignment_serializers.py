# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from rest_framework import serializers

from devilry.apps.core.models.assignment_group import AssignmentGroup


class AssignmentGroupModelSerializer(serializers.ModelSerializer):
    assignment_name = serializers.SerializerMethodField()
    assignment_gradeform_setup_json = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentGroup
        fields = ['assignment_name', 'assignment_gradeform_setup_json',
                  'created_datetime', 'last_deadline', 'delivery_status']

    def get_assignment_name(self, instance):
        return instance.parentnode.short_name

    def get_assignment_gradeform_setup_json(self, instance):
        return instance.parentnode.gradeform_setup_json
