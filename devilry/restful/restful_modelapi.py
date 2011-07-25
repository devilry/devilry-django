from types import MethodType
from inspect import getmodule

from ..simplified.modelapi import _require_metaattr
from restful_api import restful_api
from searchform import _create_seachform
from editform import _create_editform





def _copy_supports_metaattrs_from_simplified(cls):
    """ Copy all supports_[method] boolean variables from the simplified class. """
    for method in cls._meta.simplified._all_cruds_methods:
        attrname = 'supports_{0}'.format(method)
        setattr(cls, attrname, getattr(cls._meta.simplified, attrname))


def _create_get_foreignkey_fieldcls_method(cls):
    def get_foreignkey_fieldcls(cls, fkfieldname):
        """ Get the class stored at the ``fkfieldname`` key in the
        ``cls.foreignkey_fields``.

        :return: None if not found, and a restful class if found.
        """
        if not hasattr(cls, 'foreignkey_fields'):
            return None
        if not fkfieldname in cls.foreignkey_fields:
            return None
        fkrestfulcls = cls.foreignkey_fields[fkfieldname]
        if isinstance(fkrestfulcls, str): # Support giving the class name as string if in the same module. For recursive foreign keys, such as Node.parentnode.
            module = getmodule(cls)
            return getattr(module, fkrestfulcls)
        else:
            return fkrestfulcls
    setattr(cls._meta, get_foreignkey_fieldcls.__name__, MethodType(get_foreignkey_fieldcls, cls._meta))


def restful_modelapi(cls):
    """
    :class:`ModelRestfulView` is used in conjunction with the
    :class:`restful_modelapi`-decorator to autogenerate a RESTful
    interface for a simplified class (see :ref:`simplified`).

    The ``cls`` must have an inner class named ``Meta`` with
    the following attributes:

        simplified
            A :ref:`simplified` class. **Required**.
        foreignkey_fields
            A dictionary mapping foreign key fields to RESTful classes
            that contains the data for the foreign key field.

    The decorator automatically decorates ``cls`` with
    :func:`restful_api`.

    The decorator adds the following attributes to ``cls``:

        _meta
            Alias for the Meta class (above).
        supports_*
            Copied from ``_meta.simplified._meta``.
        SearchForm
            A Django form that can be used to validate the keyword arguments sent
            to the ``search()`` method in :ref:`simplified`.
        EditForm
            A Django model form that can be used to validate and edit the model
            specified in :ref:`simplified` specified in ``_meta.simplfied._meta.model``.
    """
    cls = restful_api(cls)
    _require_metaattr(cls, 'simplified')
    _create_seachform(cls)
    _create_editform(cls)
    _copy_supports_metaattrs_from_simplified(cls)
    _create_get_foreignkey_fieldcls_method(cls)

    return cls
