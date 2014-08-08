from fabric.api import local, task

@task
def compilemessages():
    local('../../../devenv/bin/django_dev.py compilemessages')
