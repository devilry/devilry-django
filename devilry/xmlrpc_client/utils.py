from StringIO import StringIO
import sys
import os
from cookielib import LWPCookieJar
import urllib2
import logging
from urlparse import urljoin
import re
import xmlrpclib
from ConfigParser import SafeConfigParser


# TODO: chmod cookies.txt


DATETIME_FORMAT = '%Y-%m-%d_%H.%M.%S'



def join_dirname_id(dirname, id):
    return "%s+%s" % (dirname, id)

def log_fault(fault):
    """ Log a xmlrpclib.Fault to logging.error. """
    logging.error('%s: %s' % (fault.faultCode, fault.faultString))


class InfoError(Exception):
    """ Base class for errors with the :class:`Info`-class.
    
    .. attribute:: info
        The info-object where the error occurred.
    """
    def __init__(self, info, msg):
        self.info = info
        super(Exception, self).__init__(msg)

class InfoFileDoesNotExistError(Exception):
    """ Raised in :meth:`Info.write` when the info-file is missing from the
    expected filesystem location. """

class InfoFileMissingSectionError(Exception):
    """ Raised in :meth:`Info.write` when the info-file is missing the
    [info]-section. """

class InfoFileWrongTypeError(Exception):
    """ Raised in :meth:`Info.write` when the *type* stored in the info-file
    does not match the expected type. """


class Info(object):
    """ Each directory in the assignment-tree has a hidden file named
    *.info* where information about the item in the directory is stored.
    """
    sectionname = 'info'

    @classmethod
    def read_open(cls, dirpath, typename):
        """ Shortcut to open a Info for reading. """
        i = Info(dirpath, typename)
        i.read()
        return i

    def __init__(self, dirpath, typename):
        self._change_dirpath(dirpath)
        self.typename = typename
        self.cfg = SafeConfigParser()

    def set(self, key, value):
        self.cfg.set(self.sectionname, key, value)

    def addmany(self, **values):
        for key, value in values.iteritems():
            self.set(key, str(value))

    def get(self, key):
        return self.cfg.get(self.sectionname, key)

    def get_id(self):
        return self.get('id')

    def get_dirpath(self):
        """ Get the directory where the info-file is stored on disk. """
        return self._dirpath

    def get_infofilepath(self):
        """ Get path to where the info-file is stored on disk. """
        return self._infofilepath

    def new(self):
        self.cfg.add_section(self.sectionname)
        self.set('type', self.typename)

    def read(self):
        self.cfg.read([self._infofilepath])
        if not os.path.exists(self._infofilepath):
            raise InfoFileDoesNotExistError(self, "The info-file does not exists.")
        if not self.cfg.has_section(self.sectionname):
            raise InfoFileMissingSectionError(self,
                    'The info-file, %s, has no [%s]-section. This could ' \
                    'be because you have changed or overwritten the file.' % (
                        self._infofilepath, self.sectionname))
        if self.get('type') != self.typename:
            raise InfoFileWrongTypeError(
                    'The expected type, %s, does not match the existing ' \
                    'type, %s, in %s. This could mean you have managed to ' \
                    'checkout one devilry-tree within another.' % (
                    self.typename, self.get('type'), self._infofilepath))

    def write(self):
        self.cfg.write(open(self._infofilepath, 'wb'))

    def __str__(self):
        f = StringIO()
        self.cfg.write(f)
        return f.getvalue()

    def _change_dirpath(self, dirpath):
        self._dirpath = dirpath
        self._infofilepath = os.path.join(dirpath, '.info')

    def rename_if_required(self, id):
        """
        If the directory for this Info does not exist, we use this to
        determine if a rename from a non-id-based naming to id-based naming
        is required to avoid name-crash. If another directory with the same
        name as this one is detected:
        
            - the *other* directory is renamed to include id in it's name.
            - :attr:`dirname` is changed to include id
            - the new directory-name of the *other directory* (the one that
              was renamed) is returned.

        If a rename is not required, ``False`` is returned.

        **Never** call this unless :meth:`determine_location` returns False.

        Only used with duplicate dirnames. See :class:`AssignmentTreeWalker`
        for more information.
        """
        #if not self.determine_location(id):
            #return False
        parentdir = os.path.dirname(self._dirpath)
        dirpath_with_id = join_dirname_id(self._dirpath, id)
        if os.path.exists(self._dirpath):
            existing_id = Info.read_open(self._dirpath, self.typename).get_id()
            existing_dirpath_with_id = join_dirname_id(self._dirpath, existing_id)
            os.rename(self._dirpath, existing_dirpath_with_id)
            self._change_dirpath(dirpath_with_id)
            return existing_dirpath_with_id
        return False

    def determine_location(self, id):
        """
        Determine the correct location of this Info, changing
        the dirpath the Info exists, but uses id in it's path.
        
        Only used with duplicate dirnames. See :class:`AssignmentTreeWalker`
        for more information.

        :return: True if the determined location exists.
        """
        dirpath_with_id = join_dirname_id(self._dirpath, id)
        if os.path.exists(dirpath_with_id):
            self._change_dirpath(dirpath_with_id)
            return True
        if os.path.exists(self._dirpath):
            existing_id = Info.read_open(self._dirpath, self.typename).get_id()
            return existing_id == str(id)
        return False


class AssignmentTreeWalker(object):
    """ Finds all assignment where the current user is examiner, and walks
    through every AssignmentGroup, Delivery, Feedback and FileMeta.

    Calls :meth:`assignment`, :meth:`assignmentgroup`, :meth:`delivery`,
    :meth:`filemeta`, :meth:`feedback_none` and :meth:`feedback_exists` with
    the returned dicts from the corresponding functions in the examiner
    xmlrpc as argument.
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
            assignmentinfo = Info(assignmentdir, "Assignment")
            self.assignment(assignment, assignmentinfo)

            for group in server.list_assignmentgroups(assignment['path']):
                groupname = '-'.join(group['students'])
                # Note that the correct dirpath depends on the assignment
                # method setting assignmentinfo.get_dirpath() correctly..
                groupdir = os.path.join(assignmentinfo.get_dirpath(), groupname)
                groupinfo = Info(groupdir, "AssignmentGroup")
                self.assignmentgroup(group, groupinfo)

                for delivery in server.list_deliveries(group['id']):
                    time_of_delivery = delivery['time_of_delivery'].strftime(
                            DATETIME_FORMAT)
                    deliverydir = os.path.join(groupinfo.get_dirpath(), time_of_delivery)
                    deliveryinfo = Info(deliverydir, "Delivery")
                    self.delivery(delivery, deliveryinfo)

                    filesdir = os.path.join(deliveryinfo.get_dirpath(), 'files')
                    for filemeta in delivery['filemetas']:
                        filepath = os.path.join(filesdir, filemeta['filename'])
                        self.filemeta(filemeta, filepath)

                    try:
                        feedback = server.get_feedback(delivery['id'])
                    except xmlrpclib.Fault, e:
                        if e.faultCode == 404:
                            self.feedback_none(delivery, deliverydir)
                        else:
                            raise
                    else:
                        self.feedback_exists(delivery, deliverydir, feedback)

    def assignment(self, assignment, info):
        """ Called on each assignment.
        
        Calls :meth:`assignment_new` if the assignment has not been synced
        before, and :meth:`assignment_exists` if not. These two methods do
        nothing by default, and are ment to be overridden in subclasses.

        :param assignment: A dictionary as returned from the 
        """
        if os.path.isdir(info.get_dirpath()):
            self.assignment_exists(assignment, info)
        else:
            self.assignment_new(assignment, info)

    def assignment_new(self, assignment, assignmentdir, info):
        pass
    def assignment_exists(self, assignment, assignmentdir, info):
        pass

    def assignmentgroup(self, group, info):
        """ Called on each assignment-group.
        
        Calls :meth:`assignmentgroup_nodeliveries` if the assignmentgroup
        has no deliveries, :meth:`assignmentgroup_new` if the assignment has
        not been synced before, and :meth:`assignmentgroup_exists` if not.
        These three methods do nothing by default, and are ment to be
        overridden in subclasses.
        """
        number_of_deliveries = group['number_of_deliveries']
        if number_of_deliveries == 0:
            self.assignmentgroup_nodeliveries(group, info)
            return

        if info.determine_location(group['id']):
            self.assignmentgroup_exists(group, info)
        else:
            self.assignmentgroup_new(group, info)

    def assignmentgroup_nodeliveries(self, group, groupdir):
        pass
    def assignmentgroup_new(self, group, groupdir):
        pass
    def assignmentgroup_exists(self, group, groupdir):
        pass

    def delivery(self, delivery, info):
        """ Called on each delivery.
        
        Calls :meth:`delivery_new` if the delivery has not been synced
        before, and :meth:`delivery_exists` if not. These two methods do
        nothing by default, and are ment to be overridden in subclasses.
        """
        if info.determine_location(delivery['id']):
            self.delivery_exists(delivery, info)
        else:
            self.delivery_new(delivery, info)

    def delivery_new(self, delivery, info):
        pass
    def delivery_exists(self, delivery, info):
        pass

    def filemeta(self, filemeta, filepath):
        """ Called on each filemeta.
        
        Calls :meth:`filemeta_new` if the filemeta has not been synced
        before, and :meth:`filemeta_exists` if not. These two methods do
        nothing by default, and are ment to be overridden in subclasses.
        """
        if os.path.isfile(filepath):
            self.filemeta_exists(filemeta, filepath)
        else:
            self.filemeta_new(filemeta, filepath)

    def filemeta_new(self, filemeta, filepath):
        pass
    def filemeta_exists(self, filemeta, filepath):
        pass

    def feedback_none(self, delivery, deliverydir):
        """ Called when there is no feedback on a delivery. Does nothing by
        default, and should be overridden in subclasses. """
        pass

    def feedback_exists(self, delivery, deliverydir, feedback):
        """ Called when there is feedback on a delivery. Does nothing by
        default, and should be overridden in subclasses. """
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

    def assignment_new(self, assignment, info):
        logging.info('+ %s' % info.get_dirpath())
        os.mkdir(info.get_dirpath())
        info.new()
        info.addmany(
                id = assignment['id'],
                short_name = assignment['short_name'],
                long_name = assignment['long_name'],
                path = assignment['path'],
                publishing_time = assignment['publishing_time'])
        info.write()

    def assignment_exists(self, assignment, info):
        logging.debug('%s already exists' % info.get_dirpath())
        info.read()
        if not assignment['xmlrpc_gradeconf']:
            logging.warning(
                    '%s does not support creating feedback using ' \
                    'the command-line' % assignment['path'])


    def assignmentgroup_nodeliveries(self, group, info):
        logging.warning('Group "%s" has no deliveries' %
                info.get_dirpath())

    def assignmentgroup_new(self, group, info):
        olddir = info.get_dirpath()
        renamed_name = info.rename_if_required(group['id'])
        if renamed_name:
            logging.warning('Renamed %s -> %s to avoid name crash with %s.' % (
                olddir, renamed_name, info.get_dirpath()))
        logging.info('+ %s' % info.get_dirpath())
        os.mkdir(info.get_dirpath())
        info.new()
        info.addmany(
                id = group['id'],
                name = group['name'] or '',
                students = ', '.join(group['students']),
                number_of_deliveries = group['number_of_deliveries'])
        info.write()

    def assignmentgroup_exists(self, group, info):
        logging.debug('%s already exists.' % info.get_dirpath())

    def delivery_new(self, delivery, info):
        if not delivery['successful']:
            logging.debug('Delivery %s was not successfully completed, and '
                    'is therefore ignored.' % info.get_dirpath())
            return

        olddir = info.get_dirpath()
        renamed_name = info.rename_if_required(delivery['id'])
        if renamed_name:
            logging.warning('Renamed %s -> %s to avoid name crash with %s.' % (
                olddir, renamed_name, info.get_dirpath()))
        logging.info('+ %s' % info.get_dirpath())
        os.mkdir(info.get_dirpath())
        os.mkdir(os.path.join(info.get_dirpath(), 'files'))
        info.new()
        info.addmany(
                id = delivery['id'],
                time_of_delivery = delivery['time_of_delivery'])
        info.write()

    def delivery_exists(self, delivery, info):
        logging.debug('%s already exists.' % info.get_dirpath())


    def filemeta_new(self, filemeta, filepath):
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

    def filemeta_exists(self, filemeta, filepath):
        logging.debug('%s already exists.' % filepath)


    def feedback_none(self, delivery, deliverydir):
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
