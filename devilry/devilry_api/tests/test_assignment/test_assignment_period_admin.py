from django.conf import settings
from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.devilry_api import devilry_api_mommy_factories
from devilry.devilry_api.assignment.views import assignment_period_admin
from devilry.devilry_api.tests.mixins import test_examiner_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.tests.mixins.test_common_filters_mixin import TestAssignmentFiltersExaminerMixin


class TestPeriodAdminAssignmentview(test_common_mixins.TestReadOnlyPermissionMixin,
                                    api_test_helper.TestCaseMixin,
                                    APITestCase):
    viewclass = assignment_period_admin.PeriodAdminAssignmentView
