from types import MethodType
from django.db.models.fields import AutoField, FieldDoesNotExist
from django.db import transaction


from qryresultwrapper import QryResultWrapper
from utils import modelinstance_to_dict, get_field_from_fieldname, get_clspath
from exceptions import PermissionDenied, InvalidNumberOfResults
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
        editablefields = [f for f in cls._meta.resultfields.localfields_aslist() \
                if not f in cls._meta.annotated_fields]
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
        """ Check if the given user has write (update/create) permission on the given obj.

        Defaults to raising :exc:NotImplementedError

        :raise PermissionDenied: If the given user do not have write permission on the given obj.
        """
        raise NotImplementedError()

    @classmethod
    def read_authorize(cls, user, obj):
        """ Check if the given user has read permission on the given obj.

        Defaults to ``cls.write_authorize(user, obj)``

        :raise PermissionDenied: If the given user do not have read permission on the given obj.
        """
        cls.write_authorize(user, obj)

    @classmethod
    def is_empty(cls, obj):
        """ Check if the given obj is empty. Defaults to returning ``False``.

        Can be implemented in subclasses to enable superadmins to recursively :meth:`delete` the ``obj``.
        """
        return False

    @classmethod
    def _getwrapper(cls, pk):
        kw = dict(pk=pk)
        try:
            return cls._meta.model.objects.get(**kw)
        except cls._meta.model.DoesNotExist, e:
            raise PermissionDenied() # Raise permission denied instead of "does not exist" to make it impossible to "brute force" query for existing items

    @classmethod
    def _writeauth_get(cls, user, pk):
        obj = cls._getwrapper(pk)
        cls.write_authorize(user, obj)
        return obj

    @classmethod
    def _set_values(cls, obj, field_values):
        for fieldname, value in field_values.iteritems():
            if not fieldname in cls._meta.editablefields and not fieldname in cls._meta.fake_editablefields:
                raise PermissionDenied('Field {fieldname} can not be edited.'.format(fieldname=fieldname))
            setattr(obj, fieldname, value)

    @classmethod
    def _readauth_get(cls, user, pk):
        obj = cls._getwrapper(pk)
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
        orderbyfields = cls._meta.orderbyfields
        resultfields = cls._meta.resultfields.aslist(result_fieldgroups)
        searchfields = cls._meta.searchfields.aslist(search_fieldgroups)
        result = QryResultWrapper(resultfields, searchfields, qryset, orderbyfields)
        return result

    @classmethod
    def pre_full_clean(cls, user, obj):
        """
        Invoked after the user has been authorize by :meth:`write_authorize` and
        before ``obj.full_clean()`` in :meth:`create` and :meth:`update`.

        Override this to set custom/generated values on ``obj`` before it is
        validated and saved. The default does nothing.
        """

    @classmethod
    def post_save(cls, user, obj):
        """
        Invoked after the ``obj`` has been saved.

        Override this to set custom/generated values on ``obj`` after it has been
        validated and saved. The default does nothing.
        """

    @classmethod
    def _create(cls, user, **field_values):
        obj = cls._meta.model()
        cls._set_values(obj, field_values)
        cls.write_authorize(user, obj) # Important that this is after parentnode is set on Nodes, or admins on parentnode will not be permitted!
        cls.pre_full_clean(user, obj)
        obj.full_clean()
        obj.save()
        cls.post_save(user, obj)
        return obj.pk

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
        with transaction.commit_on_success():
            return cls._create(user, **field_values)

    @classmethod
    def createmany(cls, user, *list_of_field_values):
        """ Create many.

        This does the same as calling :meth:`create` many times, except that it
        does it all in a single transaction. This means that the database rolls
        back the changes unless they all succeed.

        :param: list_of_field_values
            List of field_values dicts (see :meth:`create`).
        :return: List of the primary keys of the created objects.
        """
        pks = []
        with transaction.commit_manually():
            for field_values in list_of_field_values:
                pks.append(cls._create(user, **field_values))
            transaction.commit()
        return pks

    @classmethod
    def read(cls, user, pk, result_fieldgroups=[]):
        """ Read the requested item and return a dict with the fields specified
        in ``Meta.resultfields`` and additional fields specified in
        ``result_fieldgroups``.

        :param user: Django user object.
        :param pk: Id of object or kwargs to the get method of the configured model.
        :param result_fieldgroups:
            Fieldgroups from the additional_fieldgroups specified in
            ``result_fieldgroups``.

        :throws PermissionDenied:
            If the given user does not have permission to view this object, or
            if the object does not exist.
        """
        obj = cls._readauth_get(user, pk) # authorization in cls._readauth_get
        resultfields = cls._meta.resultfields.aslist(result_fieldgroups)
        return modelinstance_to_dict(obj, resultfields)

    @classmethod
    def _update(cls, user, pk, **field_values):
        obj = cls._getwrapper(pk)
        cls._set_values(obj, field_values)
        # Important to write authorize after _set_values in case any attributes
        # used in write_authorize is changed by _set_values.
        cls.write_authorize(user, obj)
        cls.pre_full_clean(user, obj)
        obj.full_clean()
        obj.save()
        cls.post_save(user, obj)
        return obj.pk

    @classmethod
    def update(cls, user, pk, **field_values):
        """ Update the given object.

        :param user: Django user object.
        :param pk: Id of object or kwargs to the get method of the configured model.
        :param: field_values: The values to set on the given object.

        :return: The primary key of the updated object.
        :throws PermissionDenied:
            If the given user does not have permission to edit this object,
            if the object does not exist, or if any of the ``field_values``
            is not in ``cls._meta.editablefields``.
        """
        with transaction.commit_on_success():
            return cls._update(user, pk, **field_values)

    @classmethod
    def updatemany(cls, user, *list_of_field_values):
        """ Update many.

        This does the same as calling :meth:`update` many times, except that it
        does it all in a single transaction. This means that the database rolls
        back the changes unless they all succeed.

        :param: list_of_field_values
            List of field_values dicts (see :meth:`update`). Each dict _must_
            have a _pk_ key that maps to the primary-key/id value.
        :return: List of the primary keys of the updated objects.
        """
        pks = []
        with transaction.commit_manually():
            for field_values in list_of_field_values:
                pk = field_values['pk']
                del field_values['pk']
                cls._update(user, pk, **field_values)
                pks.append(pk)
            transaction.commit()
        return pks

    @classmethod
    def _delete(cls, user, pk):
        obj = cls._writeauth_get(user, pk) # authorization in cls._writeauth_get
        if not cls.is_empty(obj):
            if not user.is_superuser:
                raise PermissionDenied()
        pk = obj.pk
        obj.delete()
        return pk

    @classmethod
    def delete(cls, user, pk):
        """ Delete the given object. If the object :meth:`is_empty` it can be
        deleted by any user with :meth:`write_authorize`,
        if not then only a Superuser may delete the object

        :param user: Django user object.
        :param pk: Id of object or kwargs to the get method of the configured model.

        :return: The primary key of the deleted object.
        :throws PermissionDenied:
            If the given user does not have permission to delete this object,
            if the object does not exist, or if the user does not have permission
            to recursively delete this objects and all its children.
        """
        with transaction.commit_on_success():
            cls._delete(user, pk)

    @classmethod
    def deletemany(cls, user, *list_of_pks):
        """ Delete many.

        This does the same as calling :meth:`delete` many times, except that it
        does it all in a single transaction. This means that the database rolls
        back the changes unless they all succeed.

        :param: list_of_pks
            List of primary-keys/ids of the objects to delete.
        :return: List of the primary keys of the deleted objects.
        """
        with transaction.commit_manually():
            for pk in list_of_pks:
                cls._delete(user, pk)
            transaction.commit()
        return list_of_pks

    @classmethod
    def search(cls, user,
               query = '', start = 0, limit = 50, orderby = None,
               result_fieldgroups=None, search_fieldgroups=None,
               filters={}, exact_number_of_results=None):
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
        :param exact_number_of_results:
            Expect this exact number of results. If unspecified (``None``),
            this check is not performed. If the check fails,
            :exc:`devilry.simplified.InvalidNumberOfResults` is raised.

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
        if exact_number_of_results != None:
            resultcount = len(result)
            if exact_number_of_results != resultcount:
                raise InvalidNumberOfResults('Expected {exact_number_of_results}, '
                                             'got {resultcount}.'.format(resultcount = resultcount,
                                                                         exact_number_of_results=exact_number_of_results))
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
            if hasattr(cls._meta, 'annotated_fields'):
                if fieldname in cls._meta.annotated_fields:
                    continue
            raise SimplifiedConfigError('{0}.{1}: Invalid field name: {2}.'.format(get_clspath(cls),
                                                                                   attribute,
                                                                                   fieldname))



class UnsupportedCrudsMethod(Exception):
    """
    Raised when trying to call an unsupperted CRUD+S method (a method on in Meta.methods).
    """

def _create_unsupported_cruds_method(cls, methodname):
    def wrapper(cls, *args, **kwargs):
        raise UnsupportedCrudsMethod("Unsupperted CRUD+S method: {}".format(methodname))
    setattr(cls, methodname, MethodType(wrapper, cls))


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
                - update
                - delete
                - search

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
    _validate_fieldnameiterator(cls, 'Meta.resultfields', cls._meta.resultfields)
    _require_metaattr(cls, 'searchfields')
    _validate_fieldnameiterator(cls, 'Meta.searchfields', cls._meta.searchfields)
    if not hasattr(cls._meta, 'orderbyfields'):
        cls._meta.orderbyfields = []
    cls._meta.orderbyfields = list(cls._meta.orderbyfields)
    if not hasattr(cls._meta, 'annotated_fields'):
        cls._meta.annotated_fields = tuple()
    _create_meta_ediablefields(cls)
    if not hasattr(cls._meta, 'fake_editablefields'):
        cls._meta.fake_editablefields = tuple()
    _create_meta_ediable_fieldgroups(cls)
    cls._meta.methods = set(cls._meta.methods)

    # Dynamically remove create(), read(), update(), delete() and search() if not supported
    cls._all_cruds_methods = ('create', 'read', 'update', 'delete', 'search')
    for method in cls._all_cruds_methods:
        if not method in cls._meta.methods:
            _create_unsupported_cruds_method(cls, method)
            #setattr(cls, method, None)

    for method in cls._all_cruds_methods:
        setattr(cls, 'supports_{0}'.format(method), method in cls._meta.methods)

    if hasattr(cls._meta, 'filters'):
        _validate_fieldnameiterator(cls, 'Meta.filters', cls._meta.filters)
    else:
        cls._meta.filters = FilterSpecs()
    return cls
