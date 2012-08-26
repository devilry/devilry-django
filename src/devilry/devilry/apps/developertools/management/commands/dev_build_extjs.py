from pprint import pprint
from os import walk
from os.path import join, exists
import re
import logging
from django.core.management.base import BaseCommand, CommandError
from devilry.utils.command import setup_logging, get_verbosity

from devilry.utils.importutils import get_staticdir_from_appname



def get_appname_from_classpath(classpath):
    if classpath.startswith('Ext.'):
        return 'extjs4'
    else:
        return classpath.split('.')[0]

def get_extjs_sourceroot_from_appname(appname):
    appdir = get_staticdir_from_appname(appname)
    if appname == 'extjs4':
        return join(appdir, 'src')
    if exists(join(appdir, 'app')):
        return join(appdir, 'app')
    else:
        return appdir

def get_extjs_appfile_from_appname(appname):
    return join(get_staticdir_from_appname(appname), 'app.js')



class SimpleJsFile(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.filecontent = open(self.filepath, 'rb').read()

    def __str__(self):
        return 'SIMPLE: {filepath}'.format(**self.__dict__)

    def collect_jsfiles(self, collected_jsfiles_map):
        pass


class JsFile(SimpleJsFile):
    """
    Collects information about an ExtJS javascript file, including:

        - classname (define)
        - dependencies:
            - mixins
            - model
            - requires
    """
    DEFINEPATT = re.compile(r"^Ext\.define\(.(.+?).\s*,", re.MULTILINE)
    EXTENDPATT = re.compile(r"^\s*extend\s*:\s*['\"](.+?)['\"]", re.MULTILINE|re.DOTALL)
    MODELPATT = re.compile(r"^\s*model\s*:\s*['\"](.+?)['\"]", re.MULTILINE|re.DOTALL)
    REQUIRESPATT = re.compile(r"^\s*requires\s*:\s*\[(.*?)\]", re.MULTILINE|re.DOTALL)
    MIXINSPATT = re.compile(r"^\s*mixins\s*:\s*{(.*?)}", re.MULTILINE|re.DOTALL)
    LISTSPLITPATT = re.compile(r'[\'"](.*?)[\'"]')
    EXTJS_ALTERNATE_NAMES = {
                             # Alternative names
                             'Ext.Element': 'Ext.dom.Element',
                             'Ext.core.Element': 'Ext.dom.Element',
                             'Ext.CompositeElement': 'Ext.dom.CompositeElement',
                             # Singleton instances
                             'Ext.TaskManager': 'Ext.util.TaskManager',
                             'Ext.Msg': 'Ext.window.MessageBox',
                             'Ext.MessageBox': 'Ext.window.MessageBox',
                             }

    def __init__(self, filepath):
        super(JsFile, self).__init__(filepath)
        self.extend = None
        self.parse()

    def parse(self):
        self.match_define()
        self.match_requires() # must be before extend and mixins, since they add to self.requires
        self.match_extend()
        self.match_mixins()
        self.match_model()
        #self.requires = filter(lambda r: not r.startswith('Ext.'), self.requires)

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


    def create_jsfile_for_extjsclass(self, classname):
        """
        ``create_jsfile_for_class``, but with all of the hacks required to
        handle finding stuff in the extjs sources.
        """
        if classname in self.EXTJS_ALTERNATE_NAMES:
            return self.create_jsfile_for_extjsclass(self.EXTJS_ALTERNATE_NAMES[classname])
        from os import sep
        appdir = get_extjs_sourceroot_from_appname('extjs4')
        relativepath = sep.join(classname.split('.')[1:]) + '.js'
        app_path = join(appdir, relativepath)
        if not exists(app_path):
            relativepath = join('core', 'src', relativepath)
            app_path = join(appdir, relativepath)
        try:
            return JsFile(app_path)
        except ValueError:
            return SimpleJsFile(app_path)

    def create_jsfile_for_class(self, classname):
        django_appname = get_appname_from_classpath(classname)
        if django_appname == 'extjs4':
            return self.create_jsfile_for_extjsclass(classname)
        from os import sep
        appdir = get_extjs_sourceroot_from_appname(django_appname)
        relativepath = sep.join(classname.split('.')[1:]) + '.js'
        app_path = join(appdir, relativepath)
        return JsFile(app_path)


    def __str__(self):
        return "{0}: {1} ({2})".format(self.clsname, self.extend, ','.join(self.requires))

    def prettyprint(self):
        print('#################################')
        print('# {0}'.format(self))
        print('#################################')
        print('## Extend:')
        print(self.extend)
        print('## Requires:')
        pprint(self.requires)
        print('## Mixins:')
        pprint(self.mixins)

    def collect_jsfiles(self, collected_jsfiles_map):
        logging.debug('Collecting deps of {0}'.format(self.filepath))
        for classname in self.requires:
            jsfile = self.create_jsfile_for_class(classname)
            if not jsfile.filepath in collected_jsfiles_map:
                collected_jsfiles_map[jsfile.filepath] = jsfile
                jsfile.collect_jsfiles(collected_jsfiles_map)


class ControllerFile(JsFile):
    CONTROLLERS_PATT = re.compile(r"^\s*controllers\s*:\s*\[(.*?)\]", re.MULTILINE|re.DOTALL)

    def __init__(self, filepath, appdir):
        self.appdir = appdir
        super(ControllerFile, self).__init__(filepath)

    def parse(self):
        super(ControllerFile, self).parse()
        self.match_controllers()

    def match_controllers(self):
        m = self.CONTROLLERS_PATT.search(self.filecontent)
        if m:
            controllersstr = m.groups()[0]
            self.controllers = self.LISTSPLITPATT.findall(controllersstr)
        else:
            self.controllers = []

    def prettyprint(self):
        super(ControllerFile, self).prettyprint()
        print('## Controllers:')
        pprint(self.controllers)


class AppFile(ControllerFile):
    def __init__(self, appfile, appname):
        self.appname = appname
        self.appdir = join(get_staticdir_from_appname(appname), 'app')
        super(AppFile, self).__init__(appfile, self.appdir)

    def match_define(self):
        pass

    def __str__(self):
        return "APP {appname}".format(**self.__dict__)

    def collect_jsfiles(self, collected_jsfiles_map):
        super(AppFile, self).collect_jsfiles(collected_jsfiles_map)

    def get_all_jsfiles(self):
        collected_jsfiles_map = {}
        self.collect_jsfiles(collected_jsfiles_map)
        return collected_jsfiles_map


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

def find_all_jsfiles_in_dir(jsfiles, rootdir, verbose):
    for root, dirs, files in walk(rootdir):
        for filename in files:
            if filename.endswith('.js'):
                filepath = join(root, filename)
                try:
                    jsfile = JsFile(filepath)
                except ValueError, e:
                    if verbose:
                        print str(e)
                else:
                    jsfiles[jsfile.clsname] = jsfile


#def collect_jsfiles_in_installedapps(jsfiles, verbose):
    #for app in settings.INSTALLED_APPS:
        #if not app.startswith('django.'):
            #mod = import_module(app)
            #if exists(mod.__file__) and isdir(dirname(mod.__file__)):
                #moddir = dirname(mod.__file__)
                #find_all_jsfiles_in_dir(jsfiles, moddir, verbose)


class Command(BaseCommand):
    help = 'Create new subject.'
    args = '<appname>'

    def handle(self, *args, **options):
        setup_logging(get_verbosity(options))
        if len(args) != 1:
            raise CommandError('Requires an <appname>.')
        appname = args[0]
        appfile = get_extjs_appfile_from_appname(appname)
        jsfile = AppFile(appfile, appname)
        jsfile.prettyprint()
        jsfile.get_all_jsfiles()

        #extjshelpers_dir =  dirname(import_module('devilry.apps.extjshelpers').__file__)
        #outfile = join(extjshelpers_dir, 'static', 'devilry_all_uncompiled.js')
        #jsfiles = {}
        #collect_jsfiles_in_installedapps(jsfiles, verbose=verbosity>1)
        #ordered = orderJsFiles(jsfiles)
        #open(outfile, 'wb').write('\n\n'.join([j.filecontent for j in ordered]))
