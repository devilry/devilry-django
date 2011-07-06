from django.db.models.fields.related import RelatedObject, ManyToManyField


def _clspath(cls):
    return "{0}.{1}".format(cls.__module__, cls.__name__)


def _fieldnames_to_docs(modelcls, fieldnames):
    docs = []
    for fieldname in fieldnames:
        field = modelcls._meta.get_field_by_name(fieldname)[0]
        if isinstance(field, ManyToManyField):
            pass
        elif isinstance(field, RelatedObject):
            pass
        else:
            if hasattr(field, 'help_text'):
                help_text = field.help_text
            else:
                help_text = ''
            fieldtype = "{0}.{1}".format(type(field).__module__, type(field).__name__)
            #print field.name, help_text, fieldtype
            docs.append(':param %s: %s' % (field.name, help_text))
            docs.append(':type %s: %s' % (field.name, fieldtype))
    return docs

def create_read_doc(cls, fieldnames=None):
    meta = cls._meta
    clspath = '%s.%s' % (cls.__module__, cls.__name__)
    fieldnames = fieldnames or meta.model._meta.get_all_field_names()
    #docs = _fieldnames_to_docs(meta.model, meta.resultfields.as_list())

    #throws = [
            #':throws devilry.apps.core.models.Node.DoesNotExist:',
            #'   If the node with ``idorkw`` does not exists, or if',
            #'   parentnode is not None, and no node with ``id==parentnode_id``',
            #'   exists.']

    #get_doc = '\n'.join(
            #['Get a %(modelname)s object.'] + ['\n\n'] + resultfields)
    #modelname = meta.model.__name__
    #return get_doc % vars()


def create_cls_docs(cls):
    model = cls._meta.model
    cls.__doc__ = """ Simplified wrapper for {modelcls}.

Meta attributes:
{resultfields}
""".format(modelcls = _clspath(model),
           resultfields=cls._meta.resultfields._asdocstring())


if __name__ == "__main__":
    from devilry.apps.administrator.simplified import SimplifiedPeriod

    #create_read_doc(SimplifiedPeriod)
    print SimplifiedPeriod.search.__doc__
