from string import Template
import getpass
from ConfigParser import ConfigParser
import xmlrpclib
from optparse import OptionParser
import os
from urlparse import urljoin
import logging
import logging.handlers
import sys

from cookie_transport import CookieTransport, SafeCookieTransport



log = logging.getLogger('devilry')


def log_fault(fault):
    """ Log a xmlrpclib.Fault to log.error. """
    log.error('%s: %s' % (fault.faultCode, fault.faultString))


def format_long_message(title, msg, always_show_title=True):
    """ Format a message which might be long for logging, to make it clear
    where the message starts and ends.
    
    :return:
        The formatted message, which will be surrounded by markers if
        ``msg`` has more than 200 characters.
    """
    if len(msg) < 200:
        if always_show_title:
            return '%s: %s' % (title, msg)
        else:
            return msg
    else:
        sidelen = (68 - len(title)) / 2
        beforesides = '>'.join(['' for x in xrange(sidelen)])
        aftersides = '<'.join(['' for x in xrange(sidelen)])
        m = []
        m.append('%s %s %s' % (beforesides, title, beforesides))
        m.append(msg)
        m.append('%s %s %s' % (aftersides, title, aftersides))
        return os.linesep.join(m)


class Cli(object):
    def __init__(self, commands=[], extra_help=None):
        """
        :param commands: A list of subclasses of :class:`Command`.
        :param extra_help: Extra help text.
        """
        self.commands = []
        self.commands_dict = {}
        self.set_extra_help(extra_help)
        for command in commands:
            self.add_command(command)

    def cli(self, args=sys.argv):
        """
        Redirect to the command with name matching ``args[1]``. (you add
        commands with :meth:`add_command`). If invalid number of arguments,
        or ``args[1]=='help', show help and raise :exc:`SystemExit`.
        """
        prog = os.path.basename(args[0])
        if len(args) < 2:
            print 'usage: %s <command>' % prog
            print
            self._print_commands()
            print '   %-12s %s' % ('help', 'Show command help.')
            if self._extra_help:
                print
                print Template(self._extra_help).safe_substitute(prog=prog)
            raise SystemExit()

        command = args[1]
        if command == 'help':
            if len(args) != 3:
                print 'usage: %s help <command>' % prog
                print
                self._print_commands()
                raise SystemExit()
            c = self.commands_dict[args[2]]()
            c.exit_help()
        else:
            c = self.commands_dict[command]()
            c.cli(args[2:])

    def set_extra_help(self, extra_help):
        """
        Set extra help text. Use $prog to show the program-name.
        """
        self._extra_help = extra_help

    def _print_commands(self):
        """ Print available commands. """
        print 'The available commands are:'
        for c in self.commands:
            print '   %-12s %s' % (c.name, c.short_info)

    def add_command(self, command):
        """ Add command.
        
        :param command: A subclass of :class:`Command`.
        """
        self.commands.append(command)
        self.commands_dict[command.name] = command



class Command(object):
    """ Base class for all commands in the cli.

    .. attribute:: name

        Name of the argument. Lowercase-only and no spaces. Max 12
        characters. Use ``-`` to improve readablilty on long names.
    
    .. attribute:: short_info

        Short info shown when :class:`Cli` list commands.

    .. attribute:: description

        Description shown in addition to option help and usage.

    .. attribute:: args_help

        Description of arguments in usage. Use ``[arg-description]`` for
        optional arguments and ``<arg-description>`` for required arguments.

    .. attribute:: urlpath

        Path to the xmlrpc used by the command.
    """
    name = None
    short_info = None
    description = None
    args_help = ''
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
                self.name, self.args_help),
                description=(self.description or ''))
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
        
        Raises :exc:`Command.NotInDevilryDirError` if there is no .devilry
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

    def get_logfilepath(self):
        """ Get path to the log-file. """
        return os.path.join(self.get_configdir(), 'everything.log')

    def configure_loghandlers(self, loglevel):
        """ Configure log handling. """
        console = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        console.setFormatter(formatter)
        console.setLevel(loglevel)
        log.addHandler(console)

        # Keep 10mb of complete logs, in files of 1mb
        try:
            logfile = self.get_logfilepath()
        except Command.NotInDevilryDirError:
            pass
        else:
            f = logging.handlers.RotatingFileHandler(logfile,
                    maxBytes=2**20,
                    backupCount=10)
            formatter = logging.Formatter(
                    "%(asctime)s: %(levelname)s: %(message)s")
            f.setFormatter(formatter)
            f.setLevel(logging.DEBUG)
            log.addHandler(f)


    def cli(self, argv):
        """ Start the cli. """
        self.opt, self.args = self.op.parse_args(argv)
        log.setLevel(logging.DEBUG)
        self.configure_loghandlers(self.opt.loglevel)
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
        return xmlrpclib.ServerProxy(url, transport=transport, allow_none=True)



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
    short_info = 'Initialize.'
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
    short_info ='Login to the devilry server.' 
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
        try:
            ret = server.login(self.opt.username, password)
        except xmlrpclib.Fault, e:
            log_fault(e)
            raise SystemExit()
        if ret == self.successful_login:
            log.info('Login successful')
        else:
            log.error('Login failed. Reason:')
            if ret == self.user_disabled:
                log.error('Your user is disabled.')
            elif ret == self.login_failed:
                log.error('Invalid username/password.')
            raise SystemExit()
