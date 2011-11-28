from os import linesep
from os.path import join, dirname
import logging
from optparse import make_option

from django.utils.importlib import import_module
from django.core.management.base import BaseCommand, CommandError

from devilry.apps.superadmin import i18n


class Command(BaseCommand):
    help = 'Create new subject.'
    args = ('{linesep}'
            '{indent}load <langcode> <infile>{linesep}'
            '{indent}export').format(linesep=linesep, indent='         ')
    option_list = BaseCommand.option_list + (
        make_option('--preview',
            action='store_true',
            dest='preview',
            default=False,
            help='Preview action instead of storing results on the filesystem.'),
        )

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', '1'))
        if len(args) < 1:
            raise CommandError('An action is required. See --help.')
        action = args[0]
        extjshelpers_dir =  dirname(import_module('devilry.apps.extjshelpers').__file__)
        outdir = join(extjshelpers_dir, 'static', 'i18n')

        if verbosity < 1:
            loglevel = logging.ERROR
        elif verbosity > 1:
            loglevel = logging.INFO
        else:
            loglevel = logging.WARNING
        logging.basicConfig(level=loglevel)

        try:
            loader = i18n.Loader()
        except i18n.ErrorBase, e:
            raise CommandError(str(e))

        if action == 'export':
            try:
                flattened = i18n.Flatten(loader)
            except i18n.ErrorBase, e:
                raise CommandError(str(e))
            if options['preview']:
                flattened.print_result()
        elif action == 'load':
            if len(args) < 3:
                raise CommandError('langcode and infile is required. See --help.')
            langcode = args[1]
            infilename = args[2]
            indata = i18n.flatformat_decode(open(infilename).read())
            try:
                decoupled = i18n.DecoupleFlattened(loader, indata)
                if options['preview']:
                    decoupled.print_result()
                else:
                    decoupled.save(langcode)
            except i18n.ErrorBase, e:
                raise CommandError(str(e))
