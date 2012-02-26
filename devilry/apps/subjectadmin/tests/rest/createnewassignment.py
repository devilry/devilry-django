from django.test import TestCase
from datetime import timedelta

from devilry.apps.core.testhelper import TestHelper
#from devilry.apps.subjectadmin.rest.errors import PermissionDeniedError
from devilry.apps.subjectadmin.rest.createnewassignment import CreateNewAssignmentDao


class TestRestCreateNewAssignmentDao(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)', 'p2'])
        self.testhelper.create_superuser("superuser")

    def test_create_assignment(self):
        dao = CreateNewAssignmentDao()
        publishing_time = self.testhelper.sub_p1.start_time + timedelta(days=1)
        assignment = dao._create_assignment(parentnode=self.testhelper.sub_p1,
                                            short_name='a1', long_name='Assignment 1',
                                            publishing_time=publishing_time,
                                            delivery_types=0, anonymous=False)
        self.assertEquals(assignment.short_name, 'a1')
        self.assertEquals(assignment.long_name, 'Assignment 1')
        self.assertEquals(assignment.publishing_time, publishing_time)
        self.assertEquals(assignment.delivery_types, 0)
        self.assertEquals(assignment.anonymous, False)

    def _create_related_student(self, username, candidate_id=None, tags=None):
        """
        Creates two related students on sub_p1: dewey, louie.
        dewey with candidate_id ``dew123``.
        """
        user = self.testhelper.create_user(username)
        relatedstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=user,
                                                                          candidate_id=candidate_id)
        if tags:
            relatedstudent.tags = tags
        return relatedstudent

    def test_create_group_from_relatedstudent(self):
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1')
        related_louie = self._create_related_student('louie')
        group = dao._create_group_from_relatedstudent(self.testhelper.sub_p1_a1, related_louie)
        self.assertEquals(group.candidates.all()[0].student.username, 'louie')
        self.assertEquals(group.candidates.all()[0].candidate_id, None)

        related_dewey = self._create_related_student('dewey', candidate_id='dew123',
                                                     tags='bb,aa')
        group = dao._create_group_from_relatedstudent(self.testhelper.sub_p1_a1, related_dewey)
        self.assertEquals(group.candidates.all()[0].candidate_id, 'dew123')
        tags = group.tags.all().order_by('tag')
        self.assertEquals(len(tags), 2)
        self.assertEquals(tags[0].tag, 'aa')
        self.assertEquals(tags[1].tag, 'bb')

    def test_add_all_relatedstudents(self):
        self._create_related_student('louie')
        self._create_related_student('dewey', candidate_id='dew123')
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1')

        self.assertEquals(self.testhelper.sub_p1_a1.assignmentgroups.count(), 0)
        deadline = self.testhelper.sub_p1_a1.publishing_time + timedelta(days=1)
        dao._add_all_relatedstudents(self.testhelper.sub_p1_a1, deadline)
        self.assertEquals(self.testhelper.sub_p1_a1.assignmentgroups.count(), 2)

        groups = list(self.testhelper.sub_p1_a1.assignmentgroups.all().order_by('candidates__student__username'))
        self.assertEquals(groups[0].candidates.all()[0].student.username, 'dewey')
        self.assertEquals(groups[0].candidates.all()[0].candidate_id, 'dew123')
        self.assertEquals(groups[1].candidates.all()[0].student.username, 'louie')
        self.assertEquals(groups[1].candidates.all()[0].candidate_id, None)

        self.assertEquals(groups[0].deadlines.all().count(), 1)
        self.assertEquals(groups[1].deadlines.all().count(), 1)
        self.assertEquals(groups[0].deadlines.all()[0].deadline, deadline)
