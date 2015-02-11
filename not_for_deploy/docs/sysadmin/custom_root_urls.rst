****************
Custom root urls
****************

Why?
====
Devilry comes with a default URL-route config for production. You may want to
add to this if you need to install other Django apps on the Devilry server.


Create an URL config file
=========================

First, create a url file in the same directory as your
``devilry_prod_settings.py``. We will call the file ``devilry_prod_urls.py``
for this example, but you can name it anything you like as long as it is a
valid python module name (english letters, no spaces, end with ``.py``).

The file should look like this:

.. literalinclude:: examples/devilry_prod_urls.py
    :language: python
    :linenos:

Add your custom URLs as shown in the example on line 13.


Make ``devilry_prod_settings.py`` use your custom urls
======================================================
Update your ``devilry_prod_settings.py`` with::

    ROOT_URLCONF = 'devilry_prod_urls'



Use a custom Frontpage?
=======================
You can easily create serve your own Django app as the frontpage instead of the
default Devilry frontpage. Django uses the first matched url-config, so we can
override the match for ``/`` and replace it with our own view.

Here is an example that sets up urls for the Trix-project on ``/trix/``, and
uses a Django redirect view to redirect the frontpage to that URL. We also
setup the default Devilry frontpage at ``/devilry/``:

.. literalinclude:: examples/devilry_prod_urls_custom_frontpage.py
    :language: python
    :linenos:

.. note::

    Tou do not have to redirect from the frontpage, you can just as easily use
    a Django view that renders your view at ``/`` without a redirect.
