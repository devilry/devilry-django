"""
Basic tasks, mostly useful for setting up demos, and just testing that
example-productionenv/ works.
"""

from fabric.api import local, abort, task


@task
def setup_demo():
    """
    Runs ``reset``, ``remove_db`` and ``autodb`` tasks.
    """
    reset()
    autodb()

@task
def virtualenv():
    """
    Setup a virtualenv in virtualenv/, run bootstrap in the virtualenv, and run bootstrap.
    """
    local('virtualenv virtualenv')
    local('virtualenv/bin/python ../bootstrap.py')
    local('bin/buildout')

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
def syncdb():
    local('bin/django_production.py syncdb -v0 --noinput')

@task
def autogen_extjsmodels():
    local('bin/django_production.py dev_autogen_extjsmodels')
    local('bin/django_production.py devilry_extjs_jsmerge')


@task
def reset():
    clean()
    virtualenv()
    refresh()

@task
def refresh():
    """
    Just run buildout, collectstatic and autogen_extjsmodels. Useful when
    updating the demo when database changes/reset is not required.
    """
    autogen_extjsmodels()
    local('bin/django_production.py collectstatic --noinput')



@task
def autodb():
    syncdb()
    local('bin/django_production.py dev_autodb -v2')
