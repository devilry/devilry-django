import mock
from django import test
from django.conf import settings
from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.cradmin_instances import crinstance_student
from devilry.devilry_group.models import FeedbackSet


class TestCrinstanceStudent(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_rolequeryset_publishing_time_in_future(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_middle', )
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_student.StudentCrInstance(request=mockrequest)
        self.assertEqual(0, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_one_assignment_group(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=baker.make('core.AssignmentGroup'),)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_student.StudentCrInstance(request=mockrequest)
        self.assertEqual(1, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_multiple_assignment_groups(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=baker.make('core.AssignmentGroup'),)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=baker.make('core.AssignmentGroup'),)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=baker.make('core.AssignmentGroup'),)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_student.StudentCrInstance(request=mockrequest)
        self.assertEqual(3, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_has_access_to_feedbackset(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup')
        feedbackset = FeedbackSet.objects.get(group=testgroup)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_student.StudentCrInstance(request=mockrequest)
        self.assertEqual(feedbackset, crinstance.get_rolequeryset()[0].feedbackset_set.all()[0])

    def test_get_rolequeryset_does_not_have_access_to_feedbackset(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup')
        unrelated_feedbackset = baker.make('devilry_group.FeedbackSet')
        baker.make('devilry_group.FeedbackSet', group=testgroup)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup,)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_student.StudentCrInstance(request=mockrequest)
        self.assertNotEqual(unrelated_feedbackset, crinstance.get_rolequeryset()[0].feedbackset_set.all()[0])
