
# Django imports
from django import test

# Third party imports
import mock
from model_mommy import mommy

# Devilry imports
from devilry.project.common import settings
from devilry.devilry_qualifiesforexam.cradmin_instances import crinstance


class TestCrInstance(test.TestCase):

    def test_superuser_always_access(self):
        # Tests that a superuser has access to queryset without being in a permissiongroup.
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        testadmin = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)

        mockrequest = mock.MagicMock()
        mockrequest.cradmin_role = testperiod
        mockrequest.user = testadmin
        testcrinstance = crinstance.CrInstance(request=mockrequest)
        rolequeryset = testcrinstance.get_rolequeryset()

        self.assertEquals(1, len(rolequeryset))
        self.assertIn(testperiod, rolequeryset)

    def test_admin_on_period(self):
        # testperiod_access should show up in the queryset.
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        testadmin = mommy.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup', period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testadmin,
                   permissiongroup=periodpermissiongroup.permissiongroup)

        mockrequest = mock.MagicMock()
        mockrequest.cradmin_role = testperiod
        mockrequest.user = testadmin
        testcrinstance = crinstance.CrInstance(request=mockrequest)
        rolequeryset = testcrinstance.get_rolequeryset()

        self.assertEquals(1, len(rolequeryset))
        self.assertIn(testperiod, rolequeryset)

    def test_admin_not_admin_on_period(self):
        # testperiod_access should show up in the queryset.
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        testadmin = mommy.make(settings.AUTH_USER_MODEL)

        mockrequest = mock.MagicMock()
        mockrequest.cradmin_role = testperiod
        mockrequest.user = testadmin
        testcrinstance = crinstance.CrInstance(request=mockrequest)
        rolequeryset = testcrinstance.get_rolequeryset()

        self.assertEquals(0, len(rolequeryset))

    def test_get_rolequeryset_num_queries(self):
        # User is admin on two subjects the same semester.
        # CrInstance.get_rolequeryset() filters the period the admin has access to and joins the
        # related subject with select_related.
        testsubject1 = mommy.make('core.Subject', short_name='Duck1010')
        testsubject2 = mommy.make('core.Subject', short_name='Duck1100')
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject1)
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject2)

        testadmin = mommy.make(settings.AUTH_USER_MODEL)
        subjectpermissiongroup1 = mommy.make('devilry_account.SubjectPermissionGroup', subject=testsubject1)
        subjectpermissiongroup2 = mommy.make('devilry_account.SubjectPermissionGroup', subject=testsubject2)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testadmin,
                   permissiongroup=subjectpermissiongroup1.permissiongroup)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testadmin,
                   permissiongroup=subjectpermissiongroup2.permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testadmin
        testcrinstance = crinstance.CrInstance(request=mockrequest)
        with self.assertNumQueries(1):
            rolequeryset = testcrinstance.get_rolequeryset()
            # Iterate to evaluate the number of queries
            subjects = [testsubject1, testsubject2]
            for period in rolequeryset.all():
                self.assertIn(period.parentnode, subjects)
