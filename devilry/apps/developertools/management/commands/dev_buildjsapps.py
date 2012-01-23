import logging
from os.path import join, exists, dirname, isdir, relpath, abspath, sep
from os import getcwd, remove
from subprocess import call
from tempfile import mkdtemp
from shutil import rmtree
import json
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.importlib import import_module
from django.core import management


from devilry.utils.command import setup_logging, get_verbosity
import devilry

log = logging.getLogger('buildjsapps')


def get_installed_apps():
    installed_apps = []
    checked = set()
    for app in settings.INSTALLED_APPS:
        if not app.startswith('django.') and not app in checked:
            mod = import_module(app)
            checked.add(app)
            if exists(mod.__file__) and isdir(dirname(mod.__file__)):
                moddir = dirname(mod.__file__)
                installed_apps.append((moddir, mod, mod.__name__.split('.')[-1]))
    return installed_apps

def get_js_apps():
    apps = []
    for moddir, mod, appname in get_installed_apps():
        staticdir = join(moddir, 'static', appname)
        appfile = join(staticdir, 'app.js')
        appdir = join(staticdir, 'app')
        if exists(appfile) and isdir(appdir):
            apps.append((staticdir, appname))
    return apps


class Command(BaseCommand):
    help = 'Build JS apps.'
    option_list = BaseCommand.option_list + (
        make_option('--no-collectstatic',
            action='store_false',
            dest='collectstatic',
            default=True,
            help='Do not run collectstatic before building.'),
        )


    def handle(self, *args, **options):
        self.devenv = join(dirname(dirname(devilry.__file__)), 'devenv')
        if abspath(self.devenv) != abspath(getcwd()):
            raise CommandError('Must be in devenv/')

        setup_logging(get_verbosity(options))
        if options['collectstatic']:
            log.info('Running "collectstatic"')
            management.call_command('collectstatic', verbosity=1, interactive=False)
        else:
            log.info('Skipping "collectstatic"')

        log.debug('Located devenv at: %s', self.devenv)
        for appinfo in get_js_apps():
            self._buildApp(*appinfo)

    def _buildApp(self, staticdir, appname):
        jsbconfig = self._createJsbConfig(appname)
        log.debug('sencha generated JSB config: %s', jsbconfig)
        cleanedJsbConfig = self._cleanJsbConfig(jsbconfig, staticdir)
        log.debug('cleaned JSB config: %s', cleanedJsbConfig)
        self._build(staticdir, cleanedJsbConfig)

    def _createJsbConfig(self, appname):
        url = 'http://localhost:8000/{0}/ui?fakeuser=grandma'.format(appname)
        tempdir = mkdtemp()
        tempfile = join(tempdir, 'app.jsb3')
        cmd = ['sencha', 'create', 'jsb', '-a', url, '-p', tempfile]
        log.debug('Running: %s', ' '.join(cmd))
        call(cmd)
        jsb3 = open(tempfile).read()
        rmtree(tempdir)
        return jsb3

    def _cleanJsbConfig(self, jsbconfig, staticdir):
        config = json.loads(jsbconfig)
        outdir = relpath(staticdir).replace(sep, '/') + '/' # Make sure we have a unix-style path with trailing /
        self._cleanJsbAllClassesSection(config, outdir)
        self._cleanJsbAppAllSection(config, outdir)
        return json.dumps(config, indent=4)

    def _cleanJsbAllClassesSection(self, config, outdir):
        allclasses = config['builds'][0]
        for fileinfo in allclasses['files']:
            path = fileinfo['path']
            if path.startswith('..'):
                fileinfo['path'] = path[2:]
        allclasses['target'] = join(outdir, 'all-classes.js')

    def _cleanJsbAppAllSection(self, config, outdir):
        appall = config['builds'][1]
        appall['target'] = join(outdir, 'app-all.js')
        for fileinfo in appall['files']:
            fileinfo['path'] = outdir


    def _build(self, staticdir, cleanedJsbConfig):
        tempconffile = 'temp-app.jsb3'
        open(tempconffile, 'w').write(cleanedJsbConfig)
        cmd = ['sencha', 'build', '-p', tempconffile, '-d', staticdir]
        log.debug('Running: %s', ' '.join(cmd))
        call(cmd)
        remove(tempconffile)
