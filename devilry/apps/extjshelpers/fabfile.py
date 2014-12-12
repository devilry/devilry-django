from fabric.api import local, task

@task
def makemessages(langcode):
    local(('../../../../../devenv/bin/django_dev.py makemessages -d djangojs -l {0} '
           '-i "static/extjshelpers/extjs/*" '
           '-i "templates/*" '
           '-i "static/devilry_all_uncompiled.js"'
          ).format(langcode))


@task
def compilemessages():
    local('../../../../../devenv/bin/django_dev.py compilemessages')
