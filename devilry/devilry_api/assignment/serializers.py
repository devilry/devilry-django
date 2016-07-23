# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from rest_framework import serializers

from devilry.apps.core.models.assignment_group import Assignment


# class AssignmentGroupModelSerializer(serializers.ModelSerializer):
#     assignment_name = serializers.SerializerMethodField()
#     assignment_gradeform_setup_json = serializers.SerializerMethodField()
#
#     class Meta:
#         model = AssignmentGroup
#         fields = ['assignment_name', 'assignment_gradeform_setup_json',
#                   'created_datetime', 'last_deadline', 'delivery_status']
#
#     def get_assignment_name(self, instance):
#         return instance.parentnode.short_name
#
#     def get_assignment_gradeform_setup_json(self, instance):
#         return instance.parentnode.gradeform_setup_json
#

class AssignmentModelSerializer(serializers.ModelSerializer):
    semester = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'subject',
            'long_name',
            'short_name',
            'semester',
            'publishing_time',
            'first_deadline',
            'anonymizationmode',
            'max_points',
            'passing_grade_min_points',
            'deadline_handling',
            'delivery_types']

    def get_semester(self, instance):
        return instance.parentnode.short_name

    def get_subject(self, instance):
        return instance.parentnode.parentnode.short_name