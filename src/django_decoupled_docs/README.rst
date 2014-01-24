#####################
django_decoupled_docs
#####################

The goal of this app is to make it easy to intergrate translatable tutorials
and longer documentation articles for a webapp **without forcing a specific documentation system**. 

The idea
========
Each documenation page provides a unique ID (just like a named URL in
Django). This ID points to a configuration class that determines what
happens when the user requests the ID. The configuration class can
send the user wherever you want. I.E:

- to an online Sphinx documentation on read-the-docs.org.
- to a local view defined by your webapp.
- to a translated version of the help page in the language preferrered by the requesting user.

Furthermore, you can override this mapping in ``settings.py``, so if a
local install of your app provides localized versions of certain help pages,
they can easily replace those pages with their own pages. These overrides use
exactly the same system as you use to provide the defaults for your own apps.


How it works - a use case
=========================
Lets say we have an app with a Markdown editor field. This field needs a
tutorial, which we want to provide as external documentation. Our webapp
has a lot of different users, and the amount of help required by the 
documentation varies from install to install. So the best we can hope
for is to provide a good guide that covers most of the users, but we
want to allow the local system administrators to provide a tutorial better
optimized for their users if needed.

First - write the documentation
-------------------------------
First, we need to decide how to provide the default documentation. We support
English and Norwegian out of the box, so we want to provide the documentation
in both of those languages. We think that Sphinx_ and we want to host this
on http://read-the-docs.org using their
`localization features <http://read-the-docs.readthedocs.org/en/latest/localization.html>`_.

So we add the English version of the tutorial for our Markdown editor to our
master documentation repository and the Norwegian version of the tutorial to
the Norwegian fork of the documentation repository.


Next - link to the docs from our webapp
---------------------------------------
Now we have the documentation on read-the-docs.org, but how do we link
to it?

.. note:: 

    that we could just as easily have provided the documentation
    as internal Django views, and we would still need a way to link to them
    and still support localization and the ability for local system administrators
    to provide their own optimized guides.

To link to the documentation, we first have to register it with an ID (kind of like registering an URL for a view)::

    from django_decoupled_docs.registry import decoupled_docs_registry
    from django_decoupled_docs.registry import DocProxy

    decoupled_docs_registry.add('my-markdown-editor/tutorial', DocProxy(
        # The default english docs
        default = 'http://read-the-docs.org/my-markdown-editor/en/latest/tutorial.html',

        # The Norwegian Bokmaal translation
        nb = 'http://read-the-docs.org/my-markdown-editor/nb/latest/tutorial.html',
    ))

The ``DocProxy`` class is designed to be extended, so you could easily create a
subclass that makes it less verbose to specify the URL to your docs on
read-the-docs.

Now, you can use the ``decoupled_docs_registry`` to get the URL from your specified ID::

    from django_decoupled_docs.registry import decoupled_docs_registry

    def myview(request):
        url = decoupled_docs_registry.get(request, 'my-markdown-editor/tutorial')
        ...

Or you can use the provided template tag::

    {% load django_decoupled_docs_tags %}

    <a href='{% decoupled_docs_url "my-markdown-editor/tutorial" %}'


Override the Norwegian guide
----------------------------
The users of one of our system installs reads Norwegian, and they are technical
people that needs a lot of help on how to write Math and programming code using
the Markdown editor. So the local system administrators decide to create their own
guide. All they need to do is to override the norwegian translation in their ``settings.py``::

    
    from django_decoupled_docs.registry import decoupled_docs_registry
    from django_decoupled_docs.registry import DocProxy

    decoupled_docs_registry.override('my-markdown-editor/tutorial', DocProxy(
        nb = 'http://intranet.example.com/superapp/markdown-editor-tutorial.html',
    ))

This replaces the default Norwegian guide with the local guide. If they have
any English speaking users, those users will still get the default English
guide.


Handling links to versioned documentation
=========================================
To provide links to versioned documentation, you just have to provide your own ``DocProxy`` subclass. Example::

    from myapp import version

    class VersionedDocProxy(DocProxy):
        def parse_url(self, request, url):
            return url.format(version=version)    


And then you can use ``VersionedDocProxy`` as follows::

    decoupled_docs_registry.add('my-markdown-editor/tutorial', DocProxy(
        # The default english docs
        en = 'http://read-the-docs.org/my-markdown-editor/en/{version}/tutorial.html',

        # The Norwegian Bokmaal translation
        nb = 'http://read-the-docs.org/my-markdown-editor/nb/{version}/tutorial.html',
    ))


Avoid having to register static URLs
====================================
You probably do not want to type something like::

    http://read-the-docs.org/my-markdown-editor/<ACTUAL PATH TO ARTICLE>
    
for each help article. To avoid this, you should create ``DocProxy`` subclasses for each
of your documentation sources. For a read-the-docs DocProxy, you could do something like this::

    from django_decoupled_docs.registry import DocProxy

    class ReadTheDocsDocProxy(DocProxy):
        #: The name of the project (the first path of the URL)
        projectname = None
    
        def add_for_language(self, languagecode, path):
            url = 'http://read-the-docs.org/{projectname}/{languagecode}/latest/{path}'.format(
                projectname=self.projectname, languagecode=languagecode, path=path)
            super(ReadTheDocsDocProxy, self).add_for_language(languagecode, url)


    class MyProjectReadTheDocsDocProxy(ReadTheDocsDocProxy):
        projectname = 'my-project'


And then use ``MyProjectReadTheDocsDocProxy`` and other similar specialized
``DocProxy``-implementations instead of ``DocProxy``::

    from django_decoupled_docs.registry import decoupled_docs_registry
    from django_decoupled_docs.registry import DocProxy

    decoupled_docs_registry.add('my-markdown-editor/tutorial', MyProjectReadTheDocsDocProxy(
        # The default english docs
        default = 'tutorial.html',
        nb = 'tutorial.html'
    ))

.. note::

    This could, of course, be simplified further if we just override ``__init__``
    to avoid having to re-type ``tutorial.html`` for each language.




Install
=======
Add ``django_decoupled_docs`` to ``INSTALLED_APPS``.


.. _Sphinx: http://sphinx-doc.org/
