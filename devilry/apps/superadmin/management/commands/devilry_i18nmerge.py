from os.path import join, dirname
import logging

from django.utils.importlib import import_module
from django.core.management.base import BaseCommand, CommandError

from devilry.apps.superadmin.i18n import (I18nDecoupleFlattened,
                                          #I18nFlatten,
                                          I18nLoader,
                                          I18nError)


class Command(BaseCommand):
    help = 'Create new subject.'

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', '1'))
        extjshelpers_dir =  dirname(import_module('devilry.apps.extjshelpers').__file__)
        outdir = join(extjshelpers_dir, 'static')

        try:
            loader = I18nLoader()
            #I18nFlatten(loader).print_result()
            if verbosity < 1:
                loglevel = logging.ERROR
            elif verbosity > 1:
                loglevel = logging.INFO
            else:
                loglevel = logging.WARNING
            logging.basicConfig(level=loglevel)

            indata = {'core.assignment': 'Oppgave',
                      'core.period': 'Period', # Same value as default
                      'core.subject': 'Kurs',
                      'tull': 'Ball' # Does not exist in default
                     }
            decoupled = I18nDecoupleFlattened(loader, indata)
            decoupled.print_result()
        except I18nError, e:
            raise CommandError(str(e))
