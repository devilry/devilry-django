import logging
from os import linesep, walk
from os.path import relpath, join, exists
import re
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from devilry.apps.i18n import i18n
from devilry.apps.i18n.utils import find_all_translatestrings
from devilry.utils.command import setup_logging, get_verbosity
from devilry.utils.importutils import get_installed_apps


class Command(BaseCommand):
    help = 'Manage Devilry translations. Se the devilry documentation at http://devilry.org for more help.'
    args = ('{linesep}'
            '{indent}load <language-code> <infile>{linesep}'
            '{indent}export{linesep}'
            '{indent}find [appname]').format(linesep=linesep, indent='         ')
    option_list = BaseCommand.option_list + (
        make_option('-p', '--preview',
            action='store_true',
            dest='preview',
            default=False,
            help='Preview action instead of storing results on the filesystem.'),
        make_option('-n', '--no-local-prefix',
            action='store_false',
            dest='use_local_prefix',
            default=True,
            help=('Do not prefix the output file with "local-". ONLY '
                  'use this for translations that are to be added to '
                  'the Devilry distribution.')
        ),
        make_option('-o', '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help=('Overwrite existing translations with the same language-code '
                  'with your provided translation. Without this, the "load" '
                  'command will refuse to overwrite any existing translations.')
        ),
        make_option('--create-skeleton',
            action='store_true',
            dest='createskel',
            default=False,
            help=('Create a skeleton for translation of the application specified for the "find" action.')
        ),
        make_option('--group-by-fslocation',
            action='store_true',
            dest='group_by_fslocation',
            default=False,
            help=('Group the printed translations by filesystem location '
                  'instead of their owning app. This will print all locations '
                  'where there is a translate string instead of the application '
                  'where the string belongs.')
        ),
    )

    def handle(self, *args, **options):
        verbosity = get_verbosity(options)
        if len(args) < 1:
            raise CommandError('An action is required. See --help.')
        action = args[0]
        setup_logging(verbosity)

        if not action in ('find', 'load', 'export'):
            raise CommandError('Invalid action. Must be one of: load, export, find. See --help for more details.')
        if action == 'find':
            if len(args) == 2:
                appname = args[1]
            else:
                appname = None
            self.handle_find(appname, createskel=options['createskel'], group_by_fslocation=options['group_by_fslocation'])
        else:
            try:
                loader = i18n.Loader()
            except i18n.ErrorBase, e:
                raise CommandError(str(e))
            if action == 'export':
                self.handle_export(loader, options['preview'])
            elif action == 'load':
                if len(args) < 3:
                    raise CommandError('langcode and infile is required. See --help.')
                langcode = args[1]
                self._validate_langcode(langcode)
                infilename = args[2]
                self.handle_load(loader,
                                 self._get_actual_langcode(langcode, options['use_local_prefix']),
                                 infilename,
                                 options['preview'],
                                 options['overwrite'])


    def _validate_langcode(self, langcode):
        if not re.match('[a-z0-9_-]+', langcode):
            raise CommandError('<language-code> can only contain the following letters: "a-z0-9_-".')

    def handle_export(self, loader, preview):
        try:
            flattened = i18n.Flatten(loader)
        except i18n.ErrorBase, e:
            raise CommandError(str(e))
        if preview:
            flattened.print_result()
        else:
            flattened.save()

    def handle_load(self, loader, langcode, infilename, preview, overwrite):
            indata = i18n.flatformat_decode(open(infilename).read())
            try:
                decoupled = i18n.DecoupleFlattened(loader, indata)
                if preview:
                    decoupled.print_result(langcode)
                else:
                    if decoupled.langcode_exists(langcode) and not overwrite:
                        raise CommandError('"{0}" exists. Use --overwrite to overwrite the existing '
                                           'translation with your translation.'.format(langcode))
                    files_written = decoupled.save(langcode)
            except i18n.ErrorBase, e:
                raise CommandError(str(e))

    def _get_actual_langcode(self, langcode, use_local_prefix):
        if use_local_prefix:
            return 'local-' + langcode
        else:
            return langcode

    def _iter_translatestrings_in_dir(self, appdir, appname):
        for root, dirs, files in walk(appdir):
            for filename in files:
                if appname == 'i18n' and filename == 'tests.py': # avoids hitting the test strings in i18n.tests
                    continue
                if filename.endswith('.js') or filename.endswith('.py'):
                    filepath = join(root, filename)
                    translatestrings = find_all_translatestrings(open(filepath).read())
                    if translatestrings:
                        appdirrelativepath = relpath(filepath, appdir)
                        yield appdirrelativepath, translatestrings

    def _find_translatestrings(self):
        by_location_in_fs = {}
        for appdir, mod, appname in get_installed_apps():
            if 'extjshelpers' in appdir: # Ignore extjshelpers (avoids reading ALL files in the extjs source).
                continue
            for appdirrelativepath, translatestrings in self._iter_translatestrings_in_dir(appdir, appname):
                if not appname in by_location_in_fs:
                    by_location_in_fs[appname] = {'appdir': appdir, 'fileswithtranslations': []}
                by_location_in_fs[appname]['fileswithtranslations'].append((appdirrelativepath, translatestrings))
        return by_location_in_fs


    def _group_by_owning_app(self, by_location_in_fs):
        by_owning_app = {}
        for appname, translations in by_location_in_fs.iteritems():
            for appdirrelativepath, translatestrings in translations['fileswithtranslations']:
                for translatestring in translatestrings:
                    owning_appname = translatestring.split('.')[0]
                    if not owning_appname in by_owning_app:
                        by_owning_app[owning_appname] = dict(appdir=translations['appdir'],
                                                             translatestrings=set())
                    by_owning_app[owning_appname]['translatestrings'].add(translatestring)
        return by_owning_app


    def _createskeleton(self, appname, appdir, translatestrings):
        path = join(appdir, 'static', appname, 'i18n', 'messages.yaml')
        if exists(path):
            raise CommandError('Can not create skeleton in {0}. The file already exists.'.format(path))
        else:
            yamldata = '\n'.join(self._format_translatestrings_skeleton(translatestrings))
            logging.debug('Writing the following to %s: %s', path, yamldata)
            open(path, 'w').write(yamldata)
            logging.info('Created %s', path)


    def _format_translatestrings_skeleton(self, translatestrings):
        for translatestring in sorted(translatestrings):
            yield '{0}: '.format(translatestring)

    def _print_by_fs_location(self, by_location_in_fs):
        for appname, translations in by_location_in_fs.iteritems():
            print
            print
            print '=================================='
            print appname
            print '=================================='

            for appdirrelativepath, translatestrings in translations['fileswithtranslations']:
                print
                print '#', appdirrelativepath
                for out in self._format_translatestrings_skeleton(translatestrings):
                    print out


    def _print_by_owning_app(self, by_owning_app):
        for appname, apptranslation in by_owning_app.iteritems():
            print
            print
            print '=================================='
            print appname
            print '=================================='
            for out in self._format_translatestrings_skeleton(apptranslation['translatestrings']):
                print out


    def handle_find(self, appname=None, createskel=False, group_by_fslocation=False):
        by_location_in_fs = self._find_translatestrings()
        if appname and not appname in by_location_in_fs:
            raise CommandError('Could not find any dtranslate(...) marked strings in the "{0}" app.'.format(appname))
        by_owning_app = self._group_by_owning_app(by_location_in_fs)

        if group_by_fslocation:
            self._print_by_fs_location(by_location_in_fs)
        else:
            self._print_by_owning_app(by_owning_app)
        print
        print

        if createskel:
            if not appname:
                raise CommandError('--create-skel requires an appname. See --help.')
            self._createskeleton(appname, **by_owning_app[appname])
