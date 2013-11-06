.. _devenv:

===========================================
``devenv/`` --- The development environment
===========================================


##########################################################################
Setup a local development environment
##########################################################################

Check out from GIT
=================================================================

If you plan to develop devilry, you should fork the devilry-django repo,
changes to your own repo and request inclusion to the master repo using
github pull requests. If you are just trying out Devilry, use::

    $ git clone https://github.com/devilry/devilry-django.git

The ``master`` branch, which git checks out by default, is usually the
latest semi-stable development version. The latest stable version is in
the ``latest-stable`` branch.


Install dependencies/requirements
=================================================================

.. note::
    Devilry should work perfectly well with only Python 2.7 or later Python2 versions.
    Devilry does not work with Python3 yet, but we will support it when Django and all
    our dependencies gets good Python3 support.

    Other dependencies than are not really required, but we recommend that you:

    - use Virtualenv to avoid installing anything globally, and to get a clean environment
    - use Fabric because we have a lot of useful scripts written for Fabric that will ease
      setting up your development environment and building various components of Devilry.
      See :ref:`aboutfabric`.

    Note that all instructions below assume you have and want to install Fabric and Virtualenv.


Mac OSX
------------------------------------------------

1. Install **XCode** (from app store).
2. Install command line tools for XCode (includes Git and Python):
    - Open XCode
    - Choose ``XCode->Preferences`` (or ``CMD,``).
    - Select the *Downloads*-tab.
    - Install the *Command line tools* component.
3. Install other dependencies/requirements::

    $ sudo easy_install fabric virtualenv


Ubuntu Linux
------------------------------------------------
::

    $ sudo apt-get install fabric build-essential python-dev python-virtualenv libncurses5-dev


Arch Linux
------------------------------------------------
(may be incomplete)

Install required system packages::

    $ packman -S python2 fabric python2-virtualenv





Setup the development virtualenv
=================================================================
::

    $ cd devenv/
    $ fab bootstrap

.. note::

   ``fab bootstrap`` might not work even if the right tools in `Ubuntu
   Linux`_ are installed. It is possible that the creation of
   the virtual environment will fail because it either installs *setuptools* or
   *distribute* into the environment. To use *distribute* you must
   explicitly add the *\-\-distribute* flag to the *virtualenv* command or you
   must set the VIRTUALENV_DISTRIBUTE environment variable.
   
.. note::

   If you get any trouble with ncurses linking during installation, make sure you have the development version
   of the ncurses library installed.

.. note::

    If you get ``"Error: Couldn't install: readline".``, you may try to debug
    it, or you could simply remove ``readline`` and ``ipython`` from
    ``development-base.cfg``.


.. note::

    On some systems (E.g.: ArchLinux) the `virtualenv2` command has to be
    called instead of ``virtualenv``. To trick fabric into calling virtualenv2,
    you can use::

        $ ln -s `which virtualenv2` virtualenv
        $ PATH="$PATH:." fab bootstrap


Next steps
=================================================================
You now have a complete development enviroment in ``devenv/``. You
can use Devilry just like any other Django application, except that
you have to use ``bin/django_dev.py`` instead of ``./manage.py``.

You should:

- :ref:`createdevenvdb`.
- :ref:`devrunserver`.

And you may want to read :ref:`managepy`.




.. _createdevenvdb:

#######################################################################
Create a database
#######################################################################
We have several alternatives for setting up a demo database. They all
use Fabric tasks. See :ref:`aboutfabric`


::

    $ cd devenv/
    $ bin/fab autodb

Note: Creating the testdata takes a lot of time, but you can start using
the server as soon as the users have been created (one of the first
things the script does).

Alternative step 4.1 - Setup an empty databse
================================================

::

    $ cd devenv/
    $ bin/fab syncdb

Alternative step 4.1 - From database dump
================================================

Creating the demo database takes a lot of time (~12mins on a 2012
macbook air with SSD disk). You may ask a developer to send you a
*db\_and\_deliveries\_stash*, and use it instead of ``autodb``::

    $ cd devenv/
    $ cp -r /path/to/db_and_deliveries_stash ./
    $ bin/fab unstash_db_and_deliveries

How to create a DB-stash
------------------------

Use this if you want to create a ``db_and_deliveries_stash/`` to send to
other developers (which can follow the steps in the previous section)::

    $ cd devenv/
    $ bin/fab autodb           (optional - resets your database)
    $ bin/fab stash_db_and_deliveries

Alternative step 4 - Manually (without fabric)
=================================================================

Create a clean development environment with an empty database:

::

    $ cd devenv/
    $ virtualenv --no-site-packages .
    $ bin/easy_install zc.buildout
    $ bin/buildout
    $ bin/django_dev.py syncdb

Autocreate the demo-db:

::

    $ bin/django_dev.py dev_autodb -v2



.. _devrunserver:

#################################################################
Run the Django development server
#################################################################
As long as you understand that you have to use ``bin/django_dev.py`` (see :ref:`managepy`),
the Django development server is just the Django development server::

    $ bin/django_dev.py runserver

Go to http://localhost:8000/ and log in as a superuser using::

    user: grandma
    password: test

Or as a user which is student, examiner and admin using::

    user: thor
    password: test

**Note:** All users have ``password==test``, and you can see all users
in the superadmin interface. See `the demo page on the
wiki <https://github.com/devilry/devilry-django/wiki/demo>`_ for more
info about the demo database, including recommended test users for each
role.


.. _aboutfabric:

###################################################
Fabric
###################################################

We use `Fabric <http://fabfile.org>`_ to simplify common tasks. Fabric
simply runs the requested ``@task`` decorated functions in
``fabfile.py``.

``fabfile.py`` is very straigt forward to read if you wonder what the
tasks actually do. The ``fabric.api.local(...)`` function runs an
executable on the local machine.


.. _managepy:

#######################################################################
Where is manage.py?
#######################################################################

We use a buildout-generated wrapper for manage.py that sets up the correct
PYTHONPATH and settingsmodule::

    $ bin/django_dev.py <action>

``django_dev.py`` is a wrapper that we have configured in ``development-base.cfg``.
