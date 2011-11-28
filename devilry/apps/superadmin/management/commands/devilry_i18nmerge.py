from os.path import join, dirname, isdir, exists
from os import listdir
import re

import yaml

from django.core.management.base import BaseCommand, CommandError
from django.utils.importlib import import_module
from django.conf import settings


class I18nBase(object):
    def find_i18ndirs_in_installedapps(self):
        i18ndirs = []
        for app in settings.INSTALLED_APPS:
            if not app.startswith('django.'):
                appname = app.split('.')[-1]
                mod = import_module(app)
                if exists(mod.__file__) and isdir(dirname(mod.__file__)):
                    moddir = dirname(mod.__file__)
                    i18ndir = join(moddir, 'static', appname, 'i18n')
                    if exists(i18ndir):
                        i18ndirs.append([appname, i18ndir])
        return i18ndirs

    def load_messagefile(self, i18ndir, langcode=None):
        filename = 'messages'
        if langcode:
            filename += '_' + langcode
        filename += '.yaml'
        return yaml.load(open(join(i18ndir, filename)).read())

    def load_default_messagefile(self, i18ndir):
        return self.load_messagefile(i18ndir)


class I18nLoader(I18nBase):
    def __init__(self):
        self.data = {}
        self.i18ndirs = self.find_i18ndirs_in_installedapps()
        self._load_all_defaultmessages()

    def _load_all_defaultmessages(self):
        for appname, i18ndir in self.i18ndirs:
            self._load_defaultmessages(appname, i18ndir)

    def iterdata(self):
        for appname, i18ndir in self.i18ndirs:
            yield appname, i18ndir, self.data[appname]

    def _load_defaultmessages(self, appname, i18ndir):
        messagesfile = join(i18ndir, 'messages.yaml')
        if not exists(messagesfile):
            raise CommandError('i18n directory, {i18ndir}, does not contain the required messages.yaml.'.format(**vars()))
        self.data[appname] = self.load_default_messagefile(i18ndir)


class I18nMerge(I18nBase):
    """ Merge all translations into a single map that can be exported as a single file. """
    def __init__(self, loader):
        self.result = {'messages': {}}
        for appname, i18ndir, default_messages in loader.iterdata():
            self.result['messages'].update(default_messages)
            self._parse_all_subsets(i18ndir, default_messages)

    def _parse_all_subsets(self, i18ndir, default_messages):
        """ Add all subsets (I.E: messages_en.yaml, messages_nb.yaml, ...) to results. """
        for filename in listdir(i18ndir):
            match = re.match('(?P<setname>messages_\w+)\.yaml', filename)
            if match:
                setname = match.groupdict()['setname']
                self._add_to_set(setname, join(i18ndir, filename), default_messages)

    def _add_to_set(self, setname, messagesfile, default_messages=None):
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
        loader = I18nLoader()
        I18nMerge(loader).print_result()
