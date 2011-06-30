from django.db.models.fields.related import RelatedObject, ManyToManyField


def create_read_doc(cls, fieldnames=None):
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
