from os.path import join, dirname, isdir, exists
from os import listdir
import re
import json

import yaml

from django.core.management.base import BaseCommand, CommandError
from django.utils.importlib import import_module
from django.conf import settings


class I18nBase(object):
    DEFAULT_KEY = 'messages'
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
        filename = self.DEFAULT_KEY
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
        messagesfile = join(i18ndir, self.DEFAULT_KEY + '.yaml')
        if not exists(messagesfile):
            raise CommandError('i18n directory, {i18ndir}, does not contain the required {DEFAULT_KEY}.yaml.'.format(i18ndir=i18ndir,
                                                                                                                     DEFAULT_KEY=self.DEFAULT_KEY))
        self.data[appname] = self.load_default_messagefile(i18ndir)


class I18nMerge(I18nBase):
    """ Merge all translations into a single dict that can be exported as a single file for each toplevel key. """
    def __init__(self, loader):
        self.result = {self.DEFAULT_KEY: {}}
        for appname, i18ndir, default_messages in loader.iterdata():
            self.result[self.DEFAULT_KEY].update(default_messages)
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
                raise CommandError("{messagesfile} contains property, '{key}', "
                                   "that is not in '{DEFAULT_KEY}.yaml'.".format(messagesfile=messagesfile,
                                                                                 key=key,
                                                                                 DEFAULT_KEY=self.DEFAULT_KEY))
        if setname in self.result:
            self.result[setname].update(messages)
        else:
            self.result[setname] = messages

    def _get_merged_data_for_subset(self, setname):
        merged_data = {}
        merged_data.update(self.result[self.DEFAULT_KEY])
        merged_data.update(self.result[setname])
        return merged_data

    def iter_merged(self):
        for setname in self.result:
            if setname == self.DEFAULT_KEY:
                data = self.result[setname]
            else:
                data = self._get_merged_data_for_subset(setname)
            yield setname, data

    def iter_jsonencoded(self, pretty=False):
        if pretty:
            indent = 2
        else:
            indent = None
        for setname, data in self.iter_merged():
            jsondata = json.dumps(data, ensure_ascii=False, encoding='utf-8', indent=indent)
            yield setname, jsondata

    def print_result(self):
        for name, jsondata in self.iter_jsonencoded(pretty=True):
            print
            print "##", name
            print jsondata


class Command(BaseCommand):
    help = 'Create new subject.'

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', '1'))
        extjshelpers_dir =  dirname(import_module('devilry.apps.extjshelpers').__file__)
        outdir = join(extjshelpers_dir, 'static')
        loader = I18nLoader()
        I18nMerge(loader).print_result()
