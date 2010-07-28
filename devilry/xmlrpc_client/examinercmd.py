import xmlrpclib
import os
import logging

from assignmenttree import AssignmentSync, Info
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
        AssignmentSync(self.find_rootdir(), self.get_cookiepath(),
                self.get_serverproxy(), self.get_url())


class Feedback(ExaminerCommand):
    name = 'feedback'
    description = 'Submit feedback on a delivery.'
    args_help = '[delivery-dir]'

    def add_options(self):
        help = 'Id of a existing delivery.'
        self.op.add_option("-t", "--feedback-text", metavar="TEXT",
            dest="text", default='', help='Feedback text.')
        self.op.add_option("-g", "--grade", metavar="GRADE",
            dest="grade", default=None, help='Grade.')
        self.op.add_option("-f", "--feedback-format",
            metavar="rst|txt", dest="format",
            default='rst', help='Feedback format.')

    def direrror(self):
        if len(self.args) > 0:
            log.error('The given directory is not a delivery-directory.')
        else:
            log.error('You are not in a delivery-directory.')
        raise SystemExit()

    def command(self):
        self.read_config()

        if len(self.args) > 0:
            path = self.args[0]
        else:
            path = os.getcwd()
        try:
            info = Info.read_open(path, 'Delivery')
        except Info.FileWrongTypeError, e:
            self.direrror()
        except Info.FileDoesNotExistError, e:
            self.direrror()

        grade = self.opt.grade
        if not grade:
            log.error('A grade is required. See --help for more info.')
            raise SystemExit()
        server = self.get_serverproxy()

        # Get feedback text from arguments or file.
        text = self.opt.text
        format = None
        if text:
            log.debug('Feedback found in commandline argument -t.')
            format = self.opt.format
        else:
            filenamebase = os.path.join(path, 'feedback')
            fn = filenamebase + '.rst'
            log.debug('Feedback not found in commandline argument -t. ' \
                    'Trying file feedback.rst.')
            if os.path.isfile(fn):
                log.info('Found feedback in file feedback.rst.')
                text = open(fn, 'rb').read()
                format = 'rst'
            else:
                fn = filenamebase + '.txt'
                log.debug('Did not find feedback in file feedback.rst. ' \
                        'Trying file feedback.txt')
                if os.path.isfile(fn):
                    log.info('Found feedback in file feedback.txt.')
                    text = open(fn, 'rb').read()
                    format = 'txt'
                else:
                    log.info('No feedback text found in commandline ' \
                            'argument -t, feedback.rst or feedback.txt. ' \
                            'Feedback text is empty.')
            if text:
                log.info('Feedback format: %s.' % format)

        try:
            server.set_feedback(info.get_id(), text,
                    format, grade)
        except xmlrpclib.Fault, e:
            log.error('%s' % e.faultString)
        else:
            log.info('Feedback successfully saved.')
