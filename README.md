See http://devilry.org for documentation. The rest of this readme is intended for developers.


# Setup a local development environment with testdata

(Instructions assume you have ahecked out the sources from git, and that you are in a terminal at the root of the repo).


## 1 - Run buildout (get all dependencies)

    $ cd devenv/
    $ python ../bootstrap.py
    $ bin/buildout


## 2 - Create a demo database

    $ bin/fab setup_demo


## Alternative step 2 - Setup an empty databse

    $ bin/fab reset


## Why bin/fab??

``bin/fab`` is the [Fabric](http://fabfile.org) executable. Fabric simply runs the requested ``@task`` decorated functions in ``fabfile.py``.

``fabfile.py`` is very straigt forward to read if you wonder what the tasks actually do. The ``fabric.api.local(...)`` function runs an executable on the local machine.
