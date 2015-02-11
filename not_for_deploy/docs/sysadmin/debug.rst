==============
Debug problems
==============

To test that everything works as expected, you can use the Django devserver in
DEBUG-mode. The devserver serves static files, so you do not need a webserver.
It does not use SSL, so be VERY careful when running it on an extrnal NIC (like
the example with ``0.0.0.0`` below).

First, enable debug-mode in your ``~/devilrydeploy/devilry_settings.py``::

    DEBUG = True

Then run the devserver::

    $ venv/bin/python manange.py runserver

and open http://localhost:8000. You can tell the testserver to allow external
connections, and to listen on another port with::

    $ venv/bin/python manange.py runserver 0.0.0.0:9000 --insecure


.. warning::

    NEVER use the devserver or ``DEBUG=True`` in production. It is insecure and
    slow.

.. note::

    Some browsers have issues with loading the Devilry javascript sources
    from the devserver. We recommend that you use a recent version of
    Chrome, Firefox or Safari if you have problems.
