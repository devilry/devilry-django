from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.subjectadmin.rest.group import (assignmentadmin_required,
                                                  AssignmentadminRequiredError)


class TestAssignmentAdminRequired(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['duck1010'],
                            periods=['firstsem'],
                            assignments=['a1:admin(normaluser)', 'a2'])
        self.testhelper.create_superuser("superuser")
        self.assignment1 = self.testhelper.duck1010_firstsem_a1
        self.assignment2 = self.testhelper.duck1010_firstsem_a2

    def test_assignmentadmin_required_superuser(self):
        assignmentadmin_required(self.testhelper.superuser, "", None) # Calls is_superuser and exits without further checks

    def test_assignmentadmin_required_normaluser(self):
        assignmentadmin_required(self.testhelper.normaluser, "",
                                 self.assignment1.id)

    def test_assignmentadmin_required_normaluser_denied(self):
        self.assertRaises(AssignmentadminRequiredError,
                          assignmentadmin_required, self.testhelper.normaluser,
                          "", self.assignment2.id)
