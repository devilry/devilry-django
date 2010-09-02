import os
from subprocess import call
import logging

class SystemCallError(Exception):
    pass


def systemcall(cmd):
    """ Like os.system, but with good error handling. """
    logging.info("Running: %(cmd)s" % vars())
    try:
        retcode = call(cmd, shell=True)
        if retcode < 0:
            raise SystemCallError(
                    "'%(cmd)s' was terminated by signal -%(retcode)s" % vars())
        elif retcode > 0:
            raise SystemCallError(
                    "'%(cmd)s' returned error code: %(retcode)s" % vars())
    except OSError, e:
        raise SystemCallError(
                "Excecution of %(cmd)s failed: %(e)s" % vars())

def add_quiet_opt(optparser):
    optparser.add_option("-q", "--quiet", action="store_const",
        const=logging.ERROR, dest="loglevel",
        help="Don't show extra information (only errors).")

def add_debug_opt(optparser):
    optparser.add_option("-d", "--debug", action="store_const",
        const=logging.DEBUG, dest="loglevel",
        help="Show all output.")

def add_settings_option(optparser):
    default_settings = os.environ.get("DJANGO_SETTINGS_MODULE",
            'devilry.settings') 
    optparser.add_option("--settings", dest="settings",
            default=default_settings,
            help='Django settings file. Defaults to the value of the '\
                'DJANGO_SETTINGS_MODULE environment variable, or '\
                '"devilry.settings" if DJANGO_SETTINGS_MODULE is unset.',
                metavar=default_settings)

def set_django_settings_module(opt):
    os.environ['DJANGO_SETTINGS_MODULE'] = opt.settings

def setup_logging(opt):
    logging.basicConfig(level=opt.loglevel or logging.INFO, format='%(levelname)s: %(message)s')

def load_devilry_plugins():
    from devilry.core import pluginloader
    pluginloader.autodiscover()
