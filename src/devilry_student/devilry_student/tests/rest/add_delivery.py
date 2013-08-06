import json
from django.test import TestCase
from StringIO import StringIO
from datetime import datetime, timedelta
from devilry.apps.core.models import Assignment
from devilry.apps.core.testhelper import TestHelper
#from devilry.utils.rest_testclient import RestClient
from django.test.client import Client


class FakeFile(StringIO):
    def __init__(self, name, content):
        self.name = name
        StringIO.__init__(self, content)


class TestRestAddDeliveryView(TestCase):
    def setUp(self):
        self.client = Client()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-1)'],
                            assignments=['a1'])
        #self.testhelper.create_user('testuser')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        self.group = self.testhelper.sub_p1_a1_g1
        self.url = '/devilry_student/rest/add-delivery/{0}'.format(self.group.id)

    def _postas(self, username, data):
        self.client.login(username=username, password='test')
        response = self.client.post(self.url, data)
        return response, json.loads(response.content)

    def test_add_delivery(self):
        # Create the delivery and upload a file
        fp = FakeFile('hello.txt', 'Hello world')
        response, content = self._postas('student1', {'file_to_add': fp})
        self.assertEquals(response.status_code, 200)
        deadline = self.group.get_active_deadline()
        self.assertEquals(deadline.deliveries.count(), 1)
        delivery = deadline.deliveries.all()[0]
        self.assertEquals(content, {'group_id': self.group.id,
                                    'deadline_id': deadline.id,
                                    'delivery_id': delivery.id,
                                    'added_filename': 'hello.txt',
                                    'finished': False,
                                    'success': True,
                                    'created_delivery': True})
        self.assertEquals(delivery.successful, False)
        self.assertEquals(delivery.filemetas.count(), 1)
        self.assertEquals(delivery.filemetas.all()[0].filename, 'hello.txt')

        # Upload another file
        fp2 = FakeFile('test.txt', 'test')
        response, content = self._postas('student1', {'delivery_id': delivery.id,
                                                      'file_to_add': fp2})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content, {'group_id': self.group.id,
                                    'deadline_id': deadline.id,
                                    'delivery_id': delivery.id,
                                    'added_filename': 'test.txt',
                                    'finished': False,
                                    'success': True,
                                    'created_delivery': False})
        delivery = deadline.deliveries.all()[0]
        self.assertEquals(delivery.filemetas.count(), 2)
        self.assertEquals(deadline.deliveries.count(), 1)
        self.assertEquals(delivery.successful, False)

        # Set the delivery to successful
        response, content = self._postas('student1', {'delivery_id': delivery.id,
                                                      'finish': True})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content, {'group_id': self.group.id,
                                    'deadline_id': deadline.id,
                                    'delivery_id': delivery.id,
                                    'added_filename': None,
                                    'finished': True,
                                    'success': True,
                                    'created_delivery': False})
        delivery = deadline.deliveries.all()[0]
        self.assertEquals(delivery.filemetas.count(), 2)
        self.assertEquals(deadline.deliveries.count(), 1)
        self.assertEquals(delivery.successful, True)
        self.assertEquals(delivery.delivered_by.student.username, 'student1')

    def test_add_delivery_nobody(self):
        self.testhelper.create_user('nobody')
        response, content = self._postas('nobody', {})
        self.assertEquals(response.status_code, 403)
        self.assertEquals(content['detail'],
                         'Only candidates on group with ID={0} can make this request.'.format(self.group.id))

    def test_add_delivery_duplicated_filename(self):
        fp = FakeFile('hello.txt', 'Hello world')
        response, content = self._postas('student1', {'file_to_add': fp})
        self.assertEquals(response.status_code, 200)
        deadline = self.group.get_active_deadline()
        delivery = deadline.deliveries.all()[0]

        response, content = self._postas('student1', {'delivery_id': delivery.id,
                                                      'file_to_add': fp})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(content['detail'], 'Filename must be unique')

    def test_change_after_successful(self):
        deadline = self.testhelper.sub_p1_a1_g1_d1
        delivery = deadline.deliveries.create(successful=True)

        fp = FakeFile('hello.txt', 'Hello world')
        response, content = self._postas('student1', {'delivery_id': delivery.id,
                                                      'file_to_add': fp})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(content['detail'], 'Can not change finished deliveries.')

    def test_add_delivery_to_closed_group(self):
        self.group.is_open = False
        self.group.save()
        fp = FakeFile('hello.txt', 'Hello world')
        response, content = self._postas('student1', {'file_to_add': fp})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(content['detail'], 'Can not add deliveries on closed groups.')

    def test_response_html_content_type(self):
        fp = FakeFile('hello.txt', 'Hello world')

        # Sanity check without respond_with_html_contenttype
        response, content = self._postas('student1', {'file_to_add': fp})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['content-type'], 'application/json')

        # With respond_with_html_contenttype
        response, content = self._postas('student1', {'file_to_add': fp,
                                                      'respond_with_html_contenttype': True})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['content-type'], 'text/html')
        self.assertEquals(content['success'], True)
        self.assertEquals(content['added_filename'], 'hello.txt')

    def test_error_response_html_content_type(self):
        fp = FakeFile('hello.txt', 'Hello world')
        response, content = self._postas('student1', {'file_to_add': fp})
        self.assertEquals(response.status_code, 200)
        deadline = self.group.get_active_deadline()
        delivery = deadline.deliveries.all()[0]

        response, content = self._postas('student1', {'delivery_id': delivery.id,
                                                      'file_to_add': fp,
                                                      'respond_with_html_contenttype': True})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response['content-type'], 'text/html')
        self.assertEquals(content['detail'], 'Filename must be unique')

    def test_hard_deadline(self):
        
        # Soft deadlines
        fp = FakeFile('hello.txt', 'Hello world')

        deadline = self.group.get_active_deadline()
        deadline.deadline = datetime.now() - timedelta(days=1)
        deadline.save()

        response, content = self._postas('student1', {'file_to_add': fp})
        self.assertEquals(response.status_code, 200)

        # Hard deadlines
        assignment = self.group.parentnode
        assignment.deadline_handling = Assignment.DEADLINEHANDLING_HARD
        assignment.save()

        response, content = self._postas('student1', {'file_to_add': fp})
        self.assertEquals(response.status_code, 400)

