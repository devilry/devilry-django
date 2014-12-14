from datetime import datetime, timedelta

from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient
from devilry.apps.core.models import Deadline
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_rest.serializehelpers import format_datetime
from devilry.devilry_subjectadmin.rest.deadlinesbulk import encode_bulkdeadline_id
from devilry.devilry_subjectadmin.rest.deadlinesbulk import decode_bulkdeadline_id
from devilry.devilry_subjectadmin.rest.deadlinesbulk import sha1hash


class TestRestDeadlinesBulkList(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-2)'], # 2 months ago
                            assignments=['a1:admin(adm):pub(0)']) # 0 days after period begins
        self.client = RestClient()
        self.url = '/devilry_subjectadmin/rest/deadlinesbulk/{0}/'.format(self.testhelper.sub_p1_a1.id)

    def _listas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def test_get_empty(self):
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)

    def test_get_simple(self):
        for groupnum in xrange(3):
            # deadline 5 days after assignment starts
            self.testhelper.add_to_path('uni;sub.p1.a1.g{0}.d1:ends(5)'.format(groupnum))
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        d1 = content[0]
        self.assertEquals(set(d1.keys()),
                          set(['deadline', 'text', 'groups', 'offset_from_now',
                               'in_the_future', 'bulkdeadline_id', 'url', 'groups']))
        self.assertEquals(len(d1['groups']), 3)
        self.assertEquals(d1['in_the_future'], False)
        self.assertEquals(d1['text'], None)

    def test_get_textdifference(self):
        for groupnum in xrange(3):
            # deadline 5 days after assignment starts
            self.testhelper.add_to_path('uni;sub.p1.a1.g{0}.d1:ends(5)'.format(groupnum))
        # Change text on g1_d1, which should make it a separate entry in the list
        self.testhelper.sub_p1_a1_g1_d1.text = 'Test'
        self.testhelper.sub_p1_a1_g1_d1.save()
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)
        g2_g3_d1 = content[0]
        g1_d1 = content[1]
        self.assertEquals(g1_d1['text'], 'Test')
        self.assertEquals(len(g1_d1['groups']), 1)
        self.assertEquals(g2_g3_d1['text'], None)
        self.assertEquals(len(g2_g3_d1['groups']), 2)

    def test_get_multiple_and_order(self):
        for groupnum in xrange(3):
            # deadline 5 days after assignment starts
            self.testhelper.add_to_path('uni;sub.p1.a1.g{0}.d1:ends(5)'.format(groupnum))
        for groupnum in xrange(2):
            # deadline 70 days after assignment starts, which should be in the future
            self.testhelper.add_to_path('uni;sub.p1.a1.g{0}.d2:ends(70)'.format(groupnum))
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)
        d1 = content[1]
        d2 = content[0]
        self.assertEquals(len(d1['groups']), 3)
        self.assertEquals(d1['in_the_future'], False)
        self.assertEquals(len(d2['groups']), 2)
        self.assertEquals(d2['in_the_future'], True)

    def test_get_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._listas('nobody')
        self.assertEquals(response.status_code, 403)



class TestRestDeadlinesBulkCreate(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-2)']) # 2 months ago 
        self.testhelper.sub_p1.start_time = datetime(2000, 1, 1, 22, 30, 49)
        self.testhelper.sub_p1.save()
        self.testhelper.add_to_path('uni;sub.p1.a1:admin(adm):pub(0)') # 0 days after period begins + 2 sec
        self.client = RestClient()

        for groupnum in xrange(3):
            # deadline 5 days after assignment starts
            self.testhelper.add_to_path('uni;sub.p1.a1.g{0}:candidate(cand1):examiner(exam1).d1:ends(5)'.format(groupnum))


    def _geturl(self):
        return '/devilry_subjectadmin/rest/deadlinesbulk/{0}/'.format(self.testhelper.sub_p1_a1.id)

    def _postas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_post(self._geturl(), data)

    def _itergroups(self):
        for groupnum in xrange(3):
            group_id = getattr(self.testhelper, 'sub_p1_a1_g{0}'.format(groupnum)).id
            group = AssignmentGroup.objects.get(id=group_id)
            yield group

    def test_post_no_matching_groups(self):
        for group in self._itergroups():
            deadlines = group.deadlines.all().order_by('-deadline')
            self.assertEquals(group.feedback, None)
        new_deadline = datetime(2004, 12, 24, 20, 30)
        content, response = self._postas('adm', {'deadline': format_datetime(new_deadline),
                                                 'text': 'Created',
                                                 'createmode': 'failed'})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(content['field_errors']['createmode'], ['The given option did not match any groups.'])

    def test_post_createmode_failed(self):
        self.testhelper.add_delivery('sub.p1.a1.g1', {'bad.py': ['print ', 'bah']})
        self.testhelper.add_feedback('sub.p1.a1.g1', verdict={'grade': 'F', 'points': 30, 'is_passing_grade': False})
        g1 = AssignmentGroup.objects.get(id=self.testhelper.sub_p1_a1_g1.id)
        self.assertFalse(g1.is_open)


        new_deadline = datetime(2004, 12, 24, 20, 30)
        self.assertEquals(Deadline.objects.filter(deadline=new_deadline).count(), 0)
        content, response = self._postas('adm', {'deadline': format_datetime(new_deadline),
                                                 'text': 'Created',
                                                 'createmode': 'failed'})

        # Check response
        self.assertEquals(response.status_code, 201)
        self.assertEquals(decode_bulkdeadline_id(content['bulkdeadline_id'])[0],
                          new_deadline)
        self.assertEquals(len(content['groups']), 1)
        self.assertEquals(content['text'], 'Created')
        self.assertEquals(content['deadline'], format_datetime(new_deadline))

        # Check actual data
        self.assertEquals(Deadline.objects.filter(deadline=new_deadline).count(), 1)
        g1 = AssignmentGroup.objects.get(id=self.testhelper.sub_p1_a1_g1.id)
        deadlines = g1.deadlines.all().order_by('-deadline')
        self.assertEquals(len(deadlines), 2)
        self.assertEquals(deadlines[0].deadline, new_deadline)
        self.assertEquals(deadlines[0].text, 'Created')
        self.assertTrue(g1.is_open) # Group was automatically opened in devilry.apps.core.models.Deadline.save()

    def test_post_createmode_failed_or_no_feedback(self):
        # Fail g0
        self.testhelper.add_delivery('sub.p1.a1.g0', {'bad.py': ['print ', 'bah']})
        self.testhelper.add_feedback('sub.p1.a1.g0', verdict={'grade': 'F', 'points': 30, 'is_passing_grade': False})
        # Pass g1
        self.testhelper.add_delivery('sub.p1.a1.g1', {'good.py': ['print ', 'bah']})
        self.testhelper.add_feedback('sub.p1.a1.g1', verdict={'grade': 'A', 'points': 100, 'is_passing_grade': True})
        # g2 has no feedback
        self.assertEquals(self.testhelper.sub_p1_a1_g2.feedback, None)

        new_deadline = datetime(2004, 12, 24, 20, 30)
        self.assertEquals(Deadline.objects.filter(deadline=new_deadline).count(), 0)
        content, response = self._postas('adm', {'deadline': format_datetime(new_deadline),
                                                 'text': 'Created',
                                                 'createmode': 'failed-or-no-feedback'})

        # Check response
        self.assertEquals(response.status_code, 201)
        self.assertEquals(len(content['groups']), 2)

        # Check actual data
        self.assertEquals(Deadline.objects.filter(deadline=new_deadline).count(), 2)
        g0 = self.testhelper.sub_p1_a1_g0
        g2 = self.testhelper.sub_p1_a1_g2
        for group in (g0, g2):
            deadlines = group.deadlines.all().order_by('-deadline')
            self.assertEquals(len(deadlines), 2)
            self.assertEquals(deadlines[0].deadline, new_deadline)
            self.assertEquals(deadlines[0].text, 'Created')
        g1 = self.testhelper.sub_p1_a1_g1
        self.assertEquals(g1.deadlines.count(), 1) # We did not a deadline to g1 because they have passing grade

    def test_post_createmode_no_deadlines(self):
        self.assertEquals(self.testhelper.sub_p1_a1_g1.deadlines.count(), 1)
        self.testhelper.add_to_path('uni;sub.p1.a1.extragroup')
        self.assertEquals(self.testhelper.sub_p1_a1_extragroup.deadlines.count(), 0)

        new_deadline = datetime(2004, 12, 24, 20, 30)
        self.assertEquals(Deadline.objects.filter(deadline=new_deadline).count(), 0)
        content, response = self._postas('adm', {'deadline': format_datetime(new_deadline),
                                                 'text': 'Created',
                                                 'createmode': 'no-deadlines'})

        # Check response
        self.assertEquals(response.status_code, 201)
        self.assertEquals(decode_bulkdeadline_id(content['bulkdeadline_id'])[0],
                          new_deadline)
        self.assertEquals(len(content['groups']), 1)
        self.assertEquals(content['text'], 'Created')
        self.assertEquals(content['deadline'], format_datetime(new_deadline))

        # Check actual data
        self.assertEquals(Deadline.objects.filter(deadline=new_deadline).count(), 1)
        extragroup = AssignmentGroup.objects.get(id=self.testhelper.sub_p1_a1_extragroup.id)
        deadlines = extragroup.deadlines.all()
        self.assertEquals(len(deadlines), 1)
        self.assertEquals(deadlines[0].deadline, new_deadline)
        self.assertEquals(deadlines[0].text, 'Created')
        self.assertTrue(extragroup.is_open) # Group was automatically opened in devilry.apps.core.models.Deadline.save()

    def test_post_createmode_specific_groups(self):
        self.assertEquals(self.testhelper.sub_p1_a1_g1.deadlines.count(), 1)
        self.assertEquals(self.testhelper.sub_p1_a1_g2.deadlines.count(), 1)

        new_deadline = datetime(2004, 12, 24, 20, 30)
        self.assertEquals(Deadline.objects.filter(deadline=new_deadline).count(), 0)
        content, response = self._postas('adm', {'deadline': format_datetime(new_deadline),
                                                 'text': 'Created',
                                                 'group_ids': [self.testhelper.sub_p1_a1_g1.id,
                                                               self.testhelper.sub_p1_a1_g2.id],
                                                 'createmode': 'specific-groups'})

        # Check response
        self.assertEquals(response.status_code, 201)
        self.assertEquals(decode_bulkdeadline_id(content['bulkdeadline_id'])[0],
                          new_deadline)
        self.assertEquals(len(content['groups']), 2)
        self.assertEquals(content['text'], 'Created')
        self.assertEquals(content['deadline'], format_datetime(new_deadline))

        # Check actual data
        self.assertEquals(Deadline.objects.filter(deadline=new_deadline).count(), 2)
        g1 = self.testhelper.reload_from_db(self.testhelper.sub_p1_a1_g1)
        deadlines = g1.deadlines.all()
        self.assertEquals(len(deadlines), 2)
        self.assertEquals(deadlines[0].deadline, new_deadline)
        self.assertEquals(deadlines[0].text, 'Created')

    def test_post_createmode_specific_groups_nogroups(self):
        new_deadline = datetime(2004, 12, 24, 20, 30)
        self.assertEquals(Deadline.objects.filter(deadline=new_deadline).count(), 0)
        content, response = self._postas('adm', {'deadline': format_datetime(new_deadline),
                                                 'text': 'Created',
                                                 'createmode': 'specific-groups'})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(content['field_errors']['group_ids'][0],
                          '``group_ids`` is required when ``createmode=="specific-groups"``.')

    def test_post_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._postas('nobody', {})
        self.assertEquals(response.status_code, 403)




class TestRestDeadlinesBulkUpdateReadOrDelete(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-2)']) # 2 months ago 
        self.testhelper.sub_p1.start_time = datetime(2000, 1, 1, 22, 30, 49)
        self.testhelper.sub_p1.save()
        self.testhelper.add_to_path('uni;sub.p1.a1:admin(adm):pub(0)') # 0 days after period begins + 2 sec
        self.client = RestClient()

        for groupnum in xrange(3):
            # deadline 5 days after assignment starts
            self.testhelper.add_to_path('uni;sub.p1.a1.g{0}:candidate(cand1):examiner(exam1).d1:ends(5)'.format(groupnum))


    def _geturl(self, deadline=None):
        deadline = deadline or self.testhelper.sub_p1_a1_g1_d1
        bulkdeadline_id = encode_bulkdeadline_id(deadline)
        return '/devilry_subjectadmin/rest/deadlinesbulk/{0}/{1}'.format(self.testhelper.sub_p1_a1.id,
                                                                         bulkdeadline_id)

    def test_encode_unique_bulkdeadline_id(self):
        d = Deadline(deadline=datetime(2000, 12, 24, 22, 30, 49))
        self.assertEquals(encode_bulkdeadline_id(d),
                          '2000-12-24T22_30_49--')
        d.text = 'Hello world'
        self.assertEquals(encode_bulkdeadline_id(d),
                          '2000-12-24T22_30_49--{0}'.format(sha1hash('Hello world')))
        # Ensure unicode works
        d.text = u'\u00e5ello world'
        self.assertEquals(encode_bulkdeadline_id(d),
                          '2000-12-24T22_30_49--{0}'.format(sha1hash(u'\u00e5ello world')))


    def test_decode_unique_bulkdeadline_id(self):
        self.assertEquals(decode_bulkdeadline_id('2000-12-24T22_30_49--'),
                          (datetime(2000, 12, 24, 22, 30, 49), ''))
        self.assertEquals(decode_bulkdeadline_id('2000-12-24T22_30_49--{0}'.format(sha1hash('Hello world'))),
                          (datetime(2000, 12, 24, 22, 30, 49), sha1hash('Hello world')))


    def _putas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_put(self._geturl(), data)

    def test_put(self):
        self.assertEquals(self.testhelper.sub_p1_a1.publishing_time, datetime(2000, 1, 1, 22, 30, 51))
        self.assertEquals(self.testhelper.sub_p1_a1_g1_d1.deadline,
                          datetime(2000, 1, 1, 22, 30) + timedelta(days=5))

        new_deadline = datetime(2004, 12, 24, 20, 30)
        content, response = self._putas('adm', {'deadline': format_datetime(new_deadline),
                                                'text': 'Hello'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(decode_bulkdeadline_id(content['bulkdeadline_id'])[0],
                          new_deadline)
        self.assertEquals(len(content['groups']), 3)
        self.assertEquals(content['text'], 'Hello')
        self.assertEquals(content['deadline'], format_datetime(new_deadline))
        for groupnum in xrange(3):
            deadline_id = getattr(self.testhelper, 'sub_p1_a1_g{0}_d1'.format(groupnum)).id
            deadline = Deadline.objects.get(id=deadline_id)
            self.assertEquals(deadline.deadline, new_deadline)
            self.assertEquals(deadline.text, 'Hello')

    def test_put_nonetext(self):
        self.assertEquals(self.testhelper.sub_p1_a1.publishing_time, datetime(2000, 1, 1, 22, 30, 51))
        self.assertEquals(self.testhelper.sub_p1_a1_g1_d1.deadline,
                          datetime(2000, 1, 1, 22, 30) + timedelta(days=5))

        new_deadline = datetime(2004, 12, 24, 20, 30)
        content, response = self._putas('adm', {'deadline': format_datetime(new_deadline),
                                                'text': None})
        self.assertEquals(response.status_code, 200)
        for groupnum in xrange(3):
            deadline_id = getattr(self.testhelper, 'sub_p1_a1_g{0}_d1'.format(groupnum)).id
            deadline = Deadline.objects.get(id=deadline_id)
            self.assertEquals(deadline.deadline, new_deadline)
            self.assertEquals(deadline.text, '')

    def test_put_before_publishingtime(self):
        new_deadline = datetime(1990, 1, 1, 20, 30, 40)
        content, response = self._putas('adm', {'deadline': format_datetime(new_deadline),
                                                'text': None})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(content['errors'], ['Deadline cannot be before publishing time.'])

    def test_put_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._putas('nobody', {})
        self.assertEquals(response.status_code, 403)

    def test_put_with_bulkdeadline_id(self):
        new_deadline = datetime(2004, 12, 24, 20, 30)
        content, response = self._putas('adm', {'deadline': format_datetime(new_deadline),
                                                'bulkdeadline_id': 'ignored'})
        self.assertEquals(response.status_code, 200)

    def test_put_group_ids(self):
        new_deadline = datetime(2004, 12, 24, 20, 30)
        g1 = self.testhelper.sub_p1_a1_g1
        g2 = self.testhelper.sub_p1_a1_g2
        self.assertEquals(g1.deadlines.count(), 1)

        content, response = self._putas('adm', {'deadline': format_datetime(new_deadline),
                                                'text': 'Updated',
                                                'group_ids': [g1.id, g2.id]})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content['groups']), 2)
        group_ids = set([g['id'] for g in content['groups']])
        self.assertEquals(group_ids, set([g1.id, g2.id]))

        for group in g1, g2:
            group = self.testhelper.reload_from_db(group)
            self.assertEquals(group.deadlines.count(), 1)
            deadline = group.deadlines.all()[0]
            self.assertEquals(deadline.deadline, new_deadline)
            self.assertEquals(deadline.text, 'Updated')



    def _getas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self._geturl(), **data)

    def test_get(self):
        content, response = self._getas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(decode_bulkdeadline_id(content['bulkdeadline_id'])[0],
                          self.testhelper.sub_p1_a1_g1_d1.deadline)
        self.assertEquals(content['deadline'],
                          format_datetime(self.testhelper.sub_p1_a1_g1_d1.deadline))
        self.assertEquals(content['text'], None)
        self.assertEquals(len(content['groups']), 3)

    def test_get_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._getas('nobody')
        self.assertEquals(response.status_code, 403)

    def _deleteas(self, username, deadline=None):
        self.client.login(username=username, password='test')
        return self.client.rest_delete(self._geturl(deadline))

    def test_delete_sanity(self):
        # Test that the deadline method actually does what it is supposed to do (only deletes what it should delete)
        new_deadline = datetime(2004, 12, 24, 20, 30)
        created_deadline = None
        for groupnum in xrange(2):
            group = getattr(self.testhelper, 'sub_p1_a1_g{0}'.format(groupnum))
            self.assertEquals(1, group.deadlines.count())
            created_deadline = group.deadlines.create(deadline=new_deadline) # NOTE: Does not matter which deadline object we user, since we only need the datetime and text to generate bulkdeadline_id
            self.assertEquals(2, group.deadlines.count())
        self.testhelper.sub_p1_a1_g2.deadlines.create(deadline=datetime(2006, 12, 24, 20, 30))

        self.testhelper.create_superuser('superuser')
        content, response = self._deleteas('superuser', deadline=created_deadline)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content['deleted_deadline_ids']), 2)
        self.assertEquals(1, self.testhelper.sub_p1_a1_g0.deadlines.count())
        self.assertEquals(1, self.testhelper.sub_p1_a1_g1.deadlines.count())
        self.assertEquals(2, self.testhelper.sub_p1_a1_g2.deadlines.count())

    def test_delete_with_content_as_superuser(self):
        self.testhelper.create_superuser('superuser')
        self.testhelper.add_delivery('sub.p1.a1.g1', {'bad.py': ['print ', 'bah']})
        self.testhelper.add_feedback('sub.p1.a1.g1', verdict={'grade': 'F', 'points': 30, 'is_passing_grade': False})
        content, response = self._deleteas('superuser')
        self.assertEquals(response.status_code, 200)

    def test_delete_with_content_as_assignmentadm(self):
        self.testhelper.add_delivery('sub.p1.a1.g1', {'bad.py': ['print ', 'bah']})
        self.testhelper.add_feedback('sub.p1.a1.g1', verdict={'grade': 'F', 'points': 30, 'is_passing_grade': False})
        content, response = self._deleteas('adm')
        self.assertEquals(response.status_code, 403)

    def test_delete_without_content_as_assignmentadm(self):
        content, response = self._deleteas('adm')
        self.assertEquals(response.status_code, 200)

    def test_delete_as_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._deleteas('nobody')
        self.assertEquals(response.status_code, 403)
