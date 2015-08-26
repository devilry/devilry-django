from django import test

from devilry.apps.core import testhelper
from devilry.devilry_group.cradmin_instances.crinstance_student import StudentCrInstance
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, NodeBuilder, \
    FeedbackSetBuilder
from devilry.project.develop.testhelpers.datebuilder import DateTimeBuilder


class TestCrinstanceStudent(test.TestCase):
    def setUp(self):
        self.testhelper = testhelper.TestHelper()
        self.factory = test.RequestFactory()
        self.request = self.factory.get('/test/')
        self.cr_instance = StudentCrInstance(self.request)
        self.comment_text = 'Lorem ipsum I dont know it from memory bla bla bla..'

    def test_getrolequeryset_for_user(self):
        testuser = self.testhelper.create_user('testuser')
        examiner = UserBuilder('donald', full_name='Donald Duck').user

        FeedbackSetBuilder\
            .quickadd_ducku_duck1010_active_assignment1_group_feedbackset(studentuser=testuser, examiner=examiner)

        self.cr_instance.request.user = testuser
        rolequeryset = self.cr_instance.get_rolequeryset()
        assignmentgroups = rolequeryset.all()

        self.assertEqual(1, assignmentgroups.count())

    def test_getrolequeryset_for_wrong_user(self):
        testuser = self.testhelper.create_user('testuser')
        wrong_user = self.testhelper.create_user('wrong_user')
        examiner = UserBuilder('donald', full_name='Donald Duck').user

        FeedbackSetBuilder\
            .quickadd_ducku_duck1010_active_assignment1_group_feedbackset(studentuser=testuser, examiner=examiner)

        self.cr_instance.request.user = wrong_user
        rolequeryset = self.cr_instance.get_rolequeryset()
        assignmentgroups = rolequeryset.all()

        self.assertEqual(0, assignmentgroups.count())

    def test_getrolequeryset_multiple_groups_user(self):
        testuser = self.testhelper.create_user('testuser')
        examiner = UserBuilder('donald', full_name='Donald Duck').user
        NodeBuilder('ducku')\
            .add_subject('duck1100')\
            .add_6month_active_period()\
            .add_assignment('advanced duck')\
            .add_group().add_students(testuser)\
            .add_feedback_set(
                points=10,
                published_by=examiner,
                created_by=examiner,
                deadline_datetime=DateTimeBuilder.now().minus(weeks=4))\
            .add_groupcomment(
                user=testuser,
                user_role='student',
                instant_publish=True,
                visible_for_students=True,
                text=self.comment_text,
                published_datetime=DateTimeBuilder.now().minus(weeks=4, days=3, hours=10))

        NodeBuilder('ducku')\
            .add_subject('duck1000')\
            .add_6month_active_period()\
            .add_assignment('learn to duck')\
            .add_group().add_students(testuser)\
            .add_feedback_set(
                points=10,
                published_by=examiner,
                created_by=examiner,
                deadline_datetime=DateTimeBuilder.now().minus(weeks=4))\
            .add_groupcomment(
                user=testuser,
                user_role='student',
                instant_publish=True,
                visible_for_students=True,
                text=self.comment_text,
                published_datetime=DateTimeBuilder.now().minus(weeks=4, days=3, hours=10))

        self.cr_instance.request.user = testuser
        rolequeryset = self.cr_instance.get_rolequeryset()
        assignmentgroups = rolequeryset.all()

        self.assertEqual(2, assignmentgroups.count())
