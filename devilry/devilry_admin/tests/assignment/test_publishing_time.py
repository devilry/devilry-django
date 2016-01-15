from datetime import datetime, timedelta
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.apps.core.mommy_recipes import assignment_activeperiod_end
from devilry.apps.core import models as coremodels
from devilry.devilry_admin.views.assignment import overview
from devilry.devilry_admin.views.assignment import first_deadline
from devilry.project.develop.testhelpers.corebuilder import AssignmentBuilder, UserBuilder, PeriodBuilder


class TestOverviewAppUpdatePublishingTime(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = first_deadline.AssignmentFirstDeadlineUpdateView

    def test_h1(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment, viewkwargs={'pk':assignment.id})
        self.assertEquals(mockresponse.selector.one('h1').alltext_normalized, 'Edit assignment')
