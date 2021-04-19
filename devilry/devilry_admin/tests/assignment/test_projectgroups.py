from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_admin.views.assignment import projectgroups


class TestOverviewAppUpdateFirstDeadline(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = projectgroups.AssignmentProjectGroupUpdateView

    def test_h1(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment, viewkwargs={'pk':assignment.id})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized, 'Edit project group settings')
