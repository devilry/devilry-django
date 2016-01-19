from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_admin.views.assignment import long_and_shortname


class TestOverviewAppUpdateFirstDeadline(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = long_and_shortname.AssignmentLongAndShortNameUpdateView

    def test_h1(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment, viewkwargs={'pk':assignment.id})
        self.assertEquals(mockresponse.selector.one('h1').alltext_normalized, 'Edit assignment')
