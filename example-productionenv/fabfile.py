"""
Fabric tasks that simplifies updating Devilry, and setting up a demo instance.
"""

from fabric.api import local, task



@task
def virtualenv():
    """
    Setup a virtualenv in virtualenv/, run bootstrap in the virtualenv, and run bootstrap.
    """
    local('rm -rf virtualenv')
    local('virtualenv virtualenv')
    local('virtualenv/bin/python ../bootstrap.py')
    local('bin/buildout')

@task
def syncdb():
    local('bin/django_production.py syncdb -v0 --noinput')


@task
def refreshstatic():
    """
    Refresh static files
    """
    local('bin/django_production.py dev_autogen_extjsmodels')
    local('bin/django_production.py devilry_extjs_jsmerge')
    local('bin/django_production.py collectstatic --noinput')


@task
def refresh():
    """
    (re)-create the virtualenv, run buildout, and refresh all static files.
    """
    virtualenv()
    refreshstatic()
    syncdb()


@task
def update_devilry():
    """
    Update devilry (runs ``git pull``), and run the ``refresh`` task.
    """
    local('git pull')
    refresh()



#
# Tasks for demo setup:
#

@task
def demodb():
    syncdb()
    local('bin/django_production.py dev_autodb -v2')

@task
def reset_demodb():
    from os.path import exists
    from os import remove
    if exists('db.sqlite3'):
        remove('db.sqlite3')
    demodb()
