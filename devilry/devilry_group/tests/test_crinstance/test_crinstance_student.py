import mock
from django import test
from django.conf import settings
from model_mommy import mommy

from devilry.devilry_group.cradmin_instances import crinstance_student


class TestCrinstanceStudent(test.TestCase):

    def test_get_rolequeryset_publishing_time_in_future(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_middle', )
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_student.StudentCrInstance(request=mockrequest)
        self.assertEquals(0, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_one_assignment_group(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=mommy.make('core.AssignmentGroup'),)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_student.StudentCrInstance(request=mockrequest)
        self.assertEquals(1, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_multiple_assignment_groups(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=mommy.make('core.AssignmentGroup'),)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=mommy.make('core.AssignmentGroup'),)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=mommy.make('core.AssignmentGroup'),)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_student.StudentCrInstance(request=mockrequest)
        self.assertEquals(3, crinstance.get_rolequeryset().count())

    def test_get_rolequeryset_has_access_to_feedbackset(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=testgroup)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup,)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_student.StudentCrInstance(request=mockrequest)
        self.assertEquals(feedbackset, crinstance.get_rolequeryset()[0].feedbackset_set.all()[0])

    def test_get_rolequeryset_does_not_have_access_to_feedbackset(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        unrelated_feedbackset = mommy.make('devilry_group.FeedbackSet')
        mommy.make('devilry_group.FeedbackSet', group=testgroup)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup,)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        crinstance = crinstance_student.StudentCrInstance(request=mockrequest)
        self.assertNotEqual(unrelated_feedbackset, crinstance.get_rolequeryset()[0].feedbackset_set.all()[0])
