from os.path import exists
from os import remove
from fabric.api import local, abort, task


DB_FILE = 'db.sqlite3'


@task
def setup_demo():
    """
    Runs ``reset`` and ``autodb`` tasks.
    """
    reset()
    autodb()


@task
def remove_db():
    """ Remove ``db.sqlite3`` if it exists. """
    if exists('db.sqlite3'):
        remove('db.sqlite3')

@task
def virtualenv():
    """
    Setup a virtualenv in virtualenv/.
    """
    local('virtualenv virtualenv')

@task
def bootstrap():
    """
    Run bootstrap with the python executable in the virtualenv.
    """
    local('virtualenv/bin/python ../bootstrap.py')

@task
def refreshstatic():
    """
    Refresh static files
    """
    local('bin/django_dev.py devilry_extjs_jsmerge')
    local('bin/django_dev.py collectstatic --noinput')

@task
def buildout():
    """
    Run bin/buildout.
    """
    local('bin/buildout')

@task
def clean():
    """
    Run ``git clean -dfx``. Asks for confirmation before running.
    """
    print('Are you sure you want to completely reset the environment? This '
          'will run "git clean -dfx --exclude src/", which removes any '
          'untracked files in devenv/:')
    local('git clean -ndfx .')
    ok = raw_input('Proceed (y/N)? ')
    if ok != 'y':
        abort('Aborted')
    local('git clean -dfx .')

@task
def syncdb():
    """
    Run ``bin/django_dev.py syncdb -v0 --noinput``
    """
    local('bin/django_dev.py syncdb -v0 --noinput')

@task
def autogen_extjsmodels():
    """
    Run ``bin/django_dev.py dev_autogen_extjsmodels``
    """
    local('bin/django_dev.py dev_autogen_extjsmodels')

@task
def reset():
    """
    Run the following tasks: clean, virtualenv, bootstrap, buildout, syncdb
    """
    clean()
    virtualenv()
    bootstrap()
    buildout()
    autogen_extjsmodels()

@task
def autodb():
    """
    Run ``remove_db``, ``syncdb`` and ``bin/django_dev.py dev_autodb -v2``
    """
    remove_db()
    syncdb()
    local('bin/django_dev.py dev_autodb -v2')

@task
def noextjsdebug_server():
    """
    Run ``bin/django_dev.py runserver --settings settings.noextjsdebug``
    """
    local('bin/django_dev.py runserver 0.0.0.0:8001 --settings settings.noextjsdebug')


@task
def backup_db(sqldumpfile):
    """
    Dumps a backup of ``db.sqlite3`` to the given ``sqldumpfile``.

    :param sqldumpfile: The SQL file to write the dump to.
    """
    local('sqlite3 db.sqlite3 .dump > {sqldumpfile}'.format(**vars()))

@task
def restore_db(sqldumpfile):
    """
    Restore ``db.sqlite3`` from the given ``sqldumpfile``.

    :param sqldumpfile: The SQL file to restore the database from.
    """
    from os.path import exists
    if exists(DB_FILE):
        remove(DB_FILE)
    local('sqlite3 db.sqlite3 < {sqldumpfile}'.format(**vars()))

@task
def jsbuild(appname, nocompress=False, watch=False, no_jsbcreate=False):
    """
    Use ``bin/django_dev.py senchatoolsbuild`` to build the app with the given
    ``appname``.

    :param appname: Name of an app, like ``devilry_frontpage``.
    :param nocompress: Run with ``--nocompress``. Good for debugging.
    :param watch: Run with ``--watch ../src/``. Good for development.
    :param no_jsbcreate:
        Do not re-create app.jsb3 (the slowest part of building)?
        Re-creating the jsb-file is only needed when you add requirements/deps
        or new files. Set to ``true`` to not generate JSB-file, or set to
        ``next`` and use --watch to generate the jsb-file at startup, but
        not when the watcher triggers re-build.
    """
    extra_args = []
    if nocompress:
        extra_args.append('--nocompress')
    if watch:
        extra_args.append('--watch ../src/')
    if no_jsbcreate:
        if no_jsbcreate == 'next':
            if not watch:
                abort('no_jsbcreate="next" only makes sense with --watch')
            jsbuild(appname, nocompress, watch=False) # build one with no_jsbcreate=False
        extra_args.append('--no-jsbcreate')
    extra_args = ' '.join(extra_args)
    local(('bin/django_dev.py senchatoolsbuild {extra_args} '
           '--app {appname} '
           '--settings settings.extjsbuild').format(appname=appname,
                                                    extra_args=extra_args))
