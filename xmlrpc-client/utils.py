import sys
from os import makedirs, getcwd
from os.path import isfile, isdir, join, exists, dirname
from cookielib import LWPCookieJar
import urllib2
import logging
from urlparse import urljoin
import getpass
from ConfigParser import ConfigParser
from xmlrpclib import ServerProxy
from optparse import OptionParser

from cookie_transport import CookieTransport, SafeCookieTransport

# TODO: chmod cookies.txt


DATETIME_FORMAT = '%Y-%m-%d_%H:%M:%S'


def log_fault(fault):
    """ Log a xmlrpclib.Fault to logging.error. """
    logging.error('%s: %s' % (fault.faultCode, fault.faultString))

class AssignmentTreeWalker(object):
    """ Finds all assignment where the current user is examiner, and walks
    through every AssignmentGroup, Delivery and FileMeta calling
    :meth:`assignment`, :meth:`assignmentgroup`, :meth:`delivery` and
    :meth:`filemeta`.
    """
    def __init__(self, cookiepath, server, serverurl):
        self.cookiepath = cookiepath
        self.server = server
        self.serverurl = serverurl
        cj = LWPCookieJar()
        if isfile(cookiepath):
            cj.load(cookiepath)
        self.urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        for assignment in server.list_active_assignments():
            assignmentdir = assignment['path']
            self.assignment(assignment, assignmentdir)

            for group in server.list_assignmentgroups(assignment['path']):
                groupname = "%s_id-%d" % ('-'.join(group['students']),
                        group['id'])
                groupdir = join(assignmentdir, groupname)
                self.assignmentgroup(group, groupdir)

                for delivery in server.list_deliveries(group['id']):
                    time_of_delivery = delivery['time_of_delivery'].strftime(
                            DATETIME_FORMAT)
                    deliveryname = "%s_id-%d" % (time_of_delivery,
                            delivery['id'])
                    deliverydir = join(groupdir, deliveryname)
                    self.delivery(delivery, deliverydir)

                    for filemeta in delivery['filemetas']:
                        filepath = join(deliverydir, filemeta['filename'])
                        self.filemeta(filemeta, deliverydir, filepath)


    def assignment(self, assignment, assignmentdir):
        if isdir(assignmentdir):
            self.assignment_exists(assignment, assignmentdir)
        else:
            self.assignment_new(assignment, assignmentdir)

    def assignment_new(self, assignment, assignmentdir):
        pass
    def assignment_exists(self, assignment, assignmentdir):
        pass

    def assignmentgroup(self, group, groupdir):
        number_of_deliveries = group['number_of_deliveries']
        if number_of_deliveries == 0:
            self.assignmentgroup_nodeliveries(group, groupdir)
        elif isdir(groupdir):
            self.assignmentgroup_exists(group, groupdir)
        else:
            self.assignmentgroup_new(group, groupdir)

    def assignmentgroup_nodeliveries(self, group, groupdir):
        pass
    def assignmentgroup_new(self, group, groupdir):
        pass
    def assignmentgroup_exists(self, group, groupdir):
        pass

    def delivery(self, delivery, deliverydir):
        if isdir(deliverydir):
            self.delivery_exists(delivery, deliverydir)
        else:
            self.delivery_new(delivery, deliverydir)

    def delivery_new(self, delivery, deliverydir):
        pass
    def delivery_exists(self, delivery, deliverydir):
        pass

    def filemeta(self, filemeta, deliverydir, filepath):
        if isfile(filepath):
            self.filemeta_exists(filemeta, deliverydir, filepath)
        else:
            self.filemeta_new(filemeta, deliverydir, filepath)

    def filemeta_new(self, filemeta, deliverydir, filepath):
        pass
    def filemeta_exists(self, filemeta, deliverydir, filepath):
        pass



class AssignmentSync(AssignmentTreeWalker):
    """
    Uses :class:`AssignmentTreeWalker` to sync all deliveries on any
    active assignment where the current uses is examiner into the current
    filesystem-directory.
    """
    bufsize = 65536

    def assignment_new(self, assignment, assignmentdir):
        logging.info('+ %s' % assignmentdir)
        makedirs(assignmentdir)

    def assignment_exists(self, assignment, assignmentdir):
        logging.debug('%s already exists' % assignmentdir)

    def assignmentgroup_nodeliveries(self, group, groupdir):
        logging.warning('Group "%s" has no deliveries' %
                groupdir)

    def assignmentgroup_new(self, group, groupdir):
        logging.info('+ %s' % groupdir)
        makedirs(groupdir)

    def assignmentgroup_exists(self, group, groupdir):
        logging.debug('%s already exists' % groupdir)

    def delivery_new(self, delivery, deliverydir):
        logging.info('+ %s' % deliverydir)
        makedirs(deliverydir)

    def delivery_exists(self, delivery, deliverydir):
        logging.debug('%s already exists' % deliverydir)

    def filemeta_new(self, filemeta, deliverydir, filepath):
        logging.info('+ %s' % filepath)
        url = urljoin(self.serverurl,
            "/ui/download-file/%s" % filemeta['id'])
        logging.debug('Downloading file: %s' % url)
        size = filemeta['size']
        left_bytes = size
        input = self.urlopener.open(url)
        output = open(filepath, 'wb')
        while left_bytes > 0:
            out = input.read(self.bufsize)
            left_bytes -= len(out)
            output.write(out)
        input.close()
        output.close()

    def filemeta_exists(self, filemeta, deliverydir, filepath):
        logging.debug('%s already exists' % filepath)


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
