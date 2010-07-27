import xmlrpclib
from textwrap import dedent
from os import linesep, getcwd
import logging

from assignmenttree import AssignmentSync
from cli import Command, log_fault



log = logging.getLogger('devilry')


class ExaminerCommand(Command):
    """ Base class for all examiner commands. """
    urlpath = '/xmlrpc_examiner/'


class ListAssignments(ExaminerCommand):
    name = 'list'
    description = 'List assignments where the authenticated user is examiner.'

    def command(self):
        self.read_config()
        server = self.get_serverproxy()
        try:
            assignments = server.list_active_assignments()
        except xmlrpclib.Fault, e:
            log_fault(e)
        else:
            log.info('Active assignments:')
            for assignment in assignments:
                log.info('* %(path)s' % assignment)


class ListAssignmentGroups(ExaminerCommand):
    name = 'list-groups'
    description = 'List assignment groups on a given assignment.'
    args_help = '<assignment-path>'

    def command(self):
        self.validate_argslen(1)
        self.read_config()
        server = self.get_serverproxy()
        assignmentpath = self.args[0]
        try:
            groups = server.list_assignmentgroups(assignmentpath)
        except xmlrpclib.Fault, e:
            log_fault(e)
        else:
            log.info('%16s  %s' % ('ID', 'STUDENT(S)'))
            for group in groups:
                groupinfo = "%15d)  %-45s (deliveries: %d)" % (
                    group['id'],
                    ', '.join(group['students']),
                    group['number_of_deliveries'])
                log.info(groupinfo)


class Sync(ExaminerCommand):
    name = 'sync'
    description = 'Sync all deliveries (including all files) where the '\
            'authenticated user is examiner.'

    def command(self):
        self.read_config()
        AssignmentSync(self.get_configdir(), self.get_cookiepath(),
                self.get_serverproxy(), self.get_url())


class Feedback(ExaminerCommand):
    name = 'feedback'
    description = 'Submit feedback on a delivery.'
    args_help = '[delivery-id]'

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
        self.read_config()
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
                log.error('Delivery %d: %s' % (id, e.faultString))
            else:
                log.info('Added feedback to: %s' % idstr)
