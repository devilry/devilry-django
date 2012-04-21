import logging
from subprocess import call
from os import walk
from os.path import exists, join, abspath
import webbrowser
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from devilry.utils.command import setup_logging, get_verbosity
from devilry.utils.importutils import get_installed_apps, get_staticdir_from_appname

logger = logging.getLogger(__name__)


def find_javascriptfiles():
    jsfiles = []
    extjssources = abspath(join(get_staticdir_from_appname('extjshelpers'), 'extjs'))
    jasminesources = abspath(join(get_staticdir_from_appname('jsapp'), 'jasmine'))
    for appdir, module, appname in get_installed_apps():
        for root, dirs, files in walk(join(appdir, 'static')):
            if extjssources in abspath(root): # Skip extjs
                continue
            if jasminesources in abspath(root): # Skip jasmine sources
                continue
            if 'jasminespecs' in root: # Skip jasmine tests
                continue
            for filename in files:
                if filename in ('all-classes.js', 'app-all.js'): # Skip compiled apps
                    continue
                if filename.endswith('.js'):
                    filepath = join(root, filename)
                    jsfiles.append(filepath)
    return jsfiles


class Command(BaseCommand):
    help = 'Create a database of static data for demo purposes.'
    args = '<outdir>'
    option_list = BaseCommand.option_list + (
        make_option('-b', '--openbrowser',
                    dest='openbrowser',
                    action='store_true',
                    default=False,
                    help='Open the docs in your default browser after building.'),
        make_option('--install-help',
                    dest='installhelp',
                    action='store_true',
                    default=False,
                    help='Print JSDUCK install help and exit (do not build docs). Does not require <outdir>.'),
    )

    def handle(self, *args, **options):
        verbosity = get_verbosity(options)
        setup_logging(verbosity)

        installhelp = options['installhelp']
        if installhelp:
            self.print_install_help()
            return

        if len(args) != 1:
            raise CommandError('<outdir> is required.')
        outdir = args[0]
        openbrowser = options['openbrowser']

        if not exists(outdir):
            raise CommandError('<outdir> {0} does not exist'.format(outdir))

        self.build(outdir, openbrowser)

    def build(self, outdir, openbrowser):
        infiles = find_javascriptfiles()
        retcode = call(['jsduck', '--verbose', '--output', outdir] + infiles)

        print
        if retcode == 0:
            indexpath = join(outdir, 'index.html')
            print '********************************************************************'
            print "JavaScript docs build successfully. You can view it here:"
            print
            print '   ', indexpath
            print
            print '********************************************************************'
            if openbrowser:
                print 'Opening in browser'
                webbrowser.open_new_tab('file:///' + indexpath)
        else:
            CommandError("JSDuck exited with error code {}.".format(retcode))

    def print_install_help(self):
        print """
Requires JSDuck: https://github.com/nene/jsduck

Make sure you install with (notice --pre):

    $ [sudo] gem install --pre jsduck

To get the latest version of jsduck. If you get docs with the same look and
feel as the official ExtJS docs, you have the correct version of JSDuck.
        """
