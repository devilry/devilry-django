from exceptions import PermissionDenied
from qryresultwrapper import QryResultWrapper
import create


def _require_metaattr(cls, attr):
    """ Note that this method is also used in ``devilry.restful``. """
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
        getattr(create, 'create_%s_method' % method)(cls) # Calls create.create_[CRUD+S]_method(cls)
    return cls
