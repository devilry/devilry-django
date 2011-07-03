def restful_api(cls):
    """
    :class:`RestView` and the :func:`restful_api`-decorator is use in
    conjunction to create a RESTful web service with a CRUD+S interface.

    Adds the ``_meta`` attribute to the decorated class. The ``_meta``
    attribute has the following attributes:

        urlprefix
            The url prefix used for the url created by
            :meth:`RestView.create_rest_url`.  This is always:
            ``cls.__name__.lower()``
        urlname
            The name of the url created by
            :meth:`RestView.create_rest_url`. This is the full python
            dot-path to ``cls`` with ``.`` replaced by ``-``.
    """
    class Meta:
        """ Fake meta class """
    meta = Meta
    cls._meta = meta
    cls._meta.urlprefix = cls.__name__.lower()
    #if not hasattr(cls._meta, 'urlmap'):
        #cls._meta.urlmap = {}
    urlname = '%s-%s' % (cls.__module__, cls.__name__)
    cls._meta.urlname = urlname.replace('.', '-')
    return cls


