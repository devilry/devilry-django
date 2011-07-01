from django.test import TestCase
from django.db import models

from ...simplified import simplified_modelapi, PermissionDenied, FieldSpec
from ...restful import restful_modelapi, ModelRestView
from modelintegration import restfulmodelcls_to_extjsmodel
from storeintegration import restfulmodelcls_to_extjsstore

class User(models.Model):
    first = models.CharField(max_length=20, db_index=True)
    last = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(db_index=True)
    score = models.IntegerField()


@simplified_modelapi
class SimplifiedUser(object):
    #@classmethod
    #def read_authorize(cls, user, obj):
        #return True

    class Meta:
        model = User
        resultfields = FieldSpec('id', 'first', 'last', 'email', 'score')
        searchfields = FieldSpec('short_name', 'long_name')
        methods = []


@restful_modelapi
class RestUser(ModelRestView):
    class Meta:
        simplified = SimplifiedUser

    # Override to avoid having to add the rest as an url
    @classmethod
    def get_rest_url(cls, *args, **kwargs):
        return '/restuser'


class TestModelIntegration(TestCase):
    def test_to_extjsmodel(self):
        js = restfulmodelcls_to_extjsmodel(RestUser)
        expected = """Ext.define('devilry.apps.extjshelpers.tests.SimplifiedUser', {
            extend: 'Ext.data.Model',
            fields: [{"type": "int", "name": "id"}, {"type": "string", "name": "first"}, {"type": "string", "name": "last"}, {"type": "string", "name": "email"}, {"type": "int", "name": "score"}],
            idProperty: 'id',
            proxy: {
                type: 'rest',
                url: '/restuser',
                extraParams: {getdata_in_qrystring: true},
                reader: {
                    type: 'json',
                    root: 'items'
                },
                writer: {
                    type: 'json'
                }
            }
        });"""
        self.assertEquals(js, expected)


class TestStoreIntegration(TestCase):
    def test_to_extjsstore(self):
        js = restfulmodelcls_to_extjsstore(RestUser)
        expected = """Ext.create('Ext.data.Store', {
            model: 'devilry.apps.extjshelpers.tests.SimplifiedUser',
            remoteFilter: true,
            remoteSort: true,
            autoLoad: true,
            autoSync: true
        });"""
        self.assertEquals(js, expected)



"""
successfmt = {
    successful: True,
    items: [
            {name: "Espen", score: 10},
            {name: "Tor", score: 10}
           ]
}

errormft = {
    successful: False,
    errors: {
             name: "To many chars.",
             score: "Not an integer."
            }
}
"""
