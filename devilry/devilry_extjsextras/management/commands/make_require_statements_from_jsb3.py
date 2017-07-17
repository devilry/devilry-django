import logging
from django.core.management.base import BaseCommand, CommandError
import os
import json


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<current-django-appname> <jsb3-file>'
    help = 'Make javascript require() statements from an ExtJS jsb3 file.'

    def _get_static_path(self, django_appname):
        return os.path.abspath(os.path.join('devilry', django_appname, 'static'))

    def _get_appdirectory_path(self, django_appname):
        return os.path.join(self._get_static_path(django_appname), django_appname, 'app')

    def _make_require_statement(self, absolute_path, relative_to_path):
        relative_path = os.path.relpath(absolute_path, relative_to_path)
        relative_path = relative_path.replace(os.sep, '/')
        if not relative_path.startswith('..'):
            relative_path = './{}'.format(relative_path)
        return 'require("{}");'.format(relative_path)

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('<current-django-appname> and <jsb3-file> is required')
        current_django_appname = args[0]
        current_appdirectory_path = self._get_appdirectory_path(current_django_appname)
        jsb3 = json.loads(open(args[1], 'rb').read())
        print self._make_require_statement(
            absolute_path=os.path.abspath(os.path.join('devilry', 'devilry_extjsextras', 'extjs_sources', 'ext-all.js')),
            relative_to_path=current_appdirectory_path)
        for fileinfo in jsb3['builds'][0]['files']:
            dirname = fileinfo['path']
            if not dirname.startswith('static/devilry_'):
                continue
            django_appname = dirname.split('/')[1]
            appstatic_relative_relative_path = dirname.split('/')[1:]
            appstatic_relative_relative_path.append(fileinfo['name'])
            absolute_path = os.path.join(
                self._get_static_path(django_appname), *appstatic_relative_relative_path)
            print self._make_require_statement(
                absolute_path=absolute_path,
                relative_to_path=current_appdirectory_path)
