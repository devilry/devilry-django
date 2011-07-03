def restful_api(cls):
    """
    :class:`RestView` and the :func:`restful_api`-decorator is use in
    conjunction to create a RESTful web service with a CRUD+S interface.
    """
    try:
        meta = cls.Meta
    except AttributeError:
        class Meta:
            """ Fake meta class """
        meta = Meta
    cls._meta = meta
    if not hasattr(cls._meta, 'urlprefix'):
        cls._meta.urlprefix = cls.__name__.lower()
    if not hasattr(cls._meta, 'urlmap'):
        cls._meta.urlmap = {}
    urlname = '%s-%s' % (cls.__module__, cls.__name__)
    cls._meta.urlname = urlname.replace('.', '-')
    return cls


