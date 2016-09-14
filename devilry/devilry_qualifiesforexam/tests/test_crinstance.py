
# Django imports
from django import test

# Third party imports
import mock
from model_mommy import mommy

# Devilry imports
from devilry.devilry_qualifiesforexam.cradmin_instances import crinstance
from devilry.project.common import settings


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

    def test_admin_has_access(self):
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

    def test_admin_no_access(self):
        # testperiod_access should show up in the queryset.
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        testadmin = mommy.make(settings.AUTH_USER_MODEL)

        mockrequest = mock.MagicMock()
        mockrequest.cradmin_role = testperiod
        mockrequest.user = testadmin
        testcrinstance = crinstance.CrInstance(request=mockrequest)
        rolequeryset = testcrinstance.get_rolequeryset()

        self.assertEquals(0, len(rolequeryset))

    # def test_get_rolequeryset_num_queries(self):
    #     testsubject = mommy.make('core.Subject', short_name='Duck1010')
    #     testperiod1 = mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
    #     testassignment1 = mommy.make('core.Assignment', parentnode=testperiod1, short_name='Assignment1')
    #     testassignment2 = mommy.make('core.Assignment', parentnode=testperiod1, short_name='Assignment2')
    #     testassignment3 = mommy.make('core.Assignment', parentnode=testperiod1, short_name='Assignment3')
    #     mommy.make('core.Candidate',
    #                assignment_group__parentnode=testassignment1,
    #                relatedstudent__period=testperiod1,
    #                _quantity=20)
    #     mommy.make('core.Candidate',
    #                assignment_group__parentnode=testassignment2,
    #                relatedstudent__period=testperiod1,
    #                _quantity=20)
    #     mommy.make('core.Candidate',
    #                assignment_group__parentnode=testassignment3,
    #                relatedstudent__period=testperiod1,
    #                _quantity=20)
    #
    #     mockrequest = mock.MagicMock()
    #     mockrequest.cradmin_role = testperiod1
    #     testcrinstance = crinstance.CrInstance(request=mockrequest)
    #
    #     with self.assertNumQueries(6):
    #         rolequeryset = testcrinstance.get_rolequeryset()
    #
    #         for period in rolequeryset.all():
    #             for assignment in period.assignments.all():
    #                 for assignmentgroup in assignment.assignmentgroups.all():
    #                     # candidates = assignmentgroup.candidates.all()
    #                     for candidate in assignmentgroup.candidates.all():
    #                         print candidate
