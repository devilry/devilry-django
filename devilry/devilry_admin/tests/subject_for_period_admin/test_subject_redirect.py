

import mock
from django.conf import settings
from django.http import Http404
from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_admin.views.subject_for_period_admin import subject_redirect


class TestSubjectRedirect(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = subject_redirect.SubjectRedirectView

    def test_404(self):
        testsubject = baker.make('core.Subject')
        with self.assertRaises(Http404):
            self.mock_http302_getrequest(cradmin_role=testsubject)

    def test_user_is_not_periodadmin_or_subjectadmin(self):
        testsubject = baker.make('core.Subject')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        with self.assertRaises(Http404):
            self.mock_http302_getrequest(cradmin_role=testsubject, requestuser=testuser)

    def test_redirect_to_overview_for_periodadmin(self):
        testperiod = baker.make('core.Period')
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup', period=testperiod)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        mock_cradmin_instance = mock.MagicMock()
        self.mock_http302_getrequest(
            cradmin_role=testperiod.parentnode,
            cradmin_instance=mock_cradmin_instance,
            requestuser=testuser
        )
        mock_cradmin_instance.rolefrontpage_url.assert_called_once_with(roleid=testperiod.parentnode.id)

    def test_redirect_to_overview_for_subject_admins(self):
        testsubject = baker.make('core.Subject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup', subject=testsubject)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        mockresponse = self.mock_http302_getrequest(cradmin_role=testsubject, requestuser=testuser)
        self.assertEqual('/devilry_admin/subject/{}/overview/'.format(testsubject.id), mockresponse.response.url)
