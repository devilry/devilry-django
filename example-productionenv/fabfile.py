"""
Fabric tasks that simplifies updating Devilry, and setting up a demo instance.
"""

from fabric.api import local, abort, task, local



@task
def virtualenv():
    """
    Setup a virtualenv in virtualenv/, run bootstrap in the virtualenv, and run bootstrap.
    """
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
def autodb():
    syncdb()
    local('bin/django_production.py dev_autodb -v2')

@task
def setup_demo():
    """
    Runs ``reset``, ``remove_db`` and ``autodb`` tasks.
    """
    reset()
    autodb()

@task
def clean():
    print('Are you sure you want to completely reset the environment? This '
          'will run "git clean -dfx .", which removes any '
          'untracked files in this directory:')
    local('git clean -ndfx .')
    ok = raw_input('Proceed (y/N)? ')
    if ok != 'y':
        abort('Aborted')
    local('git clean -dfx .')

@task
def reset():
    clean()
    virtualenv()
    refreshstatic()
