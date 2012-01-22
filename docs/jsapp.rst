


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



Viewport
#########

Apps should inherit from ````
