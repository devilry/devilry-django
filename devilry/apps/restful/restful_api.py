from django import forms
from django.utils import simplejson as json

from ..simplified.simplified_api import _require_metaattr
import fields



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


def _recurse_get_fkfield(modelcls, path):
    cur = modelcls._meta.get_field(path.pop(0))
    if not path:
        return cur
    else:
        return _recurse_get_fkfield(cur.related.model, path)

def _iter_fields(simplifiedcls):
    meta = simplifiedcls._meta
    for fieldname in meta.resultfields:
        if "__" in fieldname:
            path = fieldname.split('__')
            yield fieldname, _recurse_get_fkfield(meta.model, path)
        else:
            yield fieldname, meta.model._meta.get_field(fieldname)

def _create_extjs_model(cls):
    simplified = cls._meta.simplified
    tpl = """
    Ext.define('StatConfig', {
        extend: 'Ext.data.Model',
        fields: [
            %(fields)s
        ],
        idProperty: '%(idprop)s'
    });"""

    fields = []
    for fieldname, field in _iter_fields(simplified):
        exttype = cls.field_to_extjs_type(field, fieldname)
        fields.append(dict(name='fieldname', type=exttype))
    idprop = 'id'
    cls.extjs_model = tpl % dict(idprop=idprop, fields=json.dumps(fields))




def restful_api(cls):
    meta = cls.Meta
    cls._meta = meta
    _require_metaattr(cls, 'simplified')
    _create_seachform(cls)
    _create_editform(cls)
    _create_extjs_model(cls)
    return cls
