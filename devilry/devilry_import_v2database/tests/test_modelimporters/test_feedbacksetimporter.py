from devilry.devilry_account.models import PermissionGroup, SubjectPermissionGroup
from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings

from model_mommy import mommy

from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_import_v2database.modelimporters.feedbackset_importer import FeedbackSetImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


# class TestFeedbackSetImporter(ImporterTestCaseMixin, test.TestCase):
#     def _create_deadline_dict(self, assignment_group):
#         return {
#             'pk': 13,
#             'model': 'core.deadline',
#             'fields': {
#                 'feedbacks_published': True,
#                 'deliveries_available_before_deadline': False,
#                 'text': None,
#                 'deadline': '2016-04-11T11:04:00',
#                 'assignment_group': 13,
#                 'why_created': None,
#                 'added_by': None}
#         }
