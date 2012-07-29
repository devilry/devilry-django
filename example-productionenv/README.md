# Example production configs

You should copy this directory into another directory in the same parent
directory (the repo root) when setting up your own production instance:

    $ cd /path/to/root/of/devilry-django
    $ cp -r example-productionenv my-productionenv

The rest of this guide assumes your CWD is the newly copied directory (I.E.:
``my-productionenv/``).


# Setup Devilry

## Install virtualenv and Fabric
If you do not have the ``virtualenv`` or ``fab`` commands, you can install them
from your package manager, or from pypi with:

    $ sudo easy_install virtualenv fabric


## Get dependencies and compile static files
Run:

    $ fab refresh


## Create a superuser
Run:

    $ bin/django_production.py createsuperuser


## Run Gunicorn (the wsgi application server)
Run:

    $ bin/django_production.py run_gunicorn -w 4 127.0.0.1:9000

``-w`` configures the number for worker-processes. Add ``--daemon`` and
``--pid=/path/to/pidfile`` to daemonize Gunicorn. Until you have tested the
setup with a webserver, we recommend that you keep gunicorn in the foreground.



# Webserver specific instructions

## Setup nginx
Edit the config-file in ``server-conf/nginx.conf`` (see notes below).

### Change the root directory (required)
You need to change the root (in the ``location /static`` section) to the
directory where you copied ``example-productionenv/``.

### Change configured paths (optional but recommended)
You will probably want to change all of the ``/tmp`` paths to somewhere more
persistent. The correct location of pid-files and log-files with OS and
distribution, so we leave this up to you.

### Change the port (optional)
The listen port defaults to 3000, which is great when testing your setup.
However you will probably want to change it to ``80``.


### Test the setup

(Make sure Gunicorn is running)

Run nginx in the foreground using:

    $ nginx -c /path/to/this-dir/server-conf/nginx.conf -g "daemon off;"

Note: that nginx requires an absolute path to the config-file (``~`` is OK).

Navigate to your nginx-server in a browser. If you have not changed the port, this will be: http://localhost:3000.


### Run nginx as a daemon - and init-script hints
If you want to run Nginx as a daemon, simply omit ``-g "daemon off;"`` from the
command in the previous section. For init-scripts, you can configure a PID-file
in ``nginx.conf``.



## Apache

TODO


# Setup logging

TODO - logdir and logrotate


# Updating Devilry

Run:

    $ fab update_devilry

to pull the latest version of Devilry from the git repository. This runs ``git
pull``, followed by creating a virtualenv, downloading all dependencies and
re-creating static files required by Devilry.



# Why Fabric (fab)?

We use [Fabric](http://fabfile.org) to simplify common tasks. Fabric simply
runs the requested ``@task`` decorated functions in ``fabfile.py``.

``fabfile.py`` is very straigt forward to read if you wonder what the tasks
actually do. The ``fabric.api.local(...)`` function runs an executable on the
local machine.
