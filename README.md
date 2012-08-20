See http://devilry.org for documentation. The rest of this readme is intended for developers.


# Setup a local development environment with testdata


## 1 - Check out from GIT

If you plan to develop devilry, you should fork the devilry-django repo,
changes to your own repo and request inclusion to the master repo using github
pull requests. If you are just trying out devilry, use:

    $ git checkout https://github.com/devilry/devilry-django.git

The ``master`` branch, which git checks out by default, is usually the latest
semi-stable development version. The latest stable version is in the
``latest-stable`` branch.


## 2 - Install Fabric

    $ sudo easy_install fabric


## 3 - Run buildout (get all dependencies)

    $ cd devenv/
    $ python ../bootstrap.py
    $ bin/buildout


## 4 - Create a demo database

    $ fab setup_demo

Note: Creating the testdata takes a lot of time, but you can start using the
server as soon as the users have been created (one of the first things the
script does).


### Alternative step 4 - Setup an empty databse
If you just want to setup an empty database, run ``fab autogen_extjsmodels syncdb``.


### Alternative step 4 - From database dump
Creating the demo database takes a lot of time (12mins on a macbook air with SSD disk). You may ask a developer to send you a dump, and use it instead of ``setup_demo``:

    $ fab reset
    $ fab restore_db:/path/to/dbdump.sql


## 5 - Run the development server

    $ bin/django_dev.py runserver

Go to http://localhost:8000/ and log in as a superuser using:

    user: grandma
    password: test

Or as a user which is student, examiner and admin using:

    user: thor
    password: test

**Note:** All users have ``password==test``, and you can see all users in
the superadmin interface. See [the demo page on the wiki](https://github.com/devilry/devilry-django/wiki/demo)
for more info about the demo database, including recommended test users for each role.


# Why Fabric?

We use [Fabric](http://fabfile.org) to simplify common tasks. Fabric simply runs the requested ``@task`` decorated functions in ``fabfile.py``.

``fabfile.py`` is very straigt forward to read if you wonder what the tasks actually do. The ``fabric.api.local(...)`` function runs an executable on the local machine.
