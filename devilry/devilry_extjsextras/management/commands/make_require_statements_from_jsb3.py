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
        # print self._make_require_statement(
        #     absolute_path=os.path.abspath(os.path.join('devilry', 'devilry_extjsextras', 'extjs_sources', 'ext-all.js')),
        #     relative_to_path=current_appdirectory_path)
        extjs_dependencies = []
        devilry_dependencies = []
        for fileinfo in jsb3['builds'][0]['files']:
            dirname = fileinfo['path']
            if dirname.startswith('static/devilry_'):
                django_appname = dirname.split('/')[1]
                appstatic_relative_relative_path = dirname.split('/')[1:]
                appstatic_relative_relative_path.append(fileinfo['name'])
                absolute_path = os.path.join(
                    self._get_static_path(django_appname), *appstatic_relative_relative_path)
                devilry_dependencies.append(absolute_path)
            elif dirname.startswith('static/extjs4/src/'):
                relative_path = os.path.join(dirname.split('extjs4/src/')[1], fileinfo['name'])
                absolute_path = os.path.abspath(os.path.join(
                    'devilry', 'devilry_extjsextras', 'extjs_sources',
                    relative_path))
                extjs_dependencies.append(absolute_path)
            else:
                raise CommandError('Unknown path: {!r}'.format(fileinfo))

        file_lines = []
        file_lines.append('')
        file_lines.append('// ExtJS imports')
        for absolute_path in extjs_dependencies:
            file_lines.append(self._make_require_statement(
                absolute_path=absolute_path,
                relative_to_path=current_appdirectory_path))
        file_lines.append('')
        file_lines.append('// Devilry imports')
        for absolute_path in devilry_dependencies:
            file_lines.append(self._make_require_statement(
                absolute_path=absolute_path,
                relative_to_path=current_appdirectory_path))
        file_lines.append('require("../app.js");')
        open(os.path.join(current_appdirectory_path, 'entry.js'), 'wb').write(
            '\n'.join(file_lines))
