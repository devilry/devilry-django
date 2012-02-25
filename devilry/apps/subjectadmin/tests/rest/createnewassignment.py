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
