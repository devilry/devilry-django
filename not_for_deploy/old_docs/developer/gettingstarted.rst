#####################################
Setup a local development environment
#####################################


******************
Check out from GIT
******************

If you plan to develop devilry, you should fork the devilry-django repo,
changes to your own repo and request inclusion to the master repo using
github pull requests.


If you are just trying out Devilry, use
=======================================
::

    $ git clone https://github.com/devilry/devilry-django.git

If you are part of the Devilry team on GitHub, use
==================================================
::

    $ git clone git@github.com:devilry/devilry-django.git


The ``master`` branch, which git checks out by default, is usually the
latest semi-stable development version.


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

    Note that all instructions below assume you have and want to install Fabric and Virtualenv.


Mac OSX
=======

1. Install **XCode** (from app store).
2. Install command line tools for XCode (includes Git and Python)::

    $ xcode-select --install

3. `Install virtualenvwrapper <http://virtualenvwrapper.readthedocs.io/en/latest/install.html>`_.
4. Install postgresql and redis. We recommend you do this via `Homebrew <http://brew.sh/>`_::

    $ brew install postgresql redis


Ubuntu Linux
============
::

    $ sudo apt-get install build-essential python-dev python-virtualenv libncurses5-dev virtualenvwrapper libxslt1-dev libxml2 libxml2-dev zlib1g-dev libpq-dev



Setup the development virtualenv
================================
Setup a **Python 2.7** virtualenv::

    $ cd devilry-django
    $ mkvirtualenv -p /usr/local/bin/python2 devilry-django
    $ pip install -r requirements/development.txt


.. note:: Your path to `python2` may be something other than `/usr/local/bin/python2`.


.. _createdevenvdb:

*****************
Create a database
*****************

First, make sure you are in the ``devilry-django`` virtualenv::

    $ workon devilry-django

You can create a fairly full featured demo database with::

    $ ievv recreate_devdb



.. _devrunserver:

*********************************
Run the Django development server
*********************************
First, make sure you are in the ``devilry-django`` virtualenv::

    $ workon devilry-django

Start the Django development server with::

    $ ievv devrun

Go to http://localhost:8000/ and log in as a superuser using::

    user: grandma@example.com
    password: test

**Note:** All users have ``password==test``, and you can see all users
in the superadmin interface.
