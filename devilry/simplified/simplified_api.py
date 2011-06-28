from types import MethodType

from django.db.models.fields.related import RelatedObject, ManyToManyField

from getqryresult import GetQryResult


def _create_read_doc(cls, fieldnames=None):
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
            #'   If the node with ``idorkw`` does not exists, or if',
            #'   parentnode is not None, and no node with ``id==parentnode_id``',
            #'   exists.']

    get_doc = '\n'.join(
            ['Get a %(modelname)s object.'] + ['\n\n'] + resultfields)
    modelname = meta.model.__name__
    return get_doc % vars()


def _parse_fieldgroups(fieldlst, fieldgroups):
    if isinstance(fieldlst, dict):
        base = fieldlst.get('__BASE__', [])
        fields = list(base)
        for group in fieldgroups:
            fields.extend(fieldlst.get(group, []))
        return fields
    else:
        return fieldlst


def _writeauth_get(cls, user, idorkw):
    if isinstance(idorkw, dict):
        kw = idorkw
    else:
        kw = dict(pk=idorkw)
    obj = cls._meta.model.objects.get(**kw)
    cls.write_authorize(user, obj)
    return obj

def _readauth_get(cls, user, idorkw):
    if isinstance(idorkw, dict):
        kw = idorkw
    else:
        kw = dict(pk=idorkw)
    obj = cls._meta.model.objects.get(**kw)
    cls.read_authorize(user, obj)
    return obj


def _recurse_getmodelattr(instance, path):
    cur = getattr(instance, path.pop(0))
    if not path:
        return cur
    else:
        return _recurse_getmodelattr(cur, path)

def _model_to_dict(instance, fields):
    dct = {}
    for field in fields:
        if "__" in field:
            path = field.split('__')
            dct[field] = _recurse_getmodelattr(instance, path)
        else:
            dct[field] = getattr(instance, field)
    return dct


def _create_create_method(cls):
    def create(cls, user, **field_values):
        obj =  cls._meta.model(**field_values)
        cls.write_authorize(user, obj) # Important that this is after parentnode is set on Nodes, or admins on parentnode will not be permitted!
        obj.full_clean()
        obj.save()
        return obj
    setattr(cls, create.__name__, MethodType(create, cls))

def _create_read_model_method(cls):
    def read_model(cls, user, idorkw):
        return _writeauth_get(cls, user, idorkw)
    setattr(cls, read_model.__name__, MethodType(read_model, cls))
    #cls.get.__func__.__doc__

def _create_read_method(cls):
    def read(cls, user, idorkw, result_fieldgroups=[]):
        """
        :param user: Django user object.
        :param idorkw: Id of object or kwargs to the get method of the configured model.
        :result_fieldgroups: List of additions to the __BASE__ list if resultfields is a dict.
        """
        obj = _readauth_get(cls, user, idorkw) # authorization in _writeauth_get
        resultfields = _parse_fieldgroups(cls._meta.resultfields,
                result_fieldgroups)
        #if hasattr(cls, 'filter_read_resultfields'):
            #resultfields = cls.filter_read_resultfields(user, obj, resultfields)
        return _model_to_dict(obj, fields=resultfields)
    setattr(cls, read.__name__, MethodType(read, cls))

def _create_delete_method(cls):
    def delete(cls, user, idorkw):
        obj = _writeauth_get(cls, user, idorkw) # authorization in _writeauth_get
        pk = obj.pk
        obj.delete()
        return pk
    setattr(cls, delete.__name__, MethodType(delete, cls))

def _create_update_method(cls):
    def update(cls, user, idorkw, **field_values):
        obj = _writeauth_get(cls, user, idorkw) # authorization in _writeauth_get
        for fieldname, value in field_values.iteritems():
            setattr(obj, fieldname, value)
        obj.full_clean()
        obj.save()
        return obj
    setattr(cls, update.__name__, MethodType(update, cls))

def _create_search_method(cls):
    def search(cls, user, **kwargs):
        """
        :param start:
        :param limit:
        :param orderby:
        :return: The result of fiter() on cls.meta.model.
        :rtype: QuerySet
        """
        resultfields = _parse_fieldgroups(cls._meta.resultfields,
                    kwargs.pop('result_fieldgroups', []))
        searchfields = _parse_fieldgroups(cls._meta.searchfields,
                kwargs.pop('search_fieldgroups', []))
        qryset = cls.create_searchqryset(user, **kwargs)
        if isinstance(qryset, GetQryResult):
            result = qryset
        else:
            result = GetQryResult(resultfields, searchfields, qryset)
        standard_opts = dict(
            query = kwargs.pop('query', None),
            start = kwargs.pop('start', 0),
            limit = kwargs.pop('limit', 50),
            orderby = kwargs.pop('orderby', cls._meta.ordering)
        )
        result._standard_operations(**standard_opts)
        return result
    setattr(cls, search.__name__, MethodType(search, cls))

def _require_metaattr(cls, attr):
    if not hasattr(cls._meta, attr):
        raise ValueError('%s.%s.Meta is missing the required "%s" attribute.' % (
            cls.__module__, cls.__name__, attr))
def _require_attr(cls, attr):
    if not hasattr(cls, attr):
        raise ValueError('%s.%s is missing the required "%s" attribute.' % (
            cls.__module__, cls.__name__, attr))

def simplified_api(cls):
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
    cls._meta.methods = set(cls._meta.methods)
    if 'read' in cls._meta.methods:
        _require_attr(cls, 'read_authorize')
    if cls._meta.methods.issubset(set(['create', 'read_model', 'update', 'delete'])):
        _require_attr(cls, 'write_authorize')

    # Dynamically create create(), read(), read_model(), update(), delete()
    for method in cls._meta.methods:
        globals()['_create_%s_method' % method](cls)
    return cls
