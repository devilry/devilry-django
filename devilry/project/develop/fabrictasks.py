import os
from os.path import exists, join, relpath
from os import remove, getcwd
import shutil

from fabric.api import local, abort, task
from fabric.context_managers import shell_env, lcd

DB_FILE = join('devilry_developfiles', 'db.sqlite3')
LANGUAGES = ['en', 'nb']


def _managepy(args, djangoenv='develop', environment={}, working_directory=None):
    working_directory = working_directory or getcwd()
    managepy_path = relpath('manage.py', working_directory)
    with shell_env(DJANGOENV=djangoenv, **environment):
        with lcd(working_directory):
            local('python {managepy_path} {args}'.format(managepy_path=managepy_path, args=args))


@task
def remove_db(djangoenv='develop'):
    """ Remove ``db.sqlite3`` if it exists. """
    if djangoenv == 'sqlite_develop':
        if exists(DB_FILE):
            remove(DB_FILE)
    else:
        _managepy('dbdev_destroy', djangoenv=djangoenv)


@task
def syncmigrate(djangoenv='develop'):
    """
    Run ``bin/django_dev.py syncmigrate -v0 --noinput``
    """
    # _managepy('syncdb -v0 --noinput', djangoenv=djangoenv)
    _managepy('migrate --noinput', djangoenv=djangoenv)


@task
def reset_db(djangoenv='develop'):
    """ Run ``remove_db`` followed by ``syncmigrate``. """
    remove_db(djangoenv=djangoenv)
    if djangoenv != 'sqlite_develop':
        _managepy('dbdev_init', djangoenv=djangoenv)
    syncmigrate(djangoenv=djangoenv)


# @task
# def sandbox():
#     _managepy('devilry_sandboxcreate -s "duck2050" -l "DUCK2050 - Programmering uten grenser"')


@task
def autodb(djangoenv='develop', no_groups=False):
    """
    Run ``remove_db``, ``syncmigrate`` and ``bin/django_dev.py devilry_developer_old_autodb -v2``

    :param djangoenv: The DJANGOENV to use.
    :param no_groups: Use ``autodb:no_groups=yes`` to run devilry_developer_old_autodb with --no-groups.
    """
    no_groups = no_groups == 'yes'
    autodb_args = ''
    if no_groups:
        autodb_args = '--no-groups'
    reset_db(djangoenv=djangoenv)
    _managepy('devilry_developer_old_autodb -v2 {}'.format(autodb_args))
    # _managepy('rebuild_index --noinput')


@task
def demodb(djangoenv='develop'):
    """
    Run ``remove_db``, ``syncmigrate`` and ``bin/django_dev.py devilry.project.develop_demodb``

    :param djangoenv: The DJANGOENV to use.
    """
    reset_db(djangoenv=djangoenv)
    _managepy('devilry_developer_demodb',
              djangoenv=djangoenv,
              environment={
                  'DEVILRY_EMAIL_BACKEND': 'django.core.mail.backends.dummy.EmailBackend'
              })


def _demodb_managepy(command, djangoenv):
    _managepy(command,
              djangoenv=djangoenv,
              environment={
                  'DEVILRY_EMAIL_BACKEND': 'django.core.mail.backends.dummy.EmailBackend'
              })


@task
def new_demodb(djangoenv='develop'):
    """
    Run ``remove_db``, ``syncmigrate`` and ... TODO

    :param djangoenv: The DJANGOENV to use.
    """
    reset_db(djangoenv=djangoenv)
    _demodb_managepy('devilry_developer_demodb_createusers', djangoenv=djangoenv)


@task
def makemessages():
    for languagecode in LANGUAGES:
        _managepy(
            'makemessages '
            '--ignore "static*" '
            '-l {}'.format(languagecode), working_directory='devilry')


@task
def makemessages_javascript():
    """
    Build
    """
    for languagecode in LANGUAGES:
        _managepy(
            'makemessages '
            '-d djangojs '
            '--ignore "app-all.js" '
            '--ignore "all-classes.js" '
            '--ignore "node_modules" '
            '--ignore "bower_components" '
            '-l {}'.format(languagecode), working_directory='devilry')


@task
def compilemessages():
    _managepy('compilemessages', working_directory='devilry')


@task
def sync_cradmin_theme_into_devilry_theme(cradmin_root_dir):
    """
    Copies ``cradmin_base/`` and ``cradmin_theme_default/`` into
    the devilry_theme ``less/`` directory.
    """
    devilry_theme_lessdir = os.path.join(*'devilry/devilry_theme3/staticsources/devilry_theme3/styles'.split('/'))
    cradmin_lessdir = os.path.join(cradmin_root_dir, *'django_cradmin/static/django_cradmin/src/less'.split('/'))
    for directory in 'cradmin_base', 'cradmin_theme_default', 'cradmin_theme_topmenu':
        sourcedir = os.path.join(cradmin_lessdir, directory)
        destinationdir = os.path.join(devilry_theme_lessdir, directory)
        print 'Syncing', sourcedir, 'to', destinationdir
        if os.path.exists(destinationdir):
            shutil.rmtree(destinationdir)
        shutil.copytree(sourcedir, destinationdir)
        local('git add {}'.format(destinationdir))


@task
def test():
    """
    Run all the tests.
    """
    _managepy('test devilry', djangoenv='test')


@task
def codeship_test():
    """
    Run all the tests with settings for CodeShip CI.
    """
    _managepy('test devilry', djangoenv='codeship_test')


@task
def remove_pyc_files():
    os.system('find . -name "*.pyc" -exec rm {} \;')


@task
def make_source_dist():
    local('git rm -r devilry/devilry_theme3/static/devilry_theme3/')
    local('ievv buildstatic --production --yarn-clean-node-modules')
    local('git add devilry/devilry_theme3/static/devilry_theme3/')
    local('python setup.py sdist')
