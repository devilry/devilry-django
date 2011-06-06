from types import MethodType

from django.db.models.fields.related import RelatedObject, ManyToManyField

from getqryresult import GetQryResult


def _create_doc(cls, fieldnames=None):
    meta = cls._meta
    clspath = '%s.%s' % (cls.__module__, cls.__name__)
    fieldnames = fieldnames or meta.model._meta.get_all_field_names()
    resultfields = []
    for fieldname in fieldnames:
        field = meta.model._meta.get_field_by_name(fieldname)[0]
        if isinstance(field, ManyToManyField):
            pass
        elif isinstance(field, RelatedObject):
            pass
        else:
            if hasattr(field, 'help_text'):
                help_text = field.help_text
            else:
                help_text = ''
            #print type(field), field.name, help_text
            resultfields.append(':param %s: %s' % (field.name, help_text))

    #throws = [
            #':throws devilry.apps.core.models.Node.DoesNotExist:',
            #'   If the node with ``id`` does not exists, or if',
            #'   parentnode is not None, and no node with ``id==parentnode_id``',
            #'   exists.']

    get_doc = '\n'.join(
            ['Get a %(modelname)s object.'] + ['\n'] +
            throws + ['\n\n'] + resultfields)
    modelname = meta.model.__name__
    return get_doc % vars()


def _create_get_method(cls):
    def get(cls, user, id):
        if isinstance(id, dict):
            kw = id
        else:
            kw = dict(id=id)
        obj = cls._meta.model.objects.get(**kw)
        cls.authorize(user, obj)
        return obj
    setattr(cls, get.__name__, MethodType(get, cls))
    #cls.get.__func__.__doc__

def _create_delete_method(cls):
    def delete(cls, user, id):
        obj = cls.get(user, id) # authorization in cls.get()
        obj.delete()
    setattr(cls, delete.__name__, MethodType(delete, cls))

def _create_update_method(cls):
    def update(cls, user, id, **field_values):
        obj = cls.get(user, id)
        for fieldname, value in field_values.iteritems():
            setattr(obj, fieldname, value)
        obj.full_clean()
        obj.save()
        return obj
    setattr(cls, update.__name__, MethodType(update, cls))

def _create_create_method(cls):
    def create(cls, user, **field_values):
        obj =  cls._meta.model(**field_values)
        cls.authorize(user, obj) # Important that this is after parentnode is set on Nodes, or admins on parentnode will not be permitted!
        obj.full_clean()
        obj.save()
        return obj
    setattr(cls, create.__name__, MethodType(create, cls))


def _parse_fieldspec(fieldlst, fieldgroups):
    if isinstance(fieldlst, dict):
        base = fieldlst.get('__BASE__', [])
        fields = list(base)
        for group in fieldgroups:
            fields.extend(fieldlst.get(group, []))
        return fields
    else:
        return fieldlst

def _create_search_method(cls):
    def search(cls, user, **kwargs):
        resultfields = _parse_fieldspec(cls._meta.search_resultfields,
                kwargs.pop('search_fieldgroups', []))
        searchfields = _parse_fieldspec(cls._meta.search_searchfields,
                kwargs.pop('result_fieldgroups', []))
        qryset = cls.create_searchqryset(user, **kwargs)
        result = GetQryResult(resultfields, searchfields, qryset)
        standard_opts = dict(
            query = kwargs.pop('query', ''),
            start = kwargs.pop('start', 0),
            limit = kwargs.pop('limit', 50),
            orderby = kwargs.pop('orderby', cls._meta.ordering)
        )
        result._standard_operations(**standard_opts)
        return result
    setattr(cls, search.__name__, MethodType(search, cls))


def simplified_api(cls):
    #bases = tuple([SimplifiedBase] + list(cls.__bases__))
    #cls = type(cls.__name__, bases, dict(cls.__dict__))
    meta = cls.Meta
    cls._meta = meta
    cls._meta.ordering = cls._meta.model._meta.ordering
    if not hasattr(meta, 'methods'):
        cls._meta.methods = []
    for method in cls._meta.methods:
        globals()['_create_%s_method' % method](cls)
        #_create_get_method(cls)
        #_create_delete_method(cls)
        #_create_update_method(cls)
        #_create_create_method(cls)
        #_create_search_method(cls)
    return cls
