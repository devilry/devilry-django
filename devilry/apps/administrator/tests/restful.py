from datetime import datetime
from django.test import TestCase
from django.test.client import Client
import json

from ..restful import (RestfulSimplifiedNode, RestfulSimplifiedAssignment, RestfulSimplifiedSubject,
                       RestfulSimplifiedPeriod, RestfulSimplifiedAssignmentGroup)
from ..simplified import (SimplifiedAssignment, SimplifiedSubject, SimplifiedPeriod,
                          SimplifiedAssignmentGroup)
from ...core import models, testhelper

class TestAdministratorRestfulSimplifiedNode(TestCase, testhelper.TestHelper):
    def setUp(self):
        self.add(nodes='uni:admin(admin1)')
        self.client = Client()
        self.client.login(username="admin1", password="test")

    def test_search(self):
        url = RestfulSimplifiedNode.get_rest_url()
        r = self.client.get(url, data={'getdata_in_qrystring': True})
        self.assertEquals(r.status_code, 200)
        data = json.loads(r.content)
        first = data['items'][0]
        self.assertEquals(first, {'id': self.uni.id,
                                  'short_name': self.uni.short_name,
                                  'long_name': self.uni.long_name,
                                  'parentnode': None
                                 })

    def test_create(self):
        self.assertEquals(models.Node.objects.filter(short_name='testnode').count(), 0)
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(short_name='testnode', long_name='Test SimplifiedNode', parentnode=None)
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 201)
        response = json.loads(r.content)
        self.assertEquals(models.Node.objects.filter(short_name='testnode').count(), 1)
        fromdb = models.Node.objects.get(id=response['id'])
        self.assertEquals(fromdb.short_name, 'testnode')
        self.assertEquals(fromdb.long_name, 'Test SimplifiedNode')
        self.assertEquals(fromdb.parentnode, None)

    def test_create_errors(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(short_name='uniV', long_name='Univ', parentnode=None)
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 400)
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            fielderrors = {u'short_name': [u"Can only contain numbers, lowercase letters, '_' and '-'. "]},
            errormessages = []))

    def test_update(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(id=2, short_name='univ', long_name='Univ', parentnode=None)
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, {'id': self.uni.id,
                                     'short_name': 'univ',
                                     'long_name': 'Univ',
                                     'parentnode': None})

    def test_update_errors(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(id=2, short_name='uniV', long_name='Univ', parentnode=None)
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            fielderrors = {u'short_name': [u"Can only contain numbers, lowercase letters, '_' and '-'. "]},
            errormessages = []))

    def test_delete(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        self.assertEquals(models.Node.objects.filter(id=self.uni.id).count(), 1)
        r = self.client.delete(url, content_type='application/json')
        self.assertEquals(models.Node.objects.filter(id=self.uni.id).count(), 0)


class TestAdministratorRestfulSimplifiedAssignment(TestCase, testhelper.TestHelper):
    def setUp(self):
        self.add(nodes='uni:admin(admin1)',
                 subjects=['inf101', 'inf110'],
                 periods=['firstsem', 'secondsem:admin(admin2)'],
                 assignments=['a1', 'a2'])
        self.client = Client()
        self.client.login(username="admin1", password="test")

    def test_search_fieldgroups(self):
        resultfields = SimplifiedAssignment._meta.resultfields
        url = RestfulSimplifiedAssignment.get_rest_url()

        r = self.client.get(url, data={'getdata_in_qrystring': True})
        self.assertEquals(r.status_code, 200)
        data = json.loads(r.content)
        first = data['items'][0]
        self.assertEquals(set(first.keys()), set(resultfields.aslist()))

        r = self.client.get(url, data={'getdata_in_qrystring': True,
                                       'result_fieldgroups': json.dumps(['subject', 'period', 'pointfields'])})
        self.assertEquals(r.status_code, 200)
        data = json.loads(r.content)
        first = data['items'][0]
        all_resultfields = resultfields.aslist(resultfields.additional_aslist())
        self.assertEquals(set(first.keys()), set(all_resultfields))


class TestAdministratorRestfulSimplifiedSubject(TestCase, testhelper.TestHelper):
    pekerkjede = RestfulSimplifiedSubject
    resultfields = SimplifiedSubject._meta.resultfields

    def setUp(self):
        self.add(nodes='uni:admin(admin1)',
                 subjects=['inf101','inf110'])
        self.client = Client()
        self.client.login(username="admin1", password="test")
    
    def test_search(self):
        url = self.pekerkjede.get_rest_url()
        r = self.client.get(url, data={'getdata_in_qrystring': True})
        self.assertEquals(r.status_code, 200)
        data = json.loads(r.content)
        first = data['items'][0]
        self.assertEquals(set(first.keys()), set(self.resultfields.aslist()))

    def test_create(self):
        self.assertEquals(models.Subject.objects.filter(short_name='inf011').count(), 0)
        url = self.pekerkjede.get_rest_url()
        data = dict(short_name='inf011', long_name='inf011 - Moro med Programmering',
                    parentnode=self.uni.id)
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 201)
        response = json.loads(r.content)
        self.assertEquals(models.Subject.objects.filter(short_name='inf011').count(), 1)
        fromdb = models.Subject.objects.get(id=response['id'])
        self.assertEquals(fromdb.short_name, 'inf011')
        self.assertEquals(fromdb.long_name, 'inf011 - Moro med Programmering')
        self.assertEquals(fromdb.parentnode.id, self.uni.id)
        # print "\n\n", fromdb.parentnode, "\n\n"

    def test_create_errors(self):
        self.assertEquals(models.Subject.objects.filter(short_name='inf011').count(), 0)
        url = self.pekerkjede.get_rest_url()
        data = dict(short_name='inf011', long_name='inf011 - Moro med Programmering')
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 400)

    def test_update(self):
        url = self.pekerkjede.get_rest_url(self.uni.id)
        data = dict(short_name='inf101', long_name='inf101 - Ikke Moro med Programmering',
                    parentnode=self.uni.id)
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 200)
        response = json.loads(r.content)

        fromdb = models.Subject.objects.get(id=response['id'])
        self.assertEquals(fromdb.short_name, 'inf101')
        self.assertEquals(fromdb.long_name, 'inf101 - Ikke Moro med Programmering')
        self.assertEquals(fromdb.parentnode.id, self.uni.id)

    def test_update_errors(self):
        url = self.pekerkjede.get_rest_url(self.uni.id)
        data = dict(short_name='InF001', long_name='inf101 - Ikke Moro med Programmering',
                    parentnode=self.uni.id)
        r = self.client.put(url, data=json.dumps(data),
                            content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            fielderrors = {u'short_name': [u"Can only contain numbers, lowercase letters, '_' and '-'. "]},
            errormessages = []))
    
    def test_delete(self):
        url = self.pekerkjede.get_rest_url(self.uni.id)
        self.assertEquals(models.Subject.objects.filter(short_name='inf101').count(), 1)
        r = self.client.delete(url, content_type='application/json')
        self.assertEquals(r.status_code, 200)
        self.assertEquals(models.Subject.objects.filter(short_name='inf101').count(), 0)


class TestAdministratorRestfulSimplifiedPeriod(TestCase, testhelper.TestHelper):
    pekerkjede = RestfulSimplifiedPeriod
    resultfields = SimplifiedPeriod._meta.resultfields

    def setUp(self):
        self.add(nodes='uni:admin(admin1)',
                 subjects=['inf101','inf110'],
                 periods=['v2011', 'h2006'])
        self.client = Client()
        self.client.login(username="admin1", password="test")
    
    def test_search(self):
        url = self.pekerkjede.get_rest_url()
        r = self.client.get(url, data={'getdata_in_qrystring': True})
        self.assertEquals(r.status_code, 200)
        data = json.loads(r.content)
        first = data['items'][0]
        self.assertEquals(set(first.keys()), set(self.resultfields.aslist()))

    def test_create(self):
        self.assertEquals(models.Period.objects.filter(short_name='h2010').count(), 0)
        url = self.pekerkjede.get_rest_url(self.uni.id)
        data = dict(short_name='h2010', long_name='H2010',
                    parentnode=self.uni.id, start_time='2011-07-12 04:22:48',
                    end_time='2011-07-12 04:22:48')
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 201)
        response = json.loads(r.content)
        self.assertEquals(models.Period.objects.filter(short_name='h2010').count(), 1)
        fromdb = models.Period.objects.get(id=response['id'])
        self.assertEquals(fromdb.short_name, 'h2010')
        self.assertEquals(fromdb.long_name, 'H2010')
        self.assertEquals(fromdb.parentnode.id, self.uni.id)
        # print "\n\n", fromdb.parentnode, "\n\n"

    def test_create_errors(self):
        self.assertEquals(models.Period.objects.filter(short_name='h2010').count(), 0)
        url = self.pekerkjede.get_rest_url(self.uni.id)
        data = dict(short_name='h2010', long_name='H2010',
                    parentnode=self.uni.id, start_time='2011-07-12 04:22:48')
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 400)

    def test_update(self):
        url = self.pekerkjede.get_rest_url(self.uni.id)

        data = dict(short_name='v2011', long_name='V2011',
                    parentnode=self.uni.id, start_time='2011-07-12 04:22:48',
                    end_time='2011-07-12 04:22:48')
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 200)
        response = json.loads(r.content)

        fromdb = models.Period.objects.get(id=response['id'])
        self.assertEquals(fromdb.short_name, 'v2011')
        self.assertEquals(fromdb.long_name, 'V2011')
        self.assertEquals(fromdb.parentnode.id, self.uni.id)

    def test_update_errors(self):
        url = self.pekerkjede.get_rest_url(self.uni.id)
        data = dict(short_name='v2011', long_name='V2011',
                    parentnode=self.uni.id)
        r = self.client.put(url, data=json.dumps(data),
                            content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            fielderrors = {u'start_time': [u'This field is required.'],
                           u'end_time': [u'This field is required.']},
            errormessages = []))
    
    def test_delete(self):
        url = self.pekerkjede.get_rest_url(self.uni.id)
        self.assertEquals(models.Period.objects.filter(short_name='v2011').count(), 2)
        r = self.client.delete(url, content_type='application/json')
        self.assertEquals(r.status_code, 200)
        self.assertEquals(models.Period.objects.filter(short_name='v2011').count(), 1)



class TestAdministratorRestfulSimplifiedAssignmentGroup(TestCase, testhelper.TestHelper):
    pekerkjede = RestfulSimplifiedAssignmentGroup
    resultfields = SimplifiedAssignmentGroup._meta.resultfields

    def setUp(self):
        # create a base structure
        self.add(nodes='uni:admin(admin1)',
                 subjects=['inf101', 'inf110'],
                 periods=['firstsem', 'secondsem'],
                 assignments=['a1', 'a2'])

        # add firstStud to the first and secondsem assignments
        self.add_to_path('uni;inf101.firstsem.a1.g1:candidate(firstStud)')
        self.add_to_path('uni;inf101.firstsem.a2.g1:candidate(firstStud)')
        self.add_to_path('uni;inf110.secondsem.a1.g1:candidate(firstStud)')
        self.add_to_path('uni;inf110.secondsem.a2.g1:candidate(firstStud)')

        # secondStud began secondsem
        self.add_to_path('uni;inf101.secondsem.a1.g2:candidate(secondStud)')
        self.add_to_path('uni;inf101.secondsem.a2.g2:candidate(secondStud)')

        self.client.login(username="admin1", password="test")

    def test_search(self):
        url = self.pekerkjede.get_rest_url()
        r = self.client.get(url, data={'getdata_in_qrystring': True})
        self.assertEquals(r.status_code, 200)
        data = json.loads(r.content)
        first = data['items'][0]
        self.assertEquals(set(first.keys()), set(self.resultfields.aslist()))

    def test_create(self):
        #TODO test_create
        pass

    def test_create_errors(self):
        #TODO test_create_errors
        pass

    def test_update(self):
        #TODO test_update
        pass

    def test_update_errors(self):
        #TODO test_update_errors
        pass
    
    def test_delete(self):
        #TODO test_delete
        pass
