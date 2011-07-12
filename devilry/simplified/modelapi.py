from django.db.models.fields import AutoField, FieldDoesNotExist

from qryresultwrapper import QryResultWrapper
from utils import modelinstance_to_dict, get_field_from_fieldname, get_clspath
from exceptions import PermissionDenied
from filterspec import FilterSpecs



def _require_metaattr(cls, attr):
    """ Note that this method is also used in ``devilry.restful``. """
    if not hasattr(cls._meta, attr):
        raise ValueError('{modulename}.{classname}.Meta is missing the '
                         'required "{attr}" attribute.'.format(modulename=cls.__module__,
                                                               classname=cls.__name__,
                                                               attr=attr))
def _require_attr(cls, attr):
    if not hasattr(cls, attr):
        raise ValueError('{modulename}.{classname} is missing the '
                         'required "{attr}" attribute.'.format(modulename=cls.__module__,
                                                               classname=cls.__name__,
                                                               attr=attr))

def _create_meta_ediablefields(cls):
    if hasattr(cls._meta, 'editablefields'):
        editablefields = cls._meta.editablefields
    else:
        editablefields = cls._meta.resultfields.localfields_aslist()
        pk = cls._meta.model._meta.pk
        if pk.get_attname() in editablefields:
            if isinstance(pk, AutoField):
                editablefields.remove(pk.get_attname())
    cls._meta.editablefields = set(editablefields)

def _create_meta_ediable_fieldgroups(cls):
    if not hasattr(cls._meta, 'editable_fieldgroups'):
        cls._meta.editable_fieldgroups = cls._meta.resultfields.localfieldgroups_aslist()




class SimplifiedModelApi(object):
    """
    Base class for all simplified APIs.
    """
    @classmethod
    def write_authorize(cls, user, obj):
        raise NotImplementedError()

    @classmethod
    def read_authorize(cls, user, obj):
        cls.write_authorize(user, obj)

    @classmethod
    def _getwrapper(cls, idorkw):
        if isinstance(idorkw, dict):
            kw = idorkw
        else:
            kw = dict(pk=idorkw)
        try:
            return cls._meta.model.objects.get(**kw)
        except cls._meta.model.DoesNotExist, e:
            raise PermissionDenied() # Raise permission denied instead of "does not exist" to make it impossible to "brute force" query for existing items

    @classmethod
    def _writeauth_get(cls, user, idorkw):
        obj = cls._getwrapper(idorkw)
        cls.write_authorize(user, obj)
        return obj

    @classmethod
    def _set_values(cls, obj, field_values):
        for fieldname, value in field_values.iteritems():
            if not fieldname in cls._meta.editablefields:
                raise PermissionDenied('Field {fieldname} can not be edited.'.format(fieldname=fieldname))
            setattr(obj, fieldname, value)

    @classmethod
    def _readauth_get(cls, user, idorkw):
        obj = cls._getwrapper(idorkw)
        cls.read_authorize(user, obj)
        return obj

    @classmethod
    def handle_fieldgroups(cls, user,
                           result_fieldgroups, search_fieldgroups,
                           filters):
        """
        Can be overridden to change fieldgroups before they are sent into the
        QryResultWrapper. For example, if certain fieldgroups contain
        senstive data for anonymous assignments, we can add those fieldgroups
        if a filter for a specific assignment is provided in ``filters`` and
        that assignment is not anonymous.

        :return: (result_fieldgroups, search_fieldgroups)
        """
        return result_fieldgroups, search_fieldgroups

    @classmethod
    def create_searchqryset(cls, user):
        """
        Create search queryset.

        :return: A Django QuerySet.
        """
        raise NotImplementedError()

    @classmethod
    def _create_search_qryresultwrapper(cls, user,
                                       result_fieldgroups, search_fieldgroups,
                                       filters,
                                       filterqry):
        """
        :param validatedfilters:
            Filters which are applied to the QuerySet returned by
            :meth:`create_searchqryset`.

        :return: A :class:`QryResultWrapper`.
        """
        qryset = cls.create_searchqryset(user)
        qryset = qryset.filter(filterqry)
        result_fieldgroups, search_fieldgroups = cls.handle_fieldgroups(user,
                                                                        result_fieldgroups,
                                                                        search_fieldgroups,
                                                                        filters)
        resultfields = cls._meta.resultfields.aslist(result_fieldgroups)
        searchfields = cls._meta.searchfields.aslist(search_fieldgroups)
        result = QryResultWrapper(resultfields, searchfields, qryset)
        return result

    @classmethod
    def create(cls, user, **field_values):
        """ Create the given object.

        :param user: Django user object.
        :field_values: The values to set on the given object.
        :return: The primary key of the newly created object.
        :throws PermissionDenied:
            If the given user does not have permission to edit this object,
            if the object does not exist, or if any of the ``field_values``
            is not in ``cls._meta.editablefields``.
        """
        obj =  cls._meta.model()
        cls._set_values(obj, field_values)
        cls.write_authorize(user, obj) # Important that this is after parentnode is set on Nodes, or admins on parentnode will not be permitted!
        obj.full_clean()
        obj.save()
        return obj.pk

    @classmethod
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
        obj = cls._readauth_get(user, idorkw) # authorization in cls._readauth_get
        resultfields = cls._meta.resultfields.aslist(result_fieldgroups)
        return modelinstance_to_dict(obj, resultfields)

    @classmethod
    def insecure_read_model(cls, user, idorkw):
        """ Read the requested item and return a django model object.

        :param user: Django user object.
        :param idorkw: Id of object or kwargs to the get method of the configured model.

        :throws PermissionDenied:
            If the given user does not have permission to
            view this object, or if the object does not exist.
        """
        return cls._writeauth_get(user, idorkw)

    @classmethod
    def update(cls, user, idorkw, **field_values):
        """ Update the given object.

        :param user: Django user object.
        :param idorkw: Id of object or kwargs to the get method of the configured model.
        :param: field_values: The values to set on the given object.

        :return: The primary key of the updated object.
        :throws PermissionDenied:
            If the given user does not have permission to edit this object,
            if the object does not exist, or if any of the ``field_values``
            is not in ``cls._meta.editablefields``.
        """
        obj = cls._getwrapper(idorkw)
        cls._set_values(obj, field_values)
        # Important to write authorize after _set_values in case any attributes
        # used in write_authorize is changed by _set_values.
        cls.write_authorize(user, obj)
        obj.full_clean()
        obj.save()
        return obj.pk

    @classmethod
    def delete(cls, user, idorkw):
        """ Delete the given object.

        :param user: Django user object.
        :param idorkw: Id of object or kwargs to the get method of the configured model.

        :return: The primary key of the deleted object.
        :throws PermissionDenied:
            If the given user does not have permission to delete this object, or
            if the object does not exist.
        """
        obj = cls._writeauth_get(user, idorkw) # authorization in cls._writeauth_get
        pk = obj.pk
        obj.delete()
        return pk

    @classmethod
    def search(cls, user,
               query = '', start = 0, limit = 50, orderby = None,
               result_fieldgroups=None, search_fieldgroups=None,
               filters={}):
        """ Search for objects.

        :param query:
            A string to search for within the model specified in
            ``Meta.model``. The fields to search for is specified in
            ``Meta.search_fieldgroups``.
        :param start:
            Return results from this index in the results from the given
            ``query``. Defaults to ``0``.
        :param limit:
            Limit results to this number of items. Defaults to ``50``.
        :param orderby:
            List of fieldnames. Fieldnames can be prefixed by ``'-'`` for
            descending ordering.  Order the result by these fields. For
            example, if ``Meta.resultfields`` contains the short_name and
            long_name fields, we can order our results by ascending short_name
            and descending long_name as this: ``orderby=('short_name',
            '-long_name')``.  This defaults to ``cls._meta.ordering`` (see
            :func:`devilry.simplified.simplified_modelapi`).
        :param result_fieldgroups:
            Adds additional fields to the result. Available values are the
            fieldgroups in ``Meta.resultfields.additional_fieldgroups``.
        :param search_fieldgroups:
            Adds additional fields which are searched for the ``query`` string.
            Available values are the fieldgroups in
            ``Meta.searchfields.additional_fieldgroups``.
        :param filters:
            List of filters that can be parsed by :meth:`devilry.simplified.FilterSpec.parse`.

        :return: The result of the search.
        :rtype: QryResultWrapper
        """
        filterqry = cls._meta.filters.parse(filters)
        result = cls._create_search_qryresultwrapper(user,
                                                    result_fieldgroups, search_fieldgroups,
                                                    filters, filterqry)
        orderby = orderby or cls._meta.ordering
        result._query_order_and_limit(query = query,
                                    start = start,
                                    limit = limit,
                                    orderby = orderby)
        return result


class SimplifiedConfigError(Exception):
    """
    Raised when :func:`simplified_modelapi` discovers a configuration error.
    """


def _validate_fieldnameiterator(cls, attribute, fieldnameiterator):
    for fieldname in fieldnameiterator.iterfieldnames():
        try:
            get_field_from_fieldname(cls._meta.model, fieldname)
        except FieldDoesNotExist, e:
            raise SimplifiedConfigError('{0}.{1}: Invalid field name: {2}.'.format(get_clspath(cls),
                                                                                   attribute,
                                                                                   fieldname))

def simplified_modelapi(cls):
    """ Decorator which creates a simplified API for a Django model.

    The ``cls`` must have an inner class named ``Meta`` with
    the following attributes:

        model
            Then Django model. **Required**.
        methods
            A list of supported CRUD+S methods. **Required**. Legal values are:

                - create
                - read
                - insecure_read_model
                - update
                - delete
        resultfields
            A :class:`FieldSpec` which defines what fields to
            return from ``read()`` and ``search()``. **Required**.
        searchfields
            A :class:`FieldSpec` which defines what fields to
            search in ``search()``. **Required**.
        editablefields
            A list of fields that are editable. If this is not specified,
            it defaults to ``resultfields.localfields_aslist()`` with
            the primary key field removed if it is a AutoField.

            Only fields in this set may be given as ``field_values``
            to ``update()`` or ``create()``. Furthermore, these
            fields are used to generate forms in :ref:`restful`.
        editable_fieldgroups
            A list of result field groups which should at least contain
            all fields in ``editablefields``. Defaults to
            ``resultfields.localfieldgroups_aslist()``
        filters
            A :class:`devilry.simplified.FilterSpecs` limiting the possible
            filters to perform. Defaults to an empty ``FilterSpec``.

    The ``cls`` must have the following methods for handling permissions:

        read_authorize
            Authorization method used for each call to ``read()``.
        write_authorize
            Authorization method used for each call to any CRUD+S
            method except for ``read()``.
        create_searchqryset
            Method used to create the queryset filtered in search().
            Required if ``"search"`` is in ``Meta.methods``.

    The decorator adds the following attributes to ``cls``:

        _meta
            Alias for the Meta class (above).
        supports_create
            Boolean variable: is ``'create'`` in ``_meta.methods``.
        supports_read
            Boolean variable: is ``'read'`` in ``_meta.methods``.
        supports_insecure_read_model
            Boolean variable: is ``'insecure_read_model'`` in ``_meta.methods``.
        supports_update
            Boolean variable: is ``'update'`` in ``_meta.methods``.
        supports_delete
            Boolean variable: is ``'delete'`` in ``_meta.methods``.

    """
    #bases = tuple([SimplifiedBase] + list(cls.__bases__))
    #cls = type(cls.__name__, bases, dict(cls.__dict__))
    meta = cls.Meta
    cls._meta = meta
    cls._meta.ordering = cls._meta.model._meta.ordering

    # Check required meta options
    _require_metaattr(cls, 'model')
    _require_metaattr(cls, 'methods')
    _require_metaattr(cls, 'resultfields')
    _require_metaattr(cls, 'searchfields')
    _create_meta_ediablefields(cls)
    _create_meta_ediable_fieldgroups(cls)
    cls._meta.methods = set(cls._meta.methods)

    if hasattr(cls._meta, 'filters'):
        _validate_fieldnameiterator(cls, 'Meta.filters', cls._meta.filters)
    else:
        cls._meta.filters = FilterSpecs()

    # Dynamically remove create(), read(), insecure_read_model(), update(), delete() if not supported
    cls._all_crud_methods = ('create', 'read', 'insecure_read_model', 'update', 'delete')
    for method in cls._all_crud_methods:
        if not method in cls._meta.methods:
            setattr(cls, method, None)

    for method in cls._all_crud_methods:
        setattr(cls, 'supports_{0}'.format(method), method in cls._meta.methods)
    return cls
