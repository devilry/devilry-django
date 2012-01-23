


Disk Layout
###########

The layout is basically the one reccommended by ExtJS, however since we route apps through Django, there are minor differences::

    appname/
        models.py
        urls.py
        ...
        static/
            appname/
                app.js
                app/
                    controller/
                    model/
                    store/
                    view/


models.py
---------
TODO


urls.py
-------
TODO


static/appname/
---------------
Refer to ExtJS docs.





Creating a new app
###################

Create disk layout
------------------


Need CSS?
---------

We reccommend Compass_::

    $ cd <appname>/static/<appname>/
    $ compass create resources
    $ rm resources/sass/ie.scss resources/sass/screen.scss resources/sass/print.scss

Add your styles to ``resources/sass/<appname>.scss`` and compile using::

    $ compass compile

You may also autocompile on file changes using::

    $ compass watch


.. _Compass: http://compass-style.org/
