"""
Functions used to add CRUD+S methods to simplified classes at module load time.
"""
from types import MethodType

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

def _getwrapper(cls, idorkw):
    if isinstance(idorkw, dict):
        kw = idorkw
    else:
        kw = dict(pk=idorkw)
    try:
        return cls._meta.model.objects.get(**kw)
    except cls._meta.model.DoesNotExist, e:
        raise PermissionDenied() # Raise permission denied instead of "does not exist" to make it impossible to "brute force" query for existing items

def _writeauth_get(cls, user, idorkw):
    obj = _getwrapper(cls, idorkw)
    cls.write_authorize(user, obj)
    return obj

def _readauth_get(cls, user, idorkw):
    obj = _getwrapper(cls, idorkw)
    cls.read_authorize(user, obj)
    return obj



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
        obj = _readauth_get(cls, user, idorkw) # authorization in _readauth_get
        resultfields = cls._meta.resultfields.aslist(result_fieldgroups)
        #if hasattr(cls, 'filter_read_resultfields'):
            #resultfields = cls.filter_read_resultfields(user, obj, resultfields)
        return modelinstance_to_dict(obj, resultfields)
    setattr(cls, read.__name__, MethodType(read, cls))

def create_delete_method(cls):
    def delete(cls, user, idorkw):
        """ Delete the given object.

        :param user: Django user object.
        :param idorkw: Id of object or kwargs to the get method of the configured model.
        :throws PermissionDenied:
            If the given user does not have permission to delete this object, or
            if the object does not exist.
        """
        obj = _writeauth_get(cls, user, idorkw) # authorization in _writeauth_get
        pk = obj.pk
        obj.delete()
        return pk
    setattr(cls, delete.__name__, MethodType(delete, cls))


def _set_values(obj, cls, field_values):
    for fieldname, value in field_values.iteritems():
        if not fieldname in cls._meta.editablefields:
            raise PermissionDenied('Field {fieldname} can not be edited.'.format(fieldname=fieldname))
        setattr(obj, fieldname, value)

def create_create_method(cls):
    """ Adds the ``create()`` method as a classmethod on the given class. """
    def create(cls, user, **field_values):
        """ Create the given object.

        :param user: Django user object.
        :field_values: The values to set on the given object.
        :throws PermissionDenied:
            If the given user does not have permission to edit this object,
            if the object does not exist, or if any of the ``field_values``
            is not in ``cls._meta.editablefields``.
        """
        obj =  cls._meta.model()
        _set_values(obj, cls, field_values)
        cls.write_authorize(user, obj) # Important that this is after parentnode is set on Nodes, or admins on parentnode will not be permitted!
        obj.full_clean()
        obj.save()
        return obj
    setattr(cls, create.__name__, MethodType(create, cls))

def create_update_method(cls):
    """ Adds the ``update()`` method as a classmethod on the given class. """
    def update(cls, user, idorkw, **field_values):
        """ Update the given object.

        :param user: Django user object.
        :param idorkw: Id of object or kwargs to the get method of the configured model.
        :field_values: The values to set on the given object.
        :throws PermissionDenied:
            If the given user does not have permission to edit this object,
            if the object does not exist, or if any of the ``field_values``
            is not in ``cls._meta.editablefields``.
        """
        obj = _getwrapper(cls, idorkw)
        _set_values(obj, cls, field_values)
        # Important to write authorize after _set_values in case any attributes
        # used in write_authorize is changed by _set_values.
        cls.write_authorize(user, obj)
        obj.full_clean()
        obj.save()
        return obj
    setattr(cls, update.__name__, MethodType(update, cls))

def create_search_method(cls):
    pass
