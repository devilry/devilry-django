from django.test import TestCase
from django.db import models

from ...simplified import simplified_modelapi, FieldSpec
from ...restful import restful_modelapi, ModelRestfulView
from ..core.models import Period
from ..administrator.restful import RestfulSimplifiedPeriod
from modelintegration import restfulcls_to_extjsmodel
from storeintegration import restfulcls_to_extjsstore
from fieldintegration import djangofield_to_extjsformfield



class User(models.Model):
    first = models.CharField(max_length=20, db_index=True)
    last = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(db_index=True)
    score = models.IntegerField()
    introtext = models.TextField()
    text = models.TextField()


@simplified_modelapi
class SimplifiedUser(object):
    #@classmethod
    #def read_authorize(cls, user, obj):
        #return True

    class Meta:
        model = User
        resultfields = FieldSpec('id', 'first', 'last', 'email', 'score',
                                 textfields=['introtext', 'text'])
        searchfields = FieldSpec('first', 'last')
        methods = []


@restful_modelapi
class RestUser(ModelRestfulView):
    class Meta:
        simplified = SimplifiedUser

    # Override to avoid having to add the rest as an url
    @classmethod
    def get_rest_url(cls, *args, **kwargs):
        return '/restuser'


class TestModelIntegration(TestCase):
    def test_to_extjsmodel(self):
        actual = restfulcls_to_extjsmodel(RestUser)
        expected = """Ext.define('devilry.apps.extjshelpers.tests.SimplifiedUser', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int",
            "name": "id"
        },
        {
            "type": "auto",
            "name": "first"
        },
        {
            "type": "auto",
            "name": "last"
        },
        {
            "type": "auto",
            "name": "email"
        },
        {
            "type": "int", 
            "name": "score"
        }
    ],
    idProperty: 'id',
    
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/restuser',
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    })
})"""
        actual = actual.split('\n')
        expected = expected.split('\n')
        for index, actualline in enumerate(actual):
            expectedline = expected[index]
            #print "#{0}#".format(actualline)
            #print "#{0}#".format(expectedline)
            self.assertEqual(actualline.strip(), expectedline.strip())

    def test_to_extjsmodel_fieldgroups(self):
        js = restfulcls_to_extjsmodel(RestUser)
        self.assertFalse('textfields' in js)
        js = restfulcls_to_extjsmodel(RestUser, ['textfields'])
        self.assertTrue('textfields' in js)


class TestStoreIntegration(TestCase):
    def test_to_extjsstore(self):
        js = restfulcls_to_extjsstore(RestUser)
        expected = """Ext.create('Ext.data.Store', {
            model: 'devilry.apps.extjshelpers.tests.SimplifiedUser',
            id: 'devilry.apps.extjshelpers.tests.SimplifiedUserStore',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        })"""
        self.assertEquals(js, expected)




class TestFieldIntegration(TestCase):
    #def test_djangofield_to_extjsformfield(self):
        #field = find_foreign_field(Period, ["parentnode", "id"])
        ##print dir(field.model)
        ##print dir(field.model._meta)
        #self.assertEquals(field.name, 'id')

    def test_djangofield_to_extjs_xtype(self):
        extfield = djangofield_to_extjsformfield(Period, 'parentnode', RestfulSimplifiedPeriod)
