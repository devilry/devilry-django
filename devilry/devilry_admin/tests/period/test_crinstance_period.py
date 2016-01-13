from django.conf import settings
from django.test import TestCase, RequestFactory
from model_mommy import mommy

from devilry.devilry_admin.views.period import crinstance_period


class TestCrAdminInstance(TestCase):
    def test_get_rolequeryset_not_admin(self):
        request = RequestFactory().get('/test')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        request.user = testuser
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual(0, instance.get_rolequeryset().count())

    def test_get_rolequeryset_admin_on_period(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual([testperiod], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_admin_on_subject(self):
        testperiod = mommy.make('core.Period')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testperiod.subject)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual([testperiod], list(instance.get_rolequeryset()))
