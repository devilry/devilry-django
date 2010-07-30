import xmlrpclib
import os
import logging

from assignmenttree import AssignmentSync, Info, overwriteable_filename, \
    overwrite
from cli import Command, log_fault, format_long_message


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
            deliverydir = os.path.abspath(os.path.normpath(self.args[0]))
        else:
            deliverydir = os.path.abspath(os.getcwd())
        try:
            info = Info.read_open(deliverydir, 'Delivery')
        except Info.FileWrongTypeError, e:
            self.direrror()
        except Info.FileDoesNotExistError, e:
            self.direrror()

        groupdir = os.path.dirname(deliverydir)
        assignmentdir = os.path.dirname(groupdir)
        assignmentinfo = Info.read_open(assignmentdir, 'Assignment')
        gradeconf_filename = assignmentinfo.get('gradeconf_filename')
        if gradeconf_filename:
            gradeconf_help = assignmentinfo.get('gradeconf_help')
            grade = open(gradeconf_filename, 'rb').read()
        else:
            grade = self.opt.grade
            if not grade:
                log.error('A grade is required. See --help for more info.')
                raise SystemExit()

        # Get feedback text from arguments or file.
        text = self.opt.text
        feedbackfile = os.path.join(deliverydir, 'feedback.rst')
        if text:
            log.debug('Feedback found in commandline argument -t.')
        else:
            log.debug('Feedback not found in commandline argument -t. ' \
                    'Trying file feedback.rst.')
            if os.path.isfile(feedbackfile):
                log.info('Found feedback in file feedback.rst.')
                text = open(feedbackfile, 'rb').read()

        if text:
            log.info('Feedback format: %s.' % self.opt.format)

        server = self.get_serverproxy()
        try:
            ok_message = server.set_feedback(info.get_id(), text,
                    self.opt.format, grade)
        except xmlrpclib.Fault, e:
            log.error(format_long_message('ERROR MESSAGE', e.faultString,
                False))
            log.error('Setting feedback failed. See error-message above.')
        else:
            lastsave_filename = overwriteable_filename('feedback.lastsave.rst')
            overwrite(deliverydir, lastsave_filename, text)
            open(feedbackfile, 'wb').write(text)
            if ok_message:
                log.info(format_long_message('FEEDBACK SUCCESSFULLY SAVED',
                    ok_message))
            else:
                log.info('Feedback successfully saved.')
