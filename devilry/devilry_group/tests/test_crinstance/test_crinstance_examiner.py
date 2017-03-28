import mock
from django import test
from django.conf import settings
from model_mommy import mommy

from devilry.devilry_group.cradmin_instances import crinstance_examiner


class TestCrinstanceExaminer(test.TestCase):

    def test_get_titletext_for_role(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode__parentnode__short_name='s1',
                               parentnode__parentnode__short_name='p1',
                               parentnode__short_name='a1')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEqual('s1.p1 - a1', crinstance.get_titletext_for_role(testgroup))

    def test_get_rolequeryset_no_assignmentgroups_where_period_is_inactive_old(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_end')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment,)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEquals(0, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_one_assignmentgroup(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'),)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEquals(1, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_multiple_assignmentgroups(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'),)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'),)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'),)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEquals(3, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_has_access_to_feedbackset(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=testassignment)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group=testgroup)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup,)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEquals(feedbackset, crinstance.get_rolequeryset()[0].feedbackset_set.all()[0])

    def test_get_rolequeryset_does_not_have_access_to_feedbackset(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        unrelated_feedbackset = mommy.make('devilry_group.FeedbackSet')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup,)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertEqual(1, len(crinstance.get_rolequeryset()[0].feedbackset_set.all()))
        self.assertNotIn(unrelated_feedbackset, crinstance.get_rolequeryset()[0].feedbackset_set.all())

    def test_get_rolequeryset_access_to_multiple_assignment_groups_in_assignment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup',
                                parentnode=testassignment,
                                name='testgroup1')
        testgroup2 = mommy.make('core.AssignmentGroup',
                                parentnode=testassignment,
                                name='testgroup2')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1,)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2,)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        testgroups = [testgroup1, testgroup2]
        for group in testgroups:
            self.assertIn(group, crinstance.get_rolequeryset())

    def test_get_rolequeryset_access_to_multiple_assignment_groups_in_assignment_except_one(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment, name='testgroup1')
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment, name='testgroup2')
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment, name='testgroup3')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1,)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2,)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_examiner.ExaminerCrInstance(request=mockrequest)
        self.assertNotIn(testgroup3, crinstance.get_rolequeryset())
