from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import AssignmentGroup


from devilry.apps.subjectadmin.rest.errors import PermissionDeniedError
from devilry.apps.subjectadmin.rest.group import GroupDao



class TestGroupDao(TestCase):
    def create_testdata(self):
        testhelper = TestHelper()
        testhelper.add(nodes='uni',
                       subjects=['duck1010'],
                       periods=['firstsem'],
                       assignments=['a1:admin(a1admin)', 'a2:admin(a2admin)'])
        testhelper.create_superuser("superuser")

        for num in xrange(3):
            path = 'uni;duck1010.firstsem.a1.g{num}:candidate(student{num}):examiner(examiner1).d1'
            testhelper.add_to_path(path.format(**vars()))
            group = getattr(testhelper, 'duck1010_firstsem_a1_g{0}'.format(num))
            group.tags.create(tag="stuff")
            group.tags.create(tag="lownumber")
            delivery = testhelper.add_delivery(group)
            testhelper.add_feedback(delivery,
                                    verdict=dict(grade='A', points=100, is_passing_grade=True))
        return testhelper

    def test_read_permissiondenied(self):
        testhelper = self.create_testdata()
        assignment1 = testhelper.duck1010_firstsem_a1
        with self.assertRaises(PermissionDeniedError):
            GroupDao().list(testhelper.a2admin, assignment1.id)

    def test_read(self):
        testhelper = self.create_testdata()
        assignment1 = testhelper.duck1010_firstsem_a1
        groups = GroupDao().list(testhelper.a1admin, assignment1.id)
        # We only check a few values here. The most important thing is that the
        # database queries are sane, since the other stuff is tested in
        # smaller units
        self.assertEquals(len(groups), 3)
        self.assertTrue('examiners' in groups[0].keys())
        self.assertTrue('students' in groups[0].keys())
        self.assertTrue('deadlines' in groups[0].keys())
        fields = set(['id', 'name', 'is_open', 'feedback__grade', 'feedback__points',
                      'feedback__is_passing_grade', 'feedback__save_timestamp',
                      'examiners', 'students', 'tags', 'deadlines'])
        self.assertEquals(set(groups[0].keys()), fields)
        self.assertEquals(AssignmentGroup.objects.get(id=groups[0]['id']).parentnode_id,
                          assignment1.id)

    def test_merge(self):
        groups = [{'id': 1, 'name': 'Group1'}]
        candidates = [{'assignment_group_id': 1, 'username': 'stud'}]
        examiners = [{'assignmentgroup_id': 1, 'username': 'exam'}]
        tags = [{'assignment_group_id': 1, 'tag': 'important'}]
        deadlines = [{'assignment_group_id': 1, 'deadline': 'now'}]
        groups = GroupDao()._merge(groups, candidates, examiners, tags, deadlines)
        self.assertEquals(groups,
                          [{'id': 1,
                            'name': 'Group1',
                            'students': [{'username': 'stud'}],
                            'examiners': [{'username': 'exam'}],
                            'tags': [{'tag': 'important'}],
                            'deadlines': [{'deadline': 'now'}]
                           }])

    def test_get_groups(self):
        testhelper = self.create_testdata()
        assignment1 = testhelper.duck1010_firstsem_a1
        groups = GroupDao()._get_groups(assignment1.id)
        self.assertEquals(len(groups), 3)
        first = groups[0]
        fields = set(['id', 'name', 'is_open', 'feedback__grade', 'feedback__points',
                      'feedback__is_passing_grade', 'feedback__save_timestamp'])
        self.assertEquals(set(first.keys()), fields)

    def test_prepare_group(self):
        self.assertEquals(GroupDao()._prepare_group({}),
                          {'tags': [],
                           'students': [],
                           'examiners': [],
                           'deadlines': []})

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
        GroupDao()._merge_with_groupsdict(groupsdict, people, 'people')
        self.assertEquals(groupsdict, expected)
