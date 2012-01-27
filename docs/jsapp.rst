


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
