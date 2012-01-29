


Disk Layout
###########

The layout is basically the one reccommended by ExtJS, however since we route apps through Django, there are minor differences::

    appname/
        models.py
        urls.py
        ...
        static/
            appname/
                app/
                    Application.js
                    TestApplication.js
                    controller/
                    model/
                    store/
                    view/




Creating a new app
###################

Create disk layout
==================

models.py
---------
TODO


urls.py
-------

Typically looks something like this::

    from django.conf.urls.defaults import patterns
    from devilry.apps.jsapp.views import create_urls
    urlpatterns = patterns('devilry.apps.myapp',
                           *create_urls('myapp',
                                        with_css=True,
                                        libs=['jsapp', 'themebase']))

See :func:`devilry.apps.jsapp.views.create_urls`. Notice that we specify two
libs. You will usually need these two. ``jsapp`` provides the architecture
for the app framework, and ``themebase`` provides the default theme, re-usable
layouts and common widgets.


static/appname/
---------------
Refer to ExtJS docs.


static/appname/app/Application.js
---------------------------------
A subclass of ``Ext.app.Application``.

static/appname/app/TestApplication.js
---------------------------------
A subclass of ``<appname>.Application``.



Need CSS?
=========

Add your CSS to
``<appname>/static/<appname>/resources/stylesheets/<appname>.css`` and update
``urls.py`` with the ``with_css=True`` argument to
:func:`devilry.apps.jsapp.views.create_urls`.


CSS with compass
================

We reccommend Compass_::

    $ cd <appname>/static/<appname>/
    $ compass create resources
    $ cd resources
    $ rm sass/ie.scss sass/screen.scss sass/print.scss

Add your styles to ``sass/<appname>.scss`` and compile using::

    $ compass compile

You may also autocompile on file changes using::

    $ compass watch

.. _Compass: http://compass-style.org/



Routing
############

The natural structure of the data controlled by the app should be organized
in a directory-like routing scheme::

    #/
        List all items
    #/someitem
        Show "someitem"
    #/someitem/
        Show all children of "someitem"
    #/someitem/childitem
        Show "childitem"


Cross cutting and non-hierarchial routes should use the following format::

    #/@@some-action
    #/someitem/@@some-action

Prefixing with ``@@`` makes it clear to developers that these are not part of
the normal hierarchy browsing.



Libraries
#########

Libraries are just like apps, however they should put their data in extjs
classes in ``lib/`` instead of ``app``.



Code conventions
################

Require/include order
---------------------

The order of statements in ``requires: [...]`` should be:

- ExtJs includes (anything in the Ext namespace).
- Non-app includes grouped by namespace.
- App includes.

Example::

    requires: [
        'Ext.form.field.ComboBox',
        'Ext.form.field.Text',
        'Ext.form.field.Hidden',
        'Ext.toolbar.Toolbar',
        'devilry.extjshelpers.formfields.DateTimeField',
        'themebase.CreateButton',
        'themebase.AlertMessageList',
        'themebase.form.Help',
        'view.SomeView',
        'view.AnotherView'
    ]


Private methods
---------------

Private methods should be prefixed with ``_``. These methods should **never**
be used outside the class, not even in subclasses.


API
###

.. automodule:: devilry.apps.jsapp.views
