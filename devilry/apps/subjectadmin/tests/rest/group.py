from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.subjectadmin.rest.group import (assignmentadmin_required,
                                                  AssignmentadminRequiredError,
                                                  GroupDao)


class TestAssignmentAdminRequired(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['duck1010'],
                            periods=['firstsem'],
                            assignments=['a1:admin(a1admin)', 'a2'])
        self.testhelper.create_superuser("superuser")
        self.assignment1 = self.testhelper.duck1010_firstsem_a1
        self.assignment2 = self.testhelper.duck1010_firstsem_a2

    def test_assignmentadmin_required_superuser(self):
        assignmentadmin_required(self.testhelper.superuser, "", None) # Calls is_superuser and exits without further checks

    def test_assignmentadmin_required_normaluser(self):
        assignmentadmin_required(self.testhelper.a1admin, "",
                                 self.assignment1.id)

    def test_assignmentadmin_required_normaluser_denied(self):
        self.assertRaises(AssignmentadminRequiredError,
                          assignmentadmin_required, self.testhelper.a1admin,
                          "", self.assignment2.id)


class TestGroupDao(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['duck1010'],
                            periods=['firstsem'],
                            assignments=['a1:admin(a1admin)', 'a2'])
        self.testhelper.create_superuser("superuser")
        self.assignment1 = self.testhelper.duck1010_firstsem_a1
        self.assignment2 = self.testhelper.duck1010_firstsem_a2

        for num in xrange(10):
            path = 'uni;duck1010.firstsem.a1.g{num}:candidate(student{num}):examiner(examiner1).d1'
            self.testhelper.add_to_path(path.format(**vars()))
            group = getattr(self.testhelper, 'duck1010_firstsem_a1_g{0}'.format(num))
            group.tags.create(tag="stuff")
            if num < 5:
                group.tags.create(tag="lownumber")
            delivery = self.testhelper.add_delivery(group)
            self.testhelper.add_feedback(delivery,
                                         verdict=dict(grade='A', points=100, is_passing_grade=True))

        self.groupdao = GroupDao()

    def test_read(self):
        self.groupdao.read(self.testhelper.a1admin, self.assignment1.id)

    def test_get_groups(self):
        groups = self.groupdao._get_groups(self.assignment1.id)
        self.assertEquals(len(groups), 10)
        first = groups[0]
        fields = set(['id', 'name', 'is_open', 'feedback__grade', 'feedback__points',
                      'feedback__is_passing_grade', 'feedback__save_timestamp'])
        self.assertEquals(set(first.keys()), fields)

    def test_prepare_group(self):
        self.assertEquals(self.groupdao._prepare_group({}), {'tags': []})

    def test_merge_tags_with_groupsdict(self):
        tags =[{'assignment_group_id': 1, 'tag': 'test'},
               {'assignment_group_id': 1, 'tag': 'test2'},
               {'assignment_group_id': 3, 'tag': 'test'}]
        groupsdict = {1: {'tags': []},
                      2: {'tags': []},
                      3: {'tags': []}}
        expected = {1: {'tags': ['test', 'test2']},
                    2: {'tags': []},
                    3: {'tags': ['test']}}
        self.groupdao._merge_tags_with_groupsdict(tags, groupsdict)
        self.assertEquals(groupsdict, expected)

    def test_merge_with_groupsdict(self):
        people =[{'assignment_group_id': 1, 'name': 'test'},
                 {'assignment_group_id': 1, 'name': 'test2'},
                 {'assignment_group_id': 3, 'name': 'test3'}]
        groupsdict = {1: {'people': []},
                      2: {'people': []},
                      3: {'people': []}}
        expected = {1: {'people': [{'name':'test'}, {'name':'test2'}]},
                    2: {'people': []},
                    3: {'people': [{'name':'test3'}]}}
        self.groupdao._merge_with_groupsdict(groupsdict, people, 'people')
        self.assertEquals(groupsdict, expected)
