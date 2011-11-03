""" General purpose utilities used by the simplified API. If any functions here
proves useful outside this module, they should me moved to ``devilry.utils``. """
from django.db.models.fields.related import ForeignKey
from django.db.models.fields import FieldDoesNotExist
from django.db.models import Max, Count
from fieldspec import OneToMany


def get_clspath(cls):
    return '{0}.{1}'.format(cls.__module__, cls.__name__)

def get_field_from_fieldname(modelcls, fieldname, fkfield_as_idfield=False):
    def _recurse_get_modelfield(modelcls, path):
        pathseg = path.pop(0)
        field = modelcls._meta.get_field_by_name(pathseg)[0]
        if isinstance(field, ForeignKey):
            parentmodel = field.related.parent_model
            if len(path) == 0:
                if fkfield_as_idfield:
                    return _recurse_get_modelfield(parentmodel, ['id'])
                return field
            return _recurse_get_modelfield(parentmodel, path)
        else:
            return field
    if isinstance(fieldname, OneToMany):
        pass
    else:
        return _recurse_get_modelfield(modelcls, fieldname.split('__'))


def _get_instanceattr(instance, fieldname):
    fieldvalue = getattr(instance, fieldname)
    field = instance.__class__._meta.get_field_by_name(fieldname)[0]
    if isinstance(field, ForeignKey):
        if fieldvalue == None: # If the foreign key is null
            return None
        else:
            return fieldvalue.pk
    else:
        return fieldvalue

def _recurse_getmodelattr(instance, path):
    pathseg = path.pop(0)
    try:
        cur = getattr(instance, pathseg)
    except AttributeError:
        # NOTE: Dirty hack to support list results. This is to return
        # multiple candidates
        if repr(type(instance)) == "<class 'django.db.models.fields.related.RelatedManager'>":
            if path:
                # NOTE: Dirty hack to support list results. This is to return
                # multiple candidates__student__username
                return [_recurse_getmodelattr(obj, [pathseg] + path) for obj in instance.all()]
            else:
                # NOTE: Dirty hack to support list results. This is to return
                # multiple candidates__identifier
                return [_get_instanceattr(obj, pathseg) for obj in instance.all()]
        # NOTE: Dirty hack to support list results. This is to return
        # multiple examiners
        if repr(type(instance)) == "<class 'django.db.models.fields.related.ManyRelatedManager'>":
            return [_get_instanceattr(obj, pathseg) for obj in instance.all()]

        return None  # If the foreign relationship we are following is null, we return None
    if not path:
        return _get_instanceattr(instance, pathseg)
    else:
        return _recurse_getmodelattr(cur, path)


def modelinstance_to_dict(instance, fieldnames):
    """ Convert the given django model instance into a dict where
    each fieldname in ``fieldnames`` is a key.

    :param instance: A django model instance.
    :param fieldname: List of fieldname names. Can also be foreign keys, such as
        ``parentnode__parentnode__short_name``, or :class:`devilry.simplified.OneToMany`.
    """
    dct = {}
    for fieldname in fieldnames:
        if isinstance(fieldname, OneToMany):
            onetomany = fieldname
            dct[onetomany.related_field] = onetomany.as_list(instance)
        elif "__" in fieldname:
            path = fieldname.split('__')
            dct[fieldname] = _recurse_getmodelattr(instance, path)
        else:
            try:
                dct[fieldname] = _get_instanceattr(instance, fieldname)
            except FieldDoesNotExist:
                dct[fieldname] = getattr(instance, fieldname) # This is an annotated field (or something is seriously wrong)
            except AttributeError:
                # Annotated field
                continue # If we fail here, it will not work to use this for both read (which does not support annotated fields) and search
    return dct


def fix_expected_data_missing_database_fields(test_groups, expected_res, search_res=None):
    """ For internal test use ONLY. """
    for i in xrange(len(test_groups)):
        group = test_groups[i]
        deadline = group.get_active_deadline()
        expected_res[i]['latest_deadline_id'] = deadline.id
        expected_res[i]['latest_deadline_deadline'] = deadline.deadline
        expected_res[i]['number_of_deliveries'] = deadline.deliveries.all().count()
        if deadline.deliveries.all().count() > 0:
            max_id = deadline.deliveries.aggregate(Max("id"))
            expected_res[i]['latest_delivery_id'] = deadline.deliveries.filter(id=max_id['id__max'])[0].id
            #expected_res[i]['latest_delivery_id'] = deadline.deliveries.all()[0].id
        else:
            expected_res[i]['latest_delivery_id'] = None
