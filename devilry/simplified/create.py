"""
Functions used to add CRUD+S methods to simplified classes at module load time.
"""
from types import MethodType

from qryresultwrapper import QryResultWrapper
from utils import modelinstance_to_dict
from exceptions import PermissionDenied


def _parse_fieldgroups(fieldlst, fieldgroups):
    if isinstance(fieldlst, dict):
        base = fieldlst.get('__BASE__', [])
        fields = list(base)
        for group in fieldgroups:
            fields.extend(fieldlst.get(group, []))
        return fields
    else:
        return fieldlst

def _getwrapper(cls, **kw):
    try:
        return cls._meta.model.objects.get(**kw)
    except cls._meta.model.DoesNotExist, e:
        raise PermissionDenied() # Raise permission denied instead of "does not exist" to make it impossible to "brute force" query for existing items

def _writeauth_get(cls, user, idorkw):
    if isinstance(idorkw, dict):
        kw = idorkw
    else:
        kw = dict(pk=idorkw)
    obj = _getwrapper(cls, **kw)
    cls.write_authorize(user, obj)
    return obj

def _readauth_get(cls, user, idorkw):
    if isinstance(idorkw, dict):
        kw = idorkw
    else:
        kw = dict(pk=idorkw)
    obj = _getwrapper(cls, **kw)
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
        """ Read the requested item and return a django model object.

        :param user: Django user object.
        :param idorkw: Id of object or kwargs to the get method of the configured model.

        :throws PermissionDenied:
            If the given user does not have permission to
            view this object, or if the object does not exist.
        """
        return _writeauth_get(cls, user, idorkw)
    setattr(cls, insecure_read_model.__name__, MethodType(insecure_read_model, cls))
    #cls.get.__func__.__doc__

def create_read_method(cls):
    def read(cls, user, idorkw, result_fieldgroups=[]):
        """ Read the requested item and return a dict with the fields specified
        in ``Meta.resultfields`` and additional fields specified in
        ``result_fieldgroups``.

        :param user: Django user object.
        :param idorkw: Id of object or kwargs to the get method of the configured model.
        :param result_fieldgroups:
            Fieldgroups from the additional_fieldgroups specified in
            ``result_fieldgroups``.

        :throws PermissionDenied:
            If the given user does not have permission to view this object, or
            if the object does not exist.
        """
        obj = _readauth_get(cls, user, idorkw) # authorization in _writeauth_get
        resultfields = cls._meta.resultfields.aslist(result_fieldgroups)
        #if hasattr(cls, 'filter_read_resultfields'):
            #resultfields = cls.filter_read_resultfields(user, obj, resultfields)
        return modelinstance_to_dict(obj, fields=resultfields)
    setattr(cls, read.__name__, MethodType(read, cls))

def create_delete_method(cls):
    def delete(cls, user, idorkw):
        """ Delete the given object.

        :param user: Django user object.
        :param idorkw: Id of object or kwargs to the get method of the configured model.
        :throws PermissionDenied:
            If the given user does not have permission to view this object, or
            if the object does not exist.
        """
        obj = _writeauth_get(cls, user, idorkw) # authorization in _writeauth_get
        pk = obj.pk
        obj.delete()
        return pk
    setattr(cls, delete.__name__, MethodType(delete, cls))

def create_update_method(cls):
    def update(cls, user, idorkw, **field_values):
        """ Update the given object.

        :param user: Django user object.
        :param idorkw: Id of object or kwargs to the get method of the configured model.
        :field_values: The values to set on the given object.
        :throws PermissionDenied:
            If the given user does not have permission to view this object, or
            if the object does not exist.
        """
        obj = _writeauth_get(cls, user, idorkw) # authorization in _writeauth_get
        for fieldname, value in field_values.iteritems():
            setattr(obj, fieldname, value)
        obj.full_clean()
        obj.save()
        return obj
    setattr(cls, update.__name__, MethodType(update, cls))

def create_search_method(cls):
    def search(cls, user, **kwargs):
        """ Search for objects.

        :param start:
            Return results from this index in the results from the given
            ``query``. Defaults to ``0``.
        :param limit:
            Limit results to this number of items. Defaults to ``50``.
        :param orderby:
            Order the result by these fields. For example, if
            ``Meta.resultfields`` contains the short_name and long_name fields,
            we can order our results by ascending short_name and descending
            long_name as this: ``orderby=('short_name', '-long_name')``.
        :type orderby:
            List of fieldnames. Fieldnames can be prefixed by ``'-'`` for
            descending ordering.
        :param query:
            A string to search for within the model specified in
            ``Meta.model``. The fields to search for is specified in
            ``Meta.search_fieldgroups``.
        :param result_fieldgroups:
            Adds additional fields to the result. Available values are the
            fieldgroups in ``Meta.resultfields.additional_fieldgroups``.
        :param search_fieldgroups:
            Adds additional fields which are searched for the ``query`` string.
            Available values are the fieldgroups in
            ``Meta.searchfields.additional_fieldgroups``.

        :return: The result of the search.
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
