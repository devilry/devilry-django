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


def _get_clsref_even_if_string(cls, attrname):
    if not hasattr(cls, attrname):
        return None
    attr = getattr(cls, attrname)
    if isinstance(attr, str):
        module = getmodule(cls)
        return getattr(module, attr)
    else:
        return attr

def _create_belongs_to_method(cls):
    def get_belongs_to(cls):
        """ Get the belongs_to attribute as a class, or None (if no belongs_to is defined).

        If belongs_to is a string, look up the string in the module.
        """
        return _get_clsref_even_if_string(cls, 'belongs_to')
    setattr(cls._meta, get_belongs_to.__name__, MethodType(get_belongs_to, cls._meta))


def _create_has_many_method(cls):
    def get_has_many(cls):
        """ Get the has_many attribute as a class, or None (if no has_many is defined).

        If has_many is a string, look up the string in the module.
        """
        return _get_clsref_even_if_string(cls, 'has_many')
    setattr(cls._meta, get_has_many.__name__, MethodType(get_has_many, cls._meta))

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
    if not hasattr(cls._meta, 'fake_editablefields_formfields'):
        cls._meta.fake_editablefields_formfields = {}
    _create_editform(cls)
    _copy_supports_metaattrs_from_simplified(cls)
    _create_belongs_to_method(cls)
    _create_has_many_method(cls)

    return cls
