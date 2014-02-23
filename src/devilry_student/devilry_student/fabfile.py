from fabric.api import local, task

@task
def makemessages(langcode):
    local(('../../../devenv/bin/django_dev.py makemessages -d djangojs -l {0} '
           '-i "static/devilry_student/bower/*" '
           '-i "static/devilry_student/node_modules/*" '
           '-i "static/devilry_student/app-all.js" '
           '-i "static/devilry_student/all-classes.js"'
          ).format(langcode))
    local(('../../../devenv/bin/django_dev.py makemessages -l {0} '
       '-i "static/*"').format(langcode))


@task
def compilemessages():
    local('../../../devenv/bin/django_dev.py compilemessages')
