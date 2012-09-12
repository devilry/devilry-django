from os import walk, sep
from os.path import join, dirname, isdir, exists, basename
import re

from django.core.management.base import BaseCommand
from django.utils.importlib import import_module
from django.conf import settings


class JsFile(object):
    DEFINEPATT = re.compile(r"^Ext\.define\(.(.+?).\s*,", re.MULTILINE)
    EXTENDPATT = re.compile(r"^\s*extend\s*:\s*['\"](.+?)['\"]", re.MULTILINE|re.DOTALL)
    MODELPATT = re.compile(r"^\s*model\s*:\s*['\"](.+?)['\"]", re.MULTILINE|re.DOTALL)
    REQUIRESPATT = re.compile(r"^\s*requires\s*:\s*\[(.*?)\]", re.MULTILINE|re.DOTALL)
    MIXINSPATT = re.compile(r"^\s*mixins\s*:\s*{(.*?)}", re.MULTILINE|re.DOTALL)
    LISTSPLITPATT = re.compile(r'[\'"](.*?)[\'"]')

    def __init__(self, filepath):
        self.filepath = filepath
        self.filecontent = open(self.filepath, 'rb').read()
        self.match_define()
        self.match_requires() # must be before extend and mixins, since they add to self.requires
        self.match_extend()
        self.match_mixins()
        self.match_model()
        self.requires = filter(lambda r: not r.startswith('Ext.'), self.requires)

    def match_define(self):
        m = self.DEFINEPATT.search(self.filecontent)
        if m:
            self.clsname = m.groups()[0]
        else:
            raise ValueError('{0}: no Ext.define(....) found.'.format(self.filepath))

    def match_requires(self):
        m = self.REQUIRESPATT.search(self.filecontent)
        if m:
            requiresstr = m.groups()[0]
            self.requires = self.LISTSPLITPATT.findall(requiresstr)
        else:
            self.requires = []
        if 'devilryrestproxy' in self.filecontent and basename(self.filepath) != 'RestProxy.js':
            self.requires.append('devilry.extjshelpers.RestProxy')

    def match_extend(self):
        m = self.EXTENDPATT.search(self.filecontent)
        if m:
            self.extend = m.groups()[0]
            self.requires.append(self.extend)
        else:
            self.extend = None

    def match_mixins(self):
        m = self.MIXINSPATT.search(self.filecontent)
        if m:
            mixinsstr = m.groups()[0]
            self.mixins = self.LISTSPLITPATT.findall(mixinsstr)
            self.requires += self.mixins
        else:
            self.mixins = []

    def match_model(self):
        m = self.MODELPATT.search(self.filecontent)
        if m:
            model = m.groups()[0]
            self.requires.append(model)

    def __str__(self):
        return "{0}: {1} ({2})".format(self.clsname, self.extend, ','.join(self.requires))


def depsfullfilled(jsfile, jsfiles):
    for req in jsfile.requires:
        if req in jsfiles:
            return False
    return True

def orderJsFiles(jsfiles):
    ordered = []
    while jsfiles:
        for clsname in jsfiles.keys():
            jsfile = jsfiles[clsname]
            if depsfullfilled(jsfile, jsfiles):
                ordered.append(jsfile)
                del jsfiles[clsname]
    return ordered


def collect_jsfiles(jsfiles, rootdir, verbose):
    ignorefilepatt = re.compile('^.*?(configeditor.js|drafteditor.js|formatoverrides.js|app-all.js|all-classes\.js|devilry_all_uncompiled\.js|django\.js)$')
    includedirpatt = re.compile(r'(extjs_classes|extjsux|devilry_header|devilry_extjsextras|devilry_i18n|devilry_authenticateduserinfo)')
    for root, dirs, files in walk(rootdir):
        unixstyledir = root.replace(sep, '/')
        if not includedirpatt.search(root): continue
        for filename in files:
            if filename.endswith('.js'):
                filepath = join(root, filename)
                if not ignorefilepatt.match(filename):
                    try:
                        jsfile = JsFile(filepath)
                    except ValueError, e:
                        if verbose:
                            print str(e)
                    else:
                        jsfiles[jsfile.clsname] = jsfile

def collect_jsfiles_in_installedapps(jsfiles, verbose):
    for app in settings.INSTALLED_APPS:
        if not app.startswith('django.'):
            mod = import_module(app)
            if exists(mod.__file__) and isdir(dirname(mod.__file__)):
                moddir = dirname(mod.__file__)
                collect_jsfiles(jsfiles, moddir, verbose)



class Command(BaseCommand):
    help = 'Create new subject.'

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', '1'))
        extjshelpers_dir =  dirname(import_module('devilry.apps.extjshelpers').__file__)
        outfile = join(extjshelpers_dir, 'static', 'devilry_all_uncompiled.js')
        jsfiles = {}
        collect_jsfiles_in_installedapps(jsfiles, verbose=verbosity>1)
        ordered = orderJsFiles(jsfiles)
        open(outfile, 'wb').write('\n\n'.join([j.filecontent for j in ordered]))
