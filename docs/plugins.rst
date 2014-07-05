.. _plugins:


=====================
How to write a plugin
=====================

A plugin is basically just a normal Django application. The only thing making
it a *pugin* is that it integrates itself into the Devilry system in some way.


Setting up your testsite
========================

In this *howto* we assume you have created a django site, ``mysite/``, and 
and that your plugin is a application in this site called ``myplugin``. It should
look something like this::

    mysite/
        settings.py
        manage.py
        urls.py
        myplugin/
            models.py
            urls.py



Autoload plugins
================

There are several ways a plugin can integrate itself, but they all need some
place to do the integration. Just like ``admin.py`` can be used to integrate
your application with the Django admin interface, devilry provides a place
where you can put code that you want to autoload.

First initialize the plugin system by adding::

    from devilry.apps.core import pluginloader
    pluginloader.autodiscover()

to your ``mysite/urls.py``, making it look something like this::

    from django.conf.urls import *

    # Uncomment the next two lines to enable the admin:
    #from django.contrib import admin
    #admin.autodiscover()

    from devilry.apps.core import pluginloader
    pluginloader.autodiscover()

    urlpatterns = patterns('',
        # Example:
        # (r'^mysite/', include('mysite.foo.urls')),

        # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
        # to INSTALLED_APPS to enable admin documentation:
        # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

        # Uncomment the next line to enable the admin:
        # (r'^admin/', include(admin.site.urls)),
    )

``pluginloader.autodiscover()`` will autoload any module named
``devilry_plugin`` in any application in ``INSTALLED_APPS``.


Your first plugin
=================

Create a file named ``mysite/myplugin/devilry_plugin.py``, and put the
following code into the file::

    print
    print "Hello plugin world!"
    print

Start the development server with ``python manage.py runserver``, go to
http://localhost:8000/ and you should see the message you printed in the
terminal/shell running the server.


Plugin errors
=============

``pluginloader.autodiscover()`` will fail if you have any errors in your
``devilry_plugin``-module. It will not auto-reload failed modules before you
restart the server.

