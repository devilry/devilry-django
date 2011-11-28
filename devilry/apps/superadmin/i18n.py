from os.path import join, dirname, isdir, exists
from os import listdir
import re
import json
import logging

import yaml

from django.utils.importlib import import_module
from django.conf import settings


DEFAULT_KEY = 'messages'
DEFAULT_FILE = DEFAULT_KEY + '.yaml'



class ErrorBase(Exception):
    """ """
class MissingDefaultFile(ErrorBase):
    """ """
class InvalidProperty(ErrorBase):
    """ """


def flatformat_encode(data, pretty=False):
    if pretty:
        indent = 2
    else:
        indent = None
    return json.dumps(data, ensure_ascii=False, encoding='utf-8', indent=indent)

def flatformat_decode(stringdata):
    return json.loads(stringdata)


def originalformat_encode(data):
    return yaml.safe_dump(data, indent=4, default_flow_style=False, encoding='utf-8')

def originalformat_decode(stringdata):
    return yaml.load(stringdata)


class Base(object):

    def load_messagefile(self, i18ndir, langcode=None):
        filename = DEFAULT_KEY
        if langcode:
            filename += '_' + langcode
        filename += '.yaml'
        return originalformat_decode(open(join(i18ndir, filename)).read())

    def load_default_messagefile(self, i18ndir):
        return self.load_messagefile(i18ndir)


class Loader(Base):
    def __init__(self):
        self._data = {}
        self._i18ndirs = self._find_i18ndirs_in_installedapps()
        self._load_all_defaultmessages()

    def _find_i18ndirs_in_installedapps(self):
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

    def _load_all_defaultmessages(self):
        for appname, i18ndir in self._i18ndirs:
            self._load_defaultmessages(appname, i18ndir)

    def key_exists(self, key):
        for appname, appdata in self._data.iteritems():
            return key in appdata

    def iterdata(self):
        for appname, i18ndir in self._i18ndirs:
            yield appname, i18ndir, self._data[appname]

    def _load_defaultmessages(self, appname, i18ndir):
        messagesfile = join(i18ndir, DEFAULT_KEY + '.yaml')
        if not exists(messagesfile):
            raise MissingDefaultFile('i18n directory, {i18ndir}, does not contain '
                                     'the required {DEFAULT_FILE}.'.format(DEFAULT_FILE=DEFAULT_FILE, **vars()))
        self._data[appname] = self.load_default_messagefile(i18ndir)


class Flatten(Base):
    """ Flatten all translations into a single dict that can be exported as a single file for each toplevel key. """
    def __init__(self, loader):
        self.result = {DEFAULT_KEY: {}}
        for appname, i18ndir, default_messages in loader.iterdata():
            self.result[DEFAULT_KEY].update(default_messages)
            self._parse_all_subsets(i18ndir, default_messages)

    def _parse_all_subsets(self, i18ndir, default_messages):
        """ Add all subsets (I.E: messages_en.yaml, messages_nb.yaml, ...) to results. """
        for filename in listdir(i18ndir):
            match = re.match('(?P<setname>messages_\w+)\.yaml', filename)
            if match:
                setname = match.groupdict()['setname']
                self._add_to_set(setname, join(i18ndir, filename), default_messages)

    def _add_to_set(self, setname, messagesfile, default_messages=None):
        messages = originalformat_decode(open(messagesfile).read())
        for key in messages:
            if not key in default_messages:
                raise InvalidProperty("{messagesfile} contains property, '{key}', "
                                      "that is not in '{DEFAULT_FILE}'.".format(DEFAULT_FILE=DEFAULT_FILE, **vars()))
        if setname in self.result:
            self.result[setname].update(messages)
        else:
            self.result[setname] = messages

    def _get_merged_data_for_subset(self, setname):
        merged_data = {}
        merged_data.update(self.result[DEFAULT_KEY])
        merged_data.update(self.result[setname])
        return merged_data

    def iter_merged(self):
        for setname in self.result:
            if setname == DEFAULT_KEY:
                data = self.result[setname]
            else:
                data = self._get_merged_data_for_subset(setname)
            yield setname, data

    def iter_flatformatencoded(self, pretty=False):
        for setname, data in self.iter_merged():
            outdata = flatformat_encode(data, pretty)
            yield setname, outdata

    def print_result(self):
        for name, flatformatdata in self.iter_flatformatencoded(pretty=True):
            print
            print "##", name
            print flatformatdata


class DecoupleFlattened(object):
    def __init__(self, loader, data_for_singlelangcode):
        self.result = {}
        self.loader = loader
        self.data_for_singlelangcode = data_for_singlelangcode
        self._check_for_invalid_keys()
        for appname, i18ndir, default_messages in self.loader.iterdata():
            appdata = self._appdatamerge(default_messages)
            if appdata:
                self.result[appname] = appdata

    def _appdatamerge(self, default_messages):
        messages = {}
        for key, defaultvalue in default_messages.iteritems():
            if key in self.data_for_singlelangcode:
                value = self.data_for_singlelangcode[key]
                if value == defaultvalue:
                    logging.info('{key} skipped because value is same as default.'.format(**vars()))
                else:
                    messages[key] = value
        return messages

    def _check_for_invalid_keys(self):
        for key in self.data_for_singlelangcode:
            if not self.loader.key_exists(key):
                logging.warning('{key} does not exists in any "{DEFAULT_FILE}"'.format(DEFAULT_FILE=DEFAULT_FILE, **vars()))

    def _iter_originalformat(self):
        for appname, data in self.result.iteritems():
            yield appname, originalformat_encode(data)

    def print_result(self):
        for appname, formatteddata in self._iter_originalformat():
            print "##", appname
            print formatteddata

