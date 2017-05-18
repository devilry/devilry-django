from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings
from django.utils.dateparse import parse_datetime

from model_mommy import mommy

from devilry.devilry_account import models as account_models
from devilry.devilry_import_v2database.modelimporters.assignmentimporter import AssignmentImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


class TestAssignmentImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_Assignment_dict(self, period):
        return {
            'pk': 6,
            'model':
                'core.assignment',
            'admin_user_ids': [],
            'fields': {
                'examiners_publish_feedbacks_directly': True,
                'points_to_grade_mapper': 'raw-points',
                'short_name': 'week6',
                'students_can_create_groups': False,
                'students_can_see_points': True,
                'deadline_handling': 0,
                'publishing_time': '2016-05-16T11:04:59.577',
                'max_points': 2,
                'parentnode': 2,
                'delivery_types': 0,
                'long_name': 'Week 6',
                'admins': [],
                'first_deadline': '2016-05-23T11:04:59.577',
                'passing_grade_min_points': 1,
                'anonymous': False,
                'students_can_not_create_groups_after': None,
                'grading_system_plugin_id': 'devilry_gradingsystemplugin_points',
                'scale_points_percent': 100
            }
        }

