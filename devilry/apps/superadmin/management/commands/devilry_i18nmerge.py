from os import linesep
from os.path import join, dirname
import logging

from django.utils.importlib import import_module
from django.core.management.base import BaseCommand, CommandError

from devilry.apps.superadmin import i18n


class Command(BaseCommand):
    args = ('{linesep}'
            '{indent}load <langcode> <infile>{linesep}'
            '{indent}export{linesep}'
            '{indent}export_preview').format(linesep=linesep, indent='         ')

    help = 'Create new subject.'

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
        except i18n.Error, e:
            raise CommandError(str(e))

        if action.startswith('export'):
            try:
                flattened = i18n.Flatten(loader)
            except i18n.Error, e:
                raise CommandError(str(e))
            if action == 'export':
                pass
            else:
                flattened.print_result()
        elif action == 'load':
            if len(args) < 3:
                raise CommandError('langcode and infile is required. See --help.')
            langcode = args[1]
            infilename = args[2]
            indata = i18n.flatformat_decode(open(infilename).read())
            try:
                decoupled = i18n.DecoupleFlattened(loader, indata)
                decoupled.print_result()
            except i18n.Error, e:
                raise CommandError(str(e))
