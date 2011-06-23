from django import forms

from ..simplified.simplified_api import _require_metaattr
import fields


class UrlMapping(object):
    def __init__(self, restfulcls, idfield):
        self.restfulcls = restfulcls
        self.idfield = idfield


def _create_seachform(cls):
    class SearchForm(forms.Form):
        #format = fields.FormatField()
        query = forms.CharField(required=False)
        limit = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
        start = fields.PositiveIntegerWithFallbackField()
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=cls._meta.simplified._meta.ordering)
    cls.SearchForm = SearchForm


def _create_editform(cls):
    formfields = []
    model = cls._meta.simplified._meta.model
    for fieldname in cls._meta.simplified._meta.resultfields:
        if fieldname.endswith("__id"):
            formfields.append(fieldname[:-4])
        else:
            formfields.append(fieldname)
    class EditForm(forms.ModelForm):
        class Meta:
            model = cls._meta.simplified._meta.model
            fields = formfields
    cls.EditForm = EditForm


def restful_api(cls):
    try:
        meta = cls.Meta
    except AttributeError:
        class Meta:
            """ Fake meta class """
        meta = Meta
    cls._meta = meta
    cls._meta.urlprefix = cls.__name__.lower()
    if not hasattr(cls._meta, 'urlmap'):
        cls._meta.urlmap = {}
    urlname = '%s-%s' % (cls.__module__, cls.__name__)
    cls._meta.urlname = urlname.replace('.', '-')
    return cls


def restful_modelapi(cls):
    cls = restful_api(cls)
    _require_metaattr(cls, 'simplified')
    model = cls._meta.simplified._meta.model
    _create_seachform(cls)
    _create_editform(cls)
    return cls
