import xmlrpclib
from textwrap import dedent
from os import linesep, getcwd
import logging

from utils import AssignmentSync, Command, log_fault


class ListAssignments(Command):
    name = 'list'
    description = 'List assignments where the authenticated user is examiner.'
    urlpath = '/xmlrpc_examiner/'

    def command(self):
        server = self.get_server()
        try:
            assignments = server.list_active_assignments()
        except xmlrpclib.Fault, e:
            log_fault(e)
        else:
            print 'Active assignments:'
            for assignment in assignments:
                print '* %(path)s' % assignment


class ListAssignmentGroups(Command):
    name = 'list-groups'
    description = 'List assignment groups on a given assignment.'
    args_help = '<assignment-path>'
    urlpath = '/xmlrpc_examiner/'

    def command(self):
        self.validate_argslen(1)
        server = self.get_server()
        assignmentpath = self.args[0]
        try:
            groups = server.list_assignmentgroups(assignmentpath)
        except xmlrpclib.Fault, e:
            log_fault(e)
        else:
            out = [
                "%15d) %-45s (deliveries: %d)" % (
                    group['id'],
                    ', '.join(group['students']),
                    group['number_of_deliveries']
                ) for group in groups]
            out.insert(0, '%15s  %-55s' % ('ID', 'STUDENT(S)'))
            print dedent(linesep.join(out))


class Sync(Command):
    name = 'sync'
    description = 'Sync all deliveries (including all files) where the '\
            'authenticated user is examiner.'
    urlpath = '/xmlrpc_examiner/'

    def command(self):
        AssignmentSync(self.get_configdir(), self.get_cookiepath(),
                self.get_server(), self.get_url())

class Feedback(Command):
    name = 'feedback'
    description = 'Submit feedback on a delivery.'
    args_help = '[delivery-id]'
    urlpath = '/xmlrpc_examiner/'

    def add_options(self):
        help = 'Id of a existing delivery.'
        self.op.add_option("-t", "--feedback-text", metavar="TEXT",
            dest="feedback_text", default='', help='Feedback text.')
        self.op.add_option("-g", "--grade", metavar="GRADE",
            dest="grade", default=None, help='Grade.')
        self.op.add_option("-f", "--feedback-format",
            metavar="restructuredtext|text", dest="feedback_format",
            default='restructuredtext', help='Feedback format.')

    def command(self):
        grade = self.opt.grade
        if not grade:
            raise SystemExit('A grade is required. See --help for more info.')

        if len(self.args) == 0:
            ids = [getcwd()]
        else:
            ids = self.args
        allids = [(idstr, self.determine_id(idstr, 3)) for idstr in ids]

        server = self.get_server()
        for idstr, id in allids:
            try:
                server.set_feedback(id, self.opt.feedback_text,
                        self.opt.feedback_format, grade)
            except xmlrpclib.Fault, e:
                logging.error('Delivery %d: %s' % (id, e.faultString))
