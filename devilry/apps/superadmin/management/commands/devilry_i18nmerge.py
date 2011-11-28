from os.path import join, dirname, isdir, exists
from os import listdir
import re

import yaml

from django.core.management.base import BaseCommand, CommandError
from django.utils.importlib import import_module
from django.conf import settings


class I18nMerger(object):
    def __init__(self):
        self.result = {'messages': {}}
        i18ndirs = self._find_i18ndirs_in_installedapps()
        for i18ndir in i18ndirs:
            self._parse_messages(i18ndir)

    def _find_i18ndirs_in_installedapps(self):
        i18ndirs = set()
        for app in settings.INSTALLED_APPS:
            if not app.startswith('django.'):
                appname = app.split('.')[-1]
                mod = import_module(app)
                if exists(mod.__file__) and isdir(dirname(mod.__file__)):
                    moddir = dirname(mod.__file__)
                    i18ndir = join(moddir, 'static', appname, 'i18n')
                    if exists(i18ndir):
                        i18ndirs.add(i18ndir)
        return i18ndirs

    def _parse_messages(self, i18ndir):
        """ Add all messages.yaml to results. """
        messagesfile = join(i18ndir, 'messages.yaml')
        if not exists(messagesfile):
            raise CommandError('i18n directory, {i18ndir}, does not contain the required messages.yaml.'.format(**vars()))
        default_messages = self._add_default_messages_to_results(messagesfile)
        self._parse_all_subsets(i18ndir, default_messages)

    def _add_default_messages_to_results(self, messagesfile):
        default_messages = yaml.load(open(messagesfile).read())
        for key in default_messages:
            if key in self.result['messages']:
                raise CommandError("{messagesfile} contains property, '{key}', that is present in another 'messages.yaml'.".format(**vars()))
        self.result['messages'].update(default_messages)
        return default_messages

    def _parse_all_subsets(self, i18ndir, default_messages):
        """ Add all subsets (I.E: messages_en.yaml, messages_nb.yaml, ...) to results. """
        for filename in listdir(i18ndir):
            match = re.match('(?P<setname>messages_\w+)\.yaml', filename)
            if match:
                setname = match.groupdict()['setname']
                self._add_to_set(setname, join(i18ndir, filename), default_messages)

    def _add_to_set(self, setname, messagesfile, default_messages):
        messages = yaml.load(open(messagesfile).read())
        for key in messages:
            if not key in default_messages:
                raise CommandError("{messagesfile} contains property, '{key}', that is not in 'messages.yaml'.".format(**vars()))
        if setname in self.result:
            self.result[setname].update(messages)
        else:
            self.result[setname] = messages

    def print_result(self):
        from pprint import pprint
        pprint(self.result)


class Command(BaseCommand):
    help = 'Create new subject.'

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', '1'))
        extjshelpers_dir =  dirname(import_module('devilry.apps.extjshelpers').__file__)
        outdir = join(extjshelpers_dir, 'static')
        I18nMerger().print_result()
