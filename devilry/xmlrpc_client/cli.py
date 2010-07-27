import getpass
from ConfigParser import ConfigParser
from xmlrpclib import ServerProxy
from optparse import OptionParser
import os
from urlparse import urljoin
import logging
import sys

from cookie_transport import CookieTransport, SafeCookieTransport
from assignmenttree import Info



log = logging.getLogger('devilry')


def log_fault(fault):
    """ Log a xmlrpclib.Fault to log.error. """
    log.error('%s: %s' % (fault.faultCode, fault.faultString))



class Cli(object):
    def __init__(self):
        self.commands = []
        self.commands_dict = {}

    def cli(self, args=sys.argv):
        """
        Redirect to the command with name matching ``args[1]``. (you add
        commands with :meth:`add_command`). If invalid number of arguments,
        or ``args[1]=='help', show help and raise :exc:`SystemExit`.
        """
        if len(args) < 2:
            print 'usage: %s <command>' % args[0]
            print
            self.print_commands()
            print '   %-10s %s' % ('help', 'Show command help.')
            raise SystemExit()

        command = args[1]
        if command == 'help':
            if len(args) != 3:
                print 'usage: %s help <command>' % args[0]
                print
                self.print_commands()
                raise SystemExit()
            c = self.commands_dict[args[2]]()
            c.print_help()
        else:
            c = self.commands_dict[command]()
            c.cli(args[2:])

    def print_commands(self):
        """ Print available commands. """
        print 'The available commands are:'
        for c in self.commands:
            print '   %-10s %s' % (c.name, c.description)

    def add_command(self, command):
        """ Add command.
        
        :param command: A subclass of :class:`Command`.
        """
        self.commands.append(command)
        self.commands_dict[command.name] = command



class Command(object):
    """ Base class for all commands in the cli. """
    description = None
    name = None
    args_help = '[args]'
    urlpath = '/xmlrpc/'


    class NotInDevilryDirError(Exception):
        """
        Raised when searching the current working directory and it's parents
        for a subdirectory named ``".devilry"``  fails.
        """

    def __init__(self):
        self.config = ConfigParser()
        self._rootdir = None
        self.op = OptionParser(usage="usage: %%prog %s [options] %s" % (
                self.name, self.args_help))
        self.op.add_option("-q", "--quiet", action="store_const",
            const=logging.ERROR, dest="loglevel", default=logging.INFO,
            help="Don't show extra information (only errors).")
        self.op.add_option("--debug", action="store_const",
            const=logging.DEBUG, dest="loglevel",
            help="Show all output, for debugging.")
        self.add_options()

    def read_config(self):
        self.config.read([self.get_configfile()])

    def get_configfile(self):
        """
        Uses :meth:`get_configdir` to find config.cfg in the configdir.
        """
        return os.path.join(self.get_configdir(), 'config.cfg')


    def write_config(self):
        """ Update the configfile on disk. """
        self.config.write(open(self.get_configfile(), 'wb'))

    def set_config(self, key, value):
        """ Set a config value. """
        if not self.config.has_section('settings'):
            self.config.add_section('settings')
        self.config.set('settings', key, value)

    def get_config(self, key):
        """ Get a config value. """
        return self.config.get('settings', key)

    def get_url(self):
        """ Get server url from config-file. """
        return self.get_config('url')

    def find_rootdir(self, path=None):
        """
        Find the first parent-directory of ``path`` containing a
        directory named ``".devilry"``.
        
        Raises :ecx:`Command.NotInDevilryDirError` if there is no .devilry
        directory within any of the parent-directories of ``path``.

        :param path: Defaults to current working directory.
        :return: The path to the rootdir.
        """
        path = path or os.getcwd()
        while True:
            cdir = os.path.join(path, '.devilry')
            if os.path.exists(cdir):
                return path
            p = os.path.dirname(path)
            if p == path:
                break
            path = p
        raise Command.NotInDevilryDirError()

    def get_configdir(self):
        """ Get the config-directory (the .devilry directory). """
        return os.path.join(self.find_rootdir(), '.devilry')

    def get_cookiepath(self):
        """ The cli uses cookies to maintain a session. The cookie-file is
        stored in the configdir. This method returns the path to the cookie
        file. """
        return os.path.join(self.get_configdir(), 'cookies.txt')

    def get_info(self, dirpath, typename):
        """ Get id from the file name ``idfilename`` in the
        ``dirpath``-directory.
        
        Raises :exc:`IdFileNotFoundError` if the file cannot be found.

        Raises :exc:`ValueError` if the contents of the id-file can not be
        converted to int.
        """
        return Info.read_open(dirpath, typename)

    def configure_loghandlers(self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter("*** %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        log.addHandler(handler)

    def cli(self, argv):
        """ Start the cli. """
        self.opt, self.args = self.op.parse_args(argv)
        log.setLevel(self.opt.loglevel)
        self.configure_loghandlers()
        self.command()

    def add_user_option(self):
        """ Add a option for providing username using -u or --username. The
        optparse dest is ``"username"``. """
        self.op.add_option("-u", "--username", metavar="USERNAME",
            dest="username", default=getpass.getuser(),
            help="Username default to current system user (%s)." % \
                    getpass.getuser())

    def add_options(self):
        """ Override to add options to the optionparser. Does nothing by
        default. """
        pass

    def command(self):
        """ Override to and put the code for the command here. Does nothing by
        default. """
        pass

    def exit_help(self):
        """ Show help and exit. """
        self.op.print_help()
        raise SystemExit()

    def validate_argslen(self, length):
        """ Validate the length of :attr:`args`, and call :meth:`exit_help`
        if the validation fails. """
        if len(self.args) != length:
            self.exit_help()

    def get_serverproxy(self):
        """ Get a server-proxy object. If the url starts with https, a
        server-proxy with SSL-support is created. """
        url = urljoin(self.get_url(), self.urlpath)
        if url.startswith('https'):
            transport=SafeCookieTransport(self.get_cookiepath())
        else:
            transport=CookieTransport(self.get_cookiepath())
        return ServerProxy(url, transport=transport)



class CommandUsingConfig(Command):
    """ Use this as a base for commands which needs to set or get
    configuration values.

    Extends the __init__ method of :class:`Command` with a call to
    :meth:`Command.read_config`. """
    def __init__(self, *args, **kwargs):
        super(CommandUsingConfig, self).__init__(*args, **kwargs)
        self.read_config()


############################################################################
# Some commonly used commands
############################################################################


class Init(Command):
    """
    Init command.
    """
    name = 'init'
    description = 'Initialize.'
    args_help = '<url>'

    def command(self):
        try:
            self.find_rootdir()
        except Command.NotInDevilryDirError:
            pass
        else:
            raise SystemExit(
                    'You are in a existing Devilry directory tree. '\
                    'Initialization aborted.')
        self.validate_argslen(1)
        url = self.args[0]
        os.mkdir('.devilry')
        self.set_config('url', url)
        self.write_config()


class Login(CommandUsingConfig):
    """ Login command. """
    name = 'login'
    description ='Login to the devilry server.' 
    args_help = ''
    urlpath = '/xmlrpc/'

    user_disabled = 1
    login_failed = 2
    successful_login = 3

    def add_options(self):
        self.add_user_option()

    def get_password(self):
        return getpass.getpass('Password: ')

    def command(self):
        server = self.get_serverproxy()
        password = self.get_password()
        ret = server.login(self.opt.username, password)
        if ret == self.successful_login:
            log.info('Login successful')
        else:
            log.error('Login failed. Reason:')
            if ret == self.user_disabled:
                log.error('Your user is disabled.')
            elif ret == self.login_failed:
                log.error('Invalid username/password.')
            raise SystemExit()
