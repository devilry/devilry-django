"""
Functions used to add CRUD+S methods to simplified classes at module load time.
"""
from types import MethodType

from qryresultwrapper import QryResultWrapper
from utils import modelinstance_to_dict


def _parse_fieldgroups(fieldlst, fieldgroups):
    if isinstance(fieldlst, dict):
        base = fieldlst.get('__BASE__', [])
        fields = list(base)
        for group in fieldgroups:
            fields.extend(fieldlst.get(group, []))
        return fields
    else:
        return fieldlst



def _writeauth_get(cls, user, idorkw):
    if isinstance(idorkw, dict):
        kw = idorkw
    else:
        kw = dict(pk=idorkw)
    obj = cls._meta.model.objects.get(**kw)
    cls.write_authorize(user, obj)
    return obj

def _readauth_get(cls, user, idorkw):
    if isinstance(idorkw, dict):
        kw = idorkw
    else:
        kw = dict(pk=idorkw)
    obj = cls._meta.model.objects.get(**kw)
    cls.read_authorize(user, obj)
    return obj



def create_create_method(cls):
    """ Adds the ``create()`` method as a classmethod on the given class. """
    def create(cls, user, **field_values):
        obj =  cls._meta.model(**field_values)
        cls.write_authorize(user, obj) # Important that this is after parentnode is set on Nodes, or admins on parentnode will not be permitted!
        obj.full_clean()
        obj.save()
        return obj
    setattr(cls, create.__name__, MethodType(create, cls))

def create_insecure_read_model_method(cls):
    """ Adds the ``insecure_read_model()`` method as a classmethod on the given class. """
    def insecure_read_model(cls, user, idorkw):
        return _writeauth_get(cls, user, idorkw)
    setattr(cls, insecure_read_model.__name__, MethodType(insecure_read_model, cls))
    #cls.get.__func__.__doc__

def create_read_method(cls):
    def read(cls, user, idorkw, result_fieldgroups=[]):
        """
        :param user: Django user object.
        :param idorkw: Id of object or kwargs to the get method of the configured model.
        :result_fieldgroups: List of additions to the __BASE__ list if resultfields is a dict.
        """
        obj = _readauth_get(cls, user, idorkw) # authorization in _writeauth_get
        resultfields = cls._meta.resultfields.aslist(result_fieldgroups)
        #if hasattr(cls, 'filter_read_resultfields'):
            #resultfields = cls.filter_read_resultfields(user, obj, resultfields)
        return modelinstance_to_dict(obj, fields=resultfields)
    setattr(cls, read.__name__, MethodType(read, cls))

def create_delete_method(cls):
    def delete(cls, user, idorkw):
        obj = _writeauth_get(cls, user, idorkw) # authorization in _writeauth_get
        pk = obj.pk
        obj.delete()
        return pk
    setattr(cls, delete.__name__, MethodType(delete, cls))

def create_update_method(cls):
    def update(cls, user, idorkw, **field_values):
        obj = _writeauth_get(cls, user, idorkw) # authorization in _writeauth_get
        for fieldname, value in field_values.iteritems():
            setattr(obj, fieldname, value)
        obj.full_clean()
        obj.save()
        return obj
    setattr(cls, update.__name__, MethodType(update, cls))

def create_search_method(cls):
    def search(cls, user, **kwargs):
        """
        :param start:
        :param limit:
        :param orderby:
        :return: The result of fiter() on cls.meta.model.
        :rtype: QryResultWrapper
        """
        resultfields = cls._meta.resultfields.aslist(kwargs.pop('result_fieldgroups', None))
        searchfields = cls._meta.searchfields.aslist(kwargs.pop('search_fieldgroups', None))
        qryset = cls.create_searchqryset(user, **kwargs)
        if isinstance(qryset, QryResultWrapper):
            result = qryset
        else:
            result = QryResultWrapper(resultfields, searchfields, qryset)
        standard_opts = dict(
            query = kwargs.pop('query', None),
            start = kwargs.pop('start', 0),
            limit = kwargs.pop('limit', 50),
            orderby = kwargs.pop('orderby', cls._meta.ordering)
        )
        result._standard_operations(**standard_opts)
        return result
    setattr(cls, search.__name__, MethodType(search, cls))
