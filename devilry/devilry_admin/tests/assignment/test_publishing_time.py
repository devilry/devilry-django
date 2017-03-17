from datetime import datetime

from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment import publishing_time
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestAssignmentPublishingTimeUpdateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = publishing_time.AssignmentPublishingTimeUpdateView

    def test_h1(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEquals(mockresponse.selector.one('h1').alltext_normalized, 'Edit assignment')


class TestPublishNowRedirectView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = publishing_time.PublishNowRedirectView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_not_allowed(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_getrequest(cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEqual(mockresponse.response.status_code, 405)

    def test_redirect(self):
        assignment = mommy.make('core.Assignment')
        self.mock_http302_postrequest(cradmin_role=assignment)

    def test_update_publishing_time_on_assignment(self):
        assignment = mommy.make('core.Assignment', publishing_time=datetime(2000, 1, 1))
        self.mock_http302_postrequest(cradmin_role=assignment)
        assignment = Assignment.objects.get(id=assignment.id)
        assignment_publishing_time_ignore_sec_and_ms = assignment.publishing_time.replace(second=0, microsecond=0)
        now_ignore_sec_and_ms = datetime.now().replace(second=0, microsecond=0)
        self.assertEquals(assignment_publishing_time_ignore_sec_and_ms, now_ignore_sec_and_ms)

    def test_update_publishing_time_on_correct_assignment(self):
        assignment1 = mommy.make('core.Assignment', publishing_time=datetime(2000, 1, 1))
        assignment2 = mommy.make('core.Assignment', publishing_time=datetime(2000, 1, 1))
        assignment3 = mommy.make('core.Assignment', publishing_time=datetime(2000, 1, 1))
        self.mock_http302_postrequest(cradmin_role=assignment3)
        assignment3 = Assignment.objects.get(id=assignment3.id)
        assignment1_publishing_time_ignore_ms = assignment1.publishing_time.replace(microsecond=0)
        assignment2_publishing_time_ignore_ms = assignment2.publishing_time.replace(microsecond=0)
        assignment3_publishing_time_ignore_ms = assignment3.publishing_time.replace(microsecond=0)
        now_ignore_ms = datetime.now().replace(second=assignment3.publishing_time.second, microsecond=0)
        self.assertEquals(assignment1_publishing_time_ignore_ms, datetime(2000, 1, 1))
        self.assertEquals(assignment2_publishing_time_ignore_ms, datetime(2000, 1, 1))
        self.assertEquals(assignment3_publishing_time_ignore_ms, now_ignore_ms)
