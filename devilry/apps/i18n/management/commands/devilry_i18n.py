from os import linesep
import re
import logging
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from devilry.apps.i18n import i18n


class Command(BaseCommand):
    help = 'Manage Devilry translations. Se the devilry documentation at http://devilry.org for more help.'
    args = ('{linesep}'
            '{indent}load <language-code> <infile>{linesep}'
            '{indent}export').format(linesep=linesep, indent='         ')
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
    )

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', '1'))
        if len(args) < 1:
            raise CommandError('An action is required. See --help.')
        action = args[0]

        self.setup_logging(verbosity)
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

    def setup_logging(self, verbosity):
        if verbosity < 1:
            loglevel = logging.ERROR
        elif verbosity == 1:
            loglevel = logging.WARNING
        elif verbosity == 2:
            loglevel = logging.INFO
        else:
            loglevel = logging.DEBUG
        logging.basicConfig(level=loglevel)

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
