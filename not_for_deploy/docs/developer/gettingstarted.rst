#####################################
Setup a local development environment
#####################################


******************
Check out from GIT
******************

If you plan to develop devilry, you should fork the devilry-django repo,
changes to your own repo and request inclusion to the master repo using
github pull requests. If you are just trying out Devilry, use::

    $ git clone https://github.com/devilry/devilry-django.git

The ``master`` branch, which git checks out by default, is usually the
latest semi-stable development version. The latest stable version is in
the ``latest-stable`` branch.


*********************************
Install dependencies/requirements
*********************************

.. note::
    Devilry should work perfectly well with only Python 2.7 or later Python2 versions.
    Devilry does not work with Python3 yet, but we will support it when Django and all
    our dependencies gets good Python3 support.

    We require postgresql to develop Devilry. You only have to have it installed,
    Devilry comes with Django management commands that help you create and work
    with an isolated development database.

    Other dependencies than are not really required, but we recommend that you:

    - use Virtualenv to avoid installing anything globally, and to get a clean environment
    - use Fabric because we have a lot of useful scripts written for Fabric that will ease
      setting up your development environment and building various components of Devilry.
      See :ref:`aboutfabric`.

    Note that all instructions below assume you have and want to install Fabric and Virtualenv.


Mac OSX
=======

1. Install **XCode** (from app store).
2. Install command line tools for XCode (includes Git and Python)::

    $ xcode-select --install

3. Install other dependencies/requirements::

    $ sudo easy_install virtualenv

4. Install postgresql. We recommend you do this via `Homebrew <http://brew.sh/>`_::

    $ brew install postgresql


Ubuntu Linux
============
::

    $ sudo apt-get install build-essential python-dev python-virtualenv libncurses5-dev virtualenvwrapper libxslt1-dev libxml2 libxml2-dev zlib1g-dev



Setup the development virtualenv
================================
::

    $ mkvirtualenv devilry-django
    $ pip install -r requirements/development.txt



.. _createdevenvdb:

*****************
Create a database
*****************
We have several alternatives for setting up a demo database. They all
use Fabric tasks. See :ref:`aboutfabric`.

First, make sure you are in the ``devilry-django`` virtualenv::

    $ workon devilry-django

You can create a fairly full featured demo database with::

    $ fab autodb

... or you can create a much more minimalistic demo database with::

    $ fab demodb

... or you can create an empty database with::

    $ fab reset_db

Note: Creating the testdata with ``autodb`` takes a lot of time, but you can start using
the server as soon as the users have been created (one of the first
things the script does).



.. _devrunserver:

*********************************
Run the Django development server
*********************************
First, make sure you are in the ``devilry-django`` virtualenv::

    $ workon devilry-django

Start the Django development server with::

    $ python manage.py runserver

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

******
Fabric
******

We use `Fabric <http://fabfile.org>`_ to simplify common tasks. Fabric
simply runs the requested ``@task`` decorated functions in
``fabfile.py``.

``fabfile.py`` is very straigt forward to read if you wonder what the
tasks actually do. The ``fabric.api.local(...)`` function runs an
executable on the local machine.

