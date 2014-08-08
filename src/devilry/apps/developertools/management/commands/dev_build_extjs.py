from __future__ import print_function
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

def classpath_to_ospath(unixpath):
    from os import sep
    return unixpath.replace('.', sep) + '.js'


class SimpleJsFile(object):
    MULTILINE_COMMENT_PATT = re.compile('\/\*.*?\*\/', re.MULTILINE|re.DOTALL)
    SINGLELINE_COMMENT_PATT = re.compile('\/\/.*?$', re.MULTILINE)

    def __init__(self, classname, filepath):
        self.classname = classname
        self.filepath = filepath
        filecontent = open(self.filepath, 'rb').read()
        self.filecontent = self.remove_comments(filecontent)
        self.requires = []

    def remove_comments(self, filecontent):
        filecontent = self.MULTILINE_COMMENT_PATT.sub('', filecontent)
        #filecontent = self.SINGLELINE_COMMENT_PATT.sub('', filecontent)
        return filecontent

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
    LISTMIXINSPATT = re.compile(r"^\s*mixins\s*:\s*[(.*?)]", re.MULTILINE|re.DOTALL)
    OBJECTMIXINSPATT = re.compile(r"^\s*mixins\s*:\s*{(.*?)}", re.MULTILINE|re.DOTALL)
    LISTSPLITPATT = re.compile(r'[\'"](.*?)[\'"]')
    STRINGOBJECT_VALUES_PATT = re.compile(r'[\'"]?.*?[\'"]?\s*:\s*[\'"](.*?)[\'"]')
    CONTROLLERS_PATT = re.compile(r"^\s*controllers\s*:\s*\[(.*?)\]", re.MULTILINE|re.DOTALL)
    VIEWS_PATT = re.compile(r"^\s*views\s*:\s*\[(.*?)\]", re.MULTILINE|re.DOTALL)
    MODELS_PATT = re.compile(r"^\s*models\s*:\s*\[(.*?)\]", re.MULTILINE|re.DOTALL)
    STORES_PATT = re.compile(r"^\s*stores\s*:\s*\[(.*?)\]", re.MULTILINE|re.DOTALL)
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

    #: Places where ExtJS put files in the Ext.* namespace.
    #: Relative to the root of the ExtJS sources
    EXTJS_CLASSPATH = ('src',
                       join('src', 'core', 'src'),
                       join('src', 'core', 'src', 'lang'))


    def __init__(self, classname, filepath):
        super(JsFile, self).__init__(classname, filepath)
        self.appname = self.get_appname()
        self.extend = None
        self.parse()

    def get_appname(self):
        return get_appname_from_classpath(self.classname)

    def parse(self):
        self.match_define()
        self.match_requires() # must be before extend and mixins, since they add to self.requires
        self.match_extend()
        self.match_mixins()
        self.match_model()
        #self.requires = filter(lambda r: not r.startswith('Ext.'), self.requires)
        if self.is_controller():
            self.match_controllers()
            self.match_models()
            self.match_stores()
            self.match_views()

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
        m = self.LISTMIXINSPATT.search(self.filecontent)
        if m:
            mixinsstr = m.groups()[0]
            self.mixins = self.LISTSPLITPATT.findall(mixinsstr)
            self.requires += self.mixins
        else:
            m = self.OBJECTMIXINSPATT.search(self.filecontent)
            if m:
                mixinsstr = m.groups()[0]
                self.mixins = self.STRINGOBJECT_VALUES_PATT.findall(mixinsstr)
                self.requires += self.mixins
            else:
                self.mixins = []

    def match_model(self):
        m = self.MODELPATT.search(self.filecontent)
        if m:
            model = m.groups()[0]
            self.requires.append(model)

    def get_classname_for_internalname(self, context, name):
        return '{0}.{1}.{2}'.format(self.appname, context, name)

    def merge_internalnames_with_requires(self, context, internalnames):
        classnames = [self.get_classname_for_internalname(context, name)
                      for name in internalnames]
        self.requires += classnames

    def match_controllers(self):
        m = self.CONTROLLERS_PATT.search(self.filecontent)
        if m:
            controllersstr = m.groups()[0]
            self.controllers = self.LISTSPLITPATT.findall(controllersstr)
            self.merge_internalnames_with_requires('controller', self.controllers)
        else:
            self.controllers = []

    def match_views(self):
        m = self.VIEWS_PATT.search(self.filecontent)
        if m:
            viewsstr = m.groups()[0]
            self.views = self.LISTSPLITPATT.findall(viewsstr)
            pprint(self.views)
            self.merge_internalnames_with_requires('view', self.views)
        else:
            self.views = []

    def match_models(self):
        m = self.MODELS_PATT.search(self.filecontent)
        if m:
            modelsstr = m.groups()[0]
            self.models = self.LISTSPLITPATT.findall(modelsstr)
            self.merge_internalnames_with_requires('model', self.models)
        else:
            self.models = []

    def match_stores(self):
        m = self.STORES_PATT.search(self.filecontent)
        if m:
            storesstr = m.groups()[0]
            self.stores = self.LISTSPLITPATT.findall(storesstr)
            self.merge_internalnames_with_requires('store', self.stores)
        else:
            self.stores = []

    def create_jsfile_for_extjsclass(self, classname):
        """
        ``create_jsfile_for_class``, but with all of the hacks required to
        handle finding stuff in the extjs sources.
        """
        if classname in self.EXTJS_ALTERNATE_NAMES:
            return self.create_jsfile_for_extjsclass(self.EXTJS_ALTERNATE_NAMES[classname])
        from os import sep
        appdir = get_staticdir_from_appname('extjs4')
        relativepath = sep.join(classname.split('.')[1:]) + '.js'
        app_path = None
        for dirname in self.EXTJS_CLASSPATH:
            path = join(appdir, dirname, relativepath)
            if exists(path):
                app_path = path
                break
        if not app_path:
            raise ValueError('Could not find any file for: {0}'.format(classname))
        try:
            return JsFile(classname, app_path)
        except ValueError:
            return SimpleJsFile(classname, app_path)

    def create_jsfile_for_class(self, classname):
        django_appname = get_appname_from_classpath(classname)
        if django_appname == 'extjs4':
            return self.create_jsfile_for_extjsclass(classname)
        from os import sep
        appdir = get_extjs_sourceroot_from_appname(django_appname)
        relativepath = sep.join(classname.split('.')[1:]) + '.js'
        app_path = join(appdir, relativepath)
        return JsFile(classname, app_path)


    def __str__(self):
        return "{0}: {1} ({2})".format(self.clsname, self.extend, ','.join(self.requires))

    def is_controller(self):
        return self.extend == 'Ext.app.Controller'

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
        if self.is_controller():
            print('## Controllers:')
            pprint(self.controllers)
            print('## Models:')
            pprint(self.models)
            print('## Stores:')
            pprint(self.stores)
            print('## Views:')
            pprint(self.views)

    def collect_jsfiles(self, collected_jsfiles_map):
        logging.debug('Collecting deps of {0}'.format(self.filepath))
        for classname in self.requires:
            jsfile = self.create_jsfile_for_class(classname)
            if not jsfile.classname in collected_jsfiles_map:
                collected_jsfiles_map[jsfile.classname] = jsfile
                jsfile.collect_jsfiles(collected_jsfiles_map)


class AppFile(JsFile):
    def __init__(self, appfile, appname):
        self.appname = appname
        super(AppFile, self).__init__(classname=None,
                                      filepath=appfile)

    def match_define(self):
        pass

    def get_appname(self):
        return self.appname

    def __str__(self):
        return "APP {appname}".format(**self.__dict__)

    def collect_appjsfiles(self, collected_jsfiles_map, context, names,
                           create_class=lambda classname, filepath: JsFile(classname, filepath)):
        for name in names:
            filepath = join(self.appdir, context, classpath_to_ospath(name))
            classname = self.get_classname_for_internalname(context, name)
            if not classname in collected_jsfiles_map:
                jsfile = create_class(classname, filepath)
                collected_jsfiles_map[jsfile.classname] = jsfile
                jsfile.collect_jsfiles(collected_jsfiles_map)

    #def collect_jsfiles(self, collected_jsfiles_map):
        #super(AppFile, self).collect_jsfiles(collected_jsfiles_map)
        #self.collect_appjsfiles(collected_jsfiles_map, 'controller', self.controllers,
                                #lambda classname, filepath: ControllerFile(classname, filepath, self.appname))
        #self.collect_appjsfiles(collected_jsfiles_map, 'models', self.models)
        #self.collect_appjsfiles(collected_jsfiles_map, 'stores', self.stores)
        #self.collect_appjsfiles(collected_jsfiles_map, 'views', self.views)

    def get_all_jsfiles(self):
        collected_jsfiles_map = {}
        self.collect_jsfiles(collected_jsfiles_map)
        return collected_jsfiles_map


def depsfullfilled(jsfile, jsfiles):
    for reqclass in jsfile.requires:
        if reqclass in jsfiles:
            return False
    return True


def orderJsFiles(jsfiles):
    ordered = []
    remaining = -1
    while jsfiles:
        for clsname in jsfiles.keys():
            jsfile = jsfiles[clsname]
            if depsfullfilled(jsfile, jsfiles):
                ordered.append(jsfile)
                del jsfiles[clsname]
        last_remaining = remaining
        remaining = len(jsfiles)
        if remaining == last_remaining:
            print('######################################################################')
            print('Can not fulfill all dependencies')
            print('######################################################################')
            for jsfile in jsfiles.itervalues():
                print('## ', jsfile.classname, ' requires:')
                for reqclass in jsfile.requires:
                    if reqclass in jsfiles:
                        print('- ', reqclass)
                print('')
            raise CommandError('ABORTING (see output above)')
    return ordered

#def find_all_jsfiles_in_dir(jsfiles, rootdir, verbose):
    #for root, dirs, files in walk(rootdir):
        #for filename in files:
            #if filename.endswith('.js'):
                #filepath = join(root, filename)
                #try:
                    #jsfile = JsFile(filepath)
                #except ValueError, e:
                    #if verbose:
                        #print str(e)
                #else:
                    #jsfiles[jsfile.clsname] = jsfile


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
        appdir = get_staticdir_from_appname(appname)
        appfile = join(appdir, 'app.js')

        jsfile = AppFile(appfile, appname)
        #jsfile.prettyprint()
        jsfiles = jsfile.get_all_jsfiles()
        ordered = orderJsFiles(jsfiles)

        outfile = join(appdir, 'app-all.js')
        content = '\n\n'.join([j.filecontent for j in ordered])
        content += '\n\n' + jsfile.filecontent
        open(outfile, 'wb').write(content)
