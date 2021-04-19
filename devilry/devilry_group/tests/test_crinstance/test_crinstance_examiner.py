import mock
from django import test
from django.conf import settings
from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.cradmin_instances import crinstance_examiner
from devilry.devilry_group.models import FeedbackSet


class TestCrinstanceExaminer(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_titletext_for_role(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__parentnode__parentnode__short_name='s1',
                               parentnode__parentnode__short_name='p1',
                               parentnode__short_name='a1')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEqual('s1.p1 - a1', crinstance.get_titletext_for_role(testgroup))

    def test_get_rolequeryset_no_assignmentgroups_where_period_is_inactive_old(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_oldperiod_end')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment,)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEqual(0, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_one_assignmentgroup(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'),)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEqual(1, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_multiple_assignmentgroups(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'),)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'),)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'),)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEqual(3, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_has_access_to_feedbackset(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=testassignment)
        feedbackset = FeedbackSet.objects.get(group=testgroup)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEqual(feedbackset, crinstance.get_rolequeryset()[0].feedbackset_set.all()[0])

    def test_get_rolequeryset_does_not_have_access_to_feedbackset(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        unrelated_feedbackset = baker.make('devilry_group.FeedbackSet')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEqual(1, len(crinstance.get_rolequeryset()[0].feedbackset_set.all()))
        self.assertNotIn(unrelated_feedbackset, crinstance.get_rolequeryset()[0].feedbackset_set.all())

    def test_get_rolequeryset_access_to_multiple_assignment_groups_in_assignment(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = baker.make('core.AssignmentGroup',
                                parentnode=testassignment,
                                name='testgroup1')
        testgroup2 = baker.make('core.AssignmentGroup',
                                parentnode=testassignment,
                                name='testgroup2')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1,)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2,)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        testgroups = [testgroup1, testgroup2]
        for group in testgroups:
            self.assertIn(group, crinstance.get_rolequeryset())

    def test_get_rolequeryset_access_to_multiple_assignment_groups_in_assignment_except_one(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment, name='testgroup1')
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment, name='testgroup2')
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment, name='testgroup3')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1,)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2,)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertNotIn(testgroup3, crinstance.get_rolequeryset())
