# Updating from v2 to v3 using branches

This is for developers, and MOST NOT BE USED TO UPDATE A 
PRODUCTION SYSTEM!

**Remember that Devilry uses python 2**. So use a Python 2.7 version for everything in this guide.


## Overview

### What we want to en up with
We want to end up with the following versions:

``2.0.x``:
Should be able to start from any 2.0.x version.

``3.0.0``:
Must update to this first to reset migrations before the database was
changed.

``3.0.1``:
Must update to this after ``3.0.0`` to get the final migration reset.
Should be able to update to any never ``3.x`` release after the database
has been migrated to this version.

``3.1.0``:
First usable 3.x release.


### We develop the update workflow using the following branches

``devilry-2.0.x``:
The latest 2.0.x version. We start from this branch.

``devilry-3.0.0-before-new-usermodel``:
The first 3.0.x branch that 2.0.x must be updated to.



## How to update using branches

### Get a devilry 2.x database

#### Setup a 2.0.x virtualenv

```
$ git checkout --track origin/devilry-2.0.x
$ mkvirtualenv v2-0-devilry
$ pip install --upgrade pip       # because the install crashes for old PIP versions
$ pip install -r requirements/development_full.txt
```

#### Make a 2.0.x database
```
For quick sanity checks/testing, use:
$ fab demodb:djangoenv=postgres_develop

... but for a full test with more complex data, you should use:
$ fab autodb:djangoenv=postgres_develop
```

Make sure it is working:
```
$ DJANGOENV=postgres_develop python manage.py runserver
```
(login with user=granda and password=test)


### Migrate the database to 3.0.0

#### Setup a 3.0.0 virtualenv
```
$ deactivate     # if you have the v2-0-devilry virtualenv active
$ git checkout --track origin/devilry-3.0.0-before-new-usermodel
$ mkvirtualenv v3-0-0-devilry
$ pip install --upgrade pip       # because the install crashes for old PIP versions
$ pip install -r requirements/development.txt
```


#### Migrate the database
All on one line:
```
$ python manage.py migrate --fake-initial contenttypes && python manage.py migrate --fake core && python manage.py migrate --fake devilry_gradingsystem 0001 && python manage.py migrate --fake-initial
```
