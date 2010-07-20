import sys
import os
from cookielib import LWPCookieJar
import urllib2
import logging
from urlparse import urljoin
import re
import xmlrpclib


# TODO: chmod cookies.txt


DATETIME_FORMAT = '%Y.%m.%d_%H-%M-%S'


def id_from_path(path):
    m = re.match(r'.*?_id-(\d+)$', os.path.normpath(path))
    if not m:
        return None
    return int(m.groups(1)[0])

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
        if os.path.isfile(cookiepath):
            cj.load(cookiepath)
        self.urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        for assignment in server.list_active_assignments():
            assignmentdir = assignment['path']
            self.assignment(assignment, assignmentdir)

            for group in server.list_assignmentgroups(assignment['path']):
                groupname = "%s_id-%d" % ('-'.join(group['students']),
                        group['id'])
                groupdir = os.path.join(assignmentdir, groupname)
                self.assignmentgroup(group, groupdir)

                for delivery in server.list_deliveries(group['id']):
                    print(delivery['time_of_delivery'])
                    time_of_delivery = delivery['time_of_delivery'].strftime(
                            DATETIME_FORMAT)
                    deliveryname = "%s_id-%d" % (time_of_delivery,
                            delivery['id'])
                    deliverydir = os.path.join(groupdir, deliveryname)
                    filesdir = os.path.join(deliverydir, 'files')
                    self.delivery(delivery, deliverydir, filesdir)

                    for filemeta in delivery['filemetas']:
                        filepath = os.path.join(filesdir, filemeta['filename'])
                        self.filemeta(filemeta, deliverydir, filepath)

                    try:
                        feedback = server.get_feedback(delivery['id'])
                    except xmlrpclib.Fault, e:
                        if e.faultCode == 404:
                            self.feedback_new(delivery, deliverydir)
                        else:
                            raise
                    else:
                        self.feedback_exists(delivery, deliverydir, feedback)



    def assignment(self, assignment, assignmentdir):
        if os.path.isdir(assignmentdir):
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
        elif os.path.isdir(groupdir):
            self.assignmentgroup_exists(group, groupdir)
        else:
            self.assignmentgroup_new(group, groupdir)

    def assignmentgroup_nodeliveries(self, group, groupdir):
        pass
    def assignmentgroup_new(self, group, groupdir):
        pass
    def assignmentgroup_exists(self, group, groupdir):
        pass

    def delivery(self, delivery, deliverydir, filesdir):
        if os.path.isdir(deliverydir):
            self.delivery_exists(delivery, deliverydir, filesdir)
        else:
            self.delivery_new(delivery, deliverydir, filesdir)

    def delivery_new(self, delivery, deliverydir, filesdir):
        pass
    def delivery_exists(self, delivery, deliverydir, filesdir):
        pass

    def filemeta(self, filemeta, deliverydir, filepath):
        if os.path.isfile(filepath):
            self.filemeta_exists(filemeta, deliverydir, filepath)
        else:
            self.filemeta_new(filemeta, deliverydir, filepath)

    def filemeta_new(self, filemeta, deliverydir, filepath):
        pass
    def filemeta_exists(self, filemeta, deliverydir, filepath):
        pass

    def feedback_new(self, delivery, deliverydir):
        pass
    def feedback_exists(self, delivery, deliverydir, feedback):
        pass


class AssignmentSync(AssignmentTreeWalker):
    """
    Uses :class:`AssignmentTreeWalker` to sync all deliveries on any
    active assignment where the current user is examiner to the filesystem.
    """
    bufsize = 65536


    def __init__(self, rootdir, cookiepath, server, serverurl):
        cwd = os.getcwd()
        os.chdir(rootdir)
        try:
            super(AssignmentSync, self).__init__(cookiepath, server,
                    serverurl)
        finally:
            os.chdir(cwd)

    def assignment(self, assignment, assignmentdir):
        super(AssignmentSync, self).assignment(assignment, assignmentdir)
        if not assignment['xmlrpc_conf']:
            logging.warning('%s does not support creating feedback using ' \
                    'the command-line' % assignment['path'])

    def assignment_new(self, assignment, assignmentdir):
        logging.info('+ %s' % assignmentdir)
        os.makedirs(assignmentdir)

    def assignment_exists(self, assignment, assignmentdir):
        logging.debug('%s already os.path.exists' % assignmentdir)

    def assignmentgroup_nodeliveries(self, group, groupdir):
        logging.warning('Group "%s" has no deliveries' %
                groupdir)

    def assignmentgroup_new(self, group, groupdir):
        logging.info('+ %s' % groupdir)
        os.makedirs(groupdir)

    def assignmentgroup_exists(self, group, groupdir):
        logging.debug('%s already os.path.exists' % groupdir)

    def delivery_new(self, delivery, deliverydir, filesdir):
        logging.info('+ %s' % deliverydir)
        os.makedirs(filesdir)

    def delivery_exists(self, delivery, deliverydir, filesdir):
        logging.debug('%s already os.path.exists' % deliverydir)

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
            if len(out) == 0:
                break
            output.write(out)
        input.close()
        output.close()

    def filemeta_exists(self, filemeta, deliverydir, filepath):
        logging.debug('%s already os.path.exists' % filepath)

    def feedback_new(self, delivery, deliverydir):
        pass

    def feedback_exists(self, delivery, deliverydir, feedback):
        if feedback['format'] == 'restructuredtext':
            ext = 'rst'
        else:
            ext = 'txt'
        feedbackfile = os.path.join(deliverydir, 'feedback.server.%s' % ext)
        open(feedbackfile, 'wb').write(feedback['text'])


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
