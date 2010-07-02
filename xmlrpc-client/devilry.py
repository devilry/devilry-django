#!/usr/bin/env python

import sys
import logging
import getpass
from ConfigParser import ConfigParser
from xmlrpclib import ServerProxy
from optparse import OptionParser
from os.path import exists, join, dirname
from os import mkdir, getcwd
from urlparse import urljoin

from cookie_transport import CookieTransport, SafeCookieTransport
from utils import AssignmentSync



# TODO: make sure SESSION_COOKIE_SECURE is enabled by default or something
#       see: http://docs.djangoproject.com/en/dev/topics/http/sessions/#settings
# TODO: chmod cookies.txt




USER_DISABLED = 1
LOGIN_FAILED = 2
SUCCESSFUL_LOGIN = 3

#host = "https://localhost/django/example/xmlrpc/"
#host = "http://localhost:8000/xmlrpc/"


class Command(object):
    description = None
    name = None
    args_help = '[args]'

    def __init__(self):
        self.config = ConfigParser()
        self._confdir = None
        self.op = OptionParser(usage="usage: %%prog %s [options] %s" % (
                self.name, self.args_help))
        self.op.add_option("-q", "--quiet", action="store_const",
            const=logging.ERROR, dest="loglevel", default=logging.INFO,
            help="Don't show extra information (only errors).")
        self.op.add_option("-d", "--debug", action="store_const",
            const=logging.DEBUG, dest="loglevel",
            help="Show all output, for debugging.")
        self.add_options()
        self.read_config()

    def get_configfile(self):
        return join(self.get_configdir(), 'config.cfg')

    def read_config(self):
        self.config.read([self.get_configfile()])

    def write_config(self):
        self.config.write(open(self.get_configfile(), 'wb'))

    def set_config(self, key, value):
        if not self.config.has_section('settings'):
            self.config.add_section('settings')
        self.config.set('settings', key, value)

    def get_config(self, key):
        return self.config.get('settings', key)

    def get_url(self):
        return self.get_config('url')

    def find_confdir(self):
        path = getcwd()
        while True:
            cdir = join(path, '.devilry')
            if exists(cdir):
                return cdir
            p = dirname(path)
            if p == path:
                break
            path = p
        return None

    def get_configdir(self):
        if self._confdir:
            return self._confdir
        cdir = self.find_confdir()
        if not cdir:
            raise SystemExit('You are not in a Devilry directory tree.')
        self._confdir = cdir
        return cdir

    def cli(self, argv):
        self.opt, self.args = self.op.parse_args(argv)
        logging.basicConfig(level=self.opt.loglevel,
            format="*** %(levelname)s: %(message)s")
        self.command()

    def add_user_option(self):
        self.op.add_option("-u", "--username", metavar="USERNAME",
            dest="username", default=getpass.getuser(),
            help="Username default to current system user (%s)." % getpass.getuser())

    def add_options(self):
        pass

    def command(self):
        pass

    def print_help(self):
        self.op.print_help()

    def exit_help(self):
        self.print_help()
        raise SystemExit()

    def validate_argslen(self, length):
        if len(self.args) != length:
            self.exit_help()

    def get_cookiepath(self):
        return join(self.get_configdir(), 'cookies.txt')

    def get_server(self):
        url = urljoin(self.get_url(), self.urlpath)
        if url.startswith('https'):
            transport=SafeCookieTransport(self.get_cookiepath())
        else:
            transport=CookieTransport(self.get_cookiepath())
        return ServerProxy(url, transport=transport)
    

class Login(Command):
    name = 'login'
    description ='Login to the devilry server.' 
    args_help = '<url>'
    urlpath = '/xmlrpc/'

    def add_options(self):
        self.add_user_option()

    def command(self):
        server = self.get_server()
        password = getpass.getpass('Password: ')
        ret = server.login(self.opt.username, password)
        if ret == SUCCESSFUL_LOGIN:
            logging.info('Login successful')
        else:
            logging.error('Login failed. Reason:')
            if ret == USER_DISABLED:
                print logging.error('Your user is disabled.')
            elif ret == LOGIN_FAILED:
                print logging.error('Invalid username/password.')
            raise SystemExit()


class ListAssignmentGroups(Command):
    name = 'list-assignment-groups'
    description = 'List assignment groups on a given assignment.'
    args_help = '<assignment-id>'
    urlpath = '/xmlrpc_examiner/'

    def command(self):
        self.validate_argslen(1)
        server = self.get_server()
        assignment_id = int(self.args[0])
        groups = server.list_assignmentgroups(assignment_id)
        for group in groups:
            print "%15d : %s (%d deliveries)" % (group['id'],
                    ', '.join(group['students']),
                    group['number_of_deliveries'])


class GetDeliveries(Command):
    name = 'get-deliveries'
    description = 'Get deliveries.'
    urlpath = '/xmlrpc_examiner/'

    def command(self):
        AssignmentSync(self.get_cookiepath(), self.get_server(),
                self.get_url())


class Init(Command):
    name = 'init'
    description = 'Initialize.'
    args_help = '<url>'

    def read_config(self):
        pass

    def command(self):
        if self.find_confdir():
            raise SystemExit(
                    'You are in a existing Devilry directory tree. '\
                    'Initialization aborted.')
        self.validate_argslen(1)

        mkdir('.devilry')
        url = self.args[0]
        self.set_config('url', url)
        self.write_config()


class Cli(object):
    def __init__(self):
        self.commands = []
        self.commands_dict = {}

    def cli(self):
        if len(sys.argv) < 2:
            print 'usage: %s <command>' % sys.argv[0]
            print
            self.print_commands()
            print '   %-10s %s' % ('help', 'Show command help.')
            raise SystemExit()

        command = sys.argv[1]
        if command == 'help':
            if len(sys.argv) != 3:
                print 'usage: %s help <command>' % sys.argv[0]
                print
                self.print_commands()
                raise SystemExit()
            c = self.commands_dict[sys.argv[2]]()
            c.print_help()
        else:
            c = self.commands_dict[command]()
            c.cli(sys.argv[2:])

    def print_commands(self):
        print 'The available commands are:'
        for c in self.commands:
            print '   %-10s %s' % (c.name, c.description)

    def add_command(self, command):
        self.commands.append(command)
        self.commands_dict[command.name] = command



DEFAULT_COMMANDS = (
    Init,
    Login,
    ListAssignmentGroups,
    GetDeliveries,
)

if __name__ == '__main__':
    c = Cli()
    for action in DEFAULT_COMMANDS:
        c.add_command(action)
    c.cli()
