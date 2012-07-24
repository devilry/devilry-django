See http://devilry.org for documentation. The rest of this readme is intended for developers.


# Setup a local development environment with testdata


## 1 - Check out from GIT

Check out the devilry repo from git. If you plan to develop devilry, you should
fork the devilry-django repo, changes to your own repo and request inclusion to
the master repo using github pull requests. If you are just trying out devilry, use:

    $ git checkout https://github.com/devilry/devilry-django.git

The ``master``, which git checks out by default, is usually the latest
semi-stable development version. The latest stable version is in the
``latest-stable`` branch.


## 2 - Run buildout (get all dependencies)

    $ cd devenv/
    $ python ../bootstrap.py
    $ bin/buildout


## 3 - Create a demo database

    $ bin/fab setup_demo


### Alternative step 3 - Setup an empty databse

    $ bin/fab reset


## Why bin/fab??

``bin/fab`` is the [Fabric](http://fabfile.org) executable. Fabric simply runs the requested ``@task`` decorated functions in ``fabfile.py``.

``fabfile.py`` is very straigt forward to read if you wonder what the tasks actually do. The ``fabric.api.local(...)`` function runs an executable on the local machine.
