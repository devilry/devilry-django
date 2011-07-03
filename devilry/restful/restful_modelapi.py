from django import forms

from ..simplified import _require_metaattr
from restful_api import restful_api
import fields


def _create_seachform(cls):
    class SearchForm(forms.Form):
        query = forms.CharField(required=False)
        limit = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
        start = fields.PositiveIntegerWithFallbackField()
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=cls._meta.simplified._meta.ordering)
        result_fieldgroups = fields.CharListWithFallbackField()
        search_fieldgroups = fields.CharListWithFallbackField()
    cls.SearchForm = SearchForm


def _create_editform(cls):
    formfields = []
    model = cls._meta.simplified._meta.model
    for fieldname in cls._meta.simplified._meta.resultfields.always_available_fields:
        if fieldname.endswith("__id"):
            formfields.append(fieldname[:-4])
        else:
            formfields.append(fieldname)
    class EditForm(forms.ModelForm):
        class Meta:
            model = cls._meta.simplified._meta.model
            fields = formfields
    cls.EditForm = EditForm


def restful_modelapi(cls):
    """
    :class:`ModelRestfulView` is used in conjunction with the
    :class:`restful_modelapi`-decorator to autogenerate a RESTful
    interface for a simplified class (see :ref:`simplified`).

    The ``cls`` must have an inner class named ``Meta`` with
    the following required attributes:

        simplified
            A :ref:`simplified` class.

    Furthermore, this decorator automatically decorates ``cls`` with
    :func:`restful_api`.
    """
    cls = restful_api(cls)
    _require_metaattr(cls, 'simplified')
    _create_seachform(cls)
    _create_editform(cls)
    return cls
