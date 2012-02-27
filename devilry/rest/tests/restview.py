from django.test import TestCase

from devilry.rest.testutils import RestClient


class TestRestView(TestCase):
    urls = 'devilry.rest.testurls'

    def test_create(self):
        client = RestClient()
        content, response = client.rest_create('/polls/',
                                               pollname='mypoll',
                                               choices=['a', 'b', 'c'])
        self.assertEquals(response.status_code, 201)
        self.assertEquals(content['created'], 'mypoll')
        self.assertEquals(content['createdchoices'], ['a', 'b', 'c'])

    def test_read(self):
        client = RestClient()
        content, response = client.rest_read('/polls/', 1)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], '1')
        self.assertEquals(content['something'], 'Hello world')

        content, response = client.rest_read('/polls/', 1, something='Changed')
        self.assertEquals(content['something'], 'Changed')

    def test_update(self):
        client = RestClient()
        content, response = client.rest_update('/polls/', 1,
                                               pollname='mypollUp',
                                               choices=['c', 'd', 'e'])
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], '1')
        self.assertEquals(content['updated'], 'mypollUp')
        self.assertEquals(content['updatedchoices'], ['c', 'd', 'e'])

    def test_delete(self):
        client = RestClient()
        content, response = client.rest_delete('/polls/', 1)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['id'], '1')
