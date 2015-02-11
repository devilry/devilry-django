.. _required-system-packages:

========================
Required system packages
========================

Python 2.7+
-----------
If you do not have it installed globally, it is quite easy to build and install
python in a local folder just for Devilry. Take a look at the guide in our
wiki: https://github.com/devilry/devilry-django/wiki/Installing-Python-locally. Note that
the guide installs to ``$HOME``, but you can use any folder.

Python virtualenv
-----------------
This is usually named something like ``python-virtualenv`` in linux
distributions, and it is often installed by default. You could just
try something like ``virtualenv --help`` and see if it is installed.


PostgresSQL (or another database supported by Django)
-----------------------------------------------------
We recommend PostgreSQL for production. You can use any database supported by Django,
but we do not recommend MySQL because PostgreSQL is far better with an at least as open
license, especially when it comes to transaction management (which is important
when you have to migrate your database between Devilry releases).

The default base buildout config (the one you extend in your ``buildout.cfg``) has the
Python postgresql library, ``psycopg2`` configured as a dependency. See the
`psycopg2 install-from-source docs <http://packages.python.org/psycopg2/install.html#install-from-source>`_
for information about what you need to build it. NOTE: you do not have to build it
(buildout does that in the next section), but you need to install the packages required for
a source install (python development headers, libpg, C compiler, ...).

If you do not want to use PostgreSQL, you can disable it by adding the
following to the ``[buildout]``-section of your ``buildout.cfg``::

    eggs -= psycopg2
