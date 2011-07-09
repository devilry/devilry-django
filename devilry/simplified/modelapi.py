from django.db.models.fields import AutoField
import create


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
        _meta.editablefields
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
    if 'read' in cls._meta.methods:
        _require_attr(cls, 'read_authorize')
    writemethods = set(['create', 'insecure_read_model', 'update', 'delete'])
    if cls._meta.methods and cls._meta.methods.issubset(writemethods): # Check for empty methods to support empty methods list ([] is a subset of any set)
        _require_attr(cls, 'write_authorize')

    # Dynamically create create(), read(), insecure_read_model(), update(), delete()
    for method in cls._meta.methods:
        getattr(create, 'create_{methodname}_method'.format(methodname=method))(cls) # Calls create.create_[CRUD+S]_method(cls)

    cls._all_crud_methods = ('create', 'read', 'insecure_read_model', 'update', 'delete')
    for method in cls._all_crud_methods:
        setattr(cls, 'supports_{0}'.format(method), method in cls._meta.methods)
    return cls
