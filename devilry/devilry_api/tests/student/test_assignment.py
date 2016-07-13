# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django import test
from model_mommy import mommy

from devilry.apps.core import mommy_recipes
from devilry.devilry_api.student.views import assignment_views
from devilry.devilry_api.tests.mixins import auth_test_common


class TestAssignmentGroupListView(auth_test_common.TestAuthAPIKeyMixin, test.TestCase):
    viewclass = assignment_views.AssignmentGroupListView
    route = '/student/assignment-list/'
