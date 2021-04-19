import mock
from django import test
from django.conf import settings
from model_bakery import baker

from devilry.devilry_examiner.views.assignment import crinstance_assignment


class TestCradminInstanceAssignment(test.TestCase):
    def test_get_rolequeryset_not_groups_where_period_is_inactive_old(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_oldperiod_end')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_assignment.CrAdminInstance(request=mockrequest)
        self.assertEqual(0, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_not_groups_where_period_is_inactive_future(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_futureperiod_start')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_assignment.CrAdminInstance(request=mockrequest)
        self.assertEqual(0, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_not_groups_where_period_is_active_but_assignment_not_published(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_assignment.CrAdminInstance(request=mockrequest)
        self.assertEqual(0, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_groups_where_period_is_active_and_assignment_is_published(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_assignment.CrAdminInstance(request=mockrequest)
        self.assertEqual(1, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_distinct(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_assignment.CrAdminInstance(request=mockrequest)
        self.assertEqual(1, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_uses_prefetch_point_to_grade_map(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_assignment.CrAdminInstance(request=mockrequest)
        assignment = crinstance.get_rolequeryset().first()
        self.assertTrue(hasattr(assignment, 'prefetched_point_to_grade_map'))
