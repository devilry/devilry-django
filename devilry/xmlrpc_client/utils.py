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


DATETIME_FORMAT = '%Y.%m.%d_%H-%M-%S'


def id_from_path(path):
    m = re.match(r'.*?_id-(\d+)$', os.path.normpath(path))
    if not m:
        return None
    return int(m.groups(1)[0])

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
    *.info* where information about the item in the directory.
    
    .. attribute:: dirpath
        Directory where the info-file is stored on disk.
    .. attribute:: filepath
        Path where the info-file is stored on disk.
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

    def getid(self):
        return self.get('id')

    def new(self):
        self.cfg.add_section(self.sectionname)
        self.set('type', self.typename)

    def read(self):
        self.cfg.read([self.filepath])
        if not os.path.exists(self.filepath):
            raise InfoFileDoesNotExistError(self, "The info-file does not exists.")
        if not self.cfg.has_section(self.sectionname):
            raise InfoFileMissingSectionError(self,
                    'The info-file, %s, has no [%s]-section. This could ' \
                    'be because you have changed or overwritten the file.' % (
                        self.filepath, self.sectionname))
        if self.get('type') != self.typename:
            raise InfoFileWrongTypeError(
                    'The expected type, %s, does not match the existing ' \
                    'type, %s, in %s. This could mean you have managed to ' \
                    'checkout one devilry-tree within another.' % (
                    self.typename, self.get('type'), self.filepath))

    def write(self):
        self.cfg.write(open(self.filepath, 'wb'))

    def __str__(self):
        f = StringIO()
        self.cfg.write(f)
        return f.getvalue()

    def _change_dirpath(self, dirpath):
        self.dirpath = dirpath
        self.filepath = os.path.join(dirpath, '.info')

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
        """
        parentdir = os.path.dirname(self.dirpath)
        dirpath_with_id = '%s.%s' % (self.dirpath, id)
        if os.path.exists(self.dirpath):
            existing_id = Info.read_open(self.dirpath, self.typename).getid()
            existing_dirpath_with_id = '%s.%s' % (self.dirpath, existing_id)
            os.rename(self.dirpath, existing_dirpath_with_id)
            self._change_dirpath(dirpath_with_id)
            return existing_dirpath_with_id
        return False

    def determine_location(self, id):
        """
        Determine the correct location of this Info, changing
        the :attr:`dirpath` the Info exists, but uses id in it's path.

        :return: True if the determined location exists.
        """
        dirpath_with_id = '%s.%s' % (self.dirpath, id)
        if os.path.exists(dirpath_with_id):
            self._change_dirpath(dirpath_with_id)
            return True
        if os.path.exists(self.dirpath):
            existing_id = Info.read_open(self.dirpath, self.typename).getid()
            return existing_id == str(id)
        return False


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
            assignmentinfo = Info(assignmentdir, "Assignment")
            self.assignment(assignment, assignmentinfo)

            for group in server.list_assignmentgroups(assignment['path']):
                groupname = '-'.join(group['students'])
                # Note that the correct dirpath depends on the assignment
                # method setting assignmentinfo.dirpath correctly..
                groupdir = os.path.join(assignmentinfo.dirpath, groupname)
                groupinfo = Info(groupdir, "AssignmentGroup")
                self.assignmentgroup(group, groupinfo)

                for delivery in server.list_deliveries(group['id']):
                    time_of_delivery = delivery['time_of_delivery'].strftime(
                            DATETIME_FORMAT)
                    deliverydir = os.path.join(groupinfo.dirpath, time_of_delivery)
                    filesdir = os.path.join(deliverydir, 'files')
                    self.delivery(delivery, deliverydir, filesdir)

                    for filemeta in delivery['filemetas']:
                        filepath = os.path.join(filesdir, filemeta['filename'])
                        self.filemeta(filemeta, deliverydir, filepath)

                    try:
                        feedback = server.get_feedback(delivery['id'])
                    except xmlrpclib.Fault, e:
                        if e.faultCode == 404:
                            self.feeback_none(delivery, deliverydir)
                        else:
                            raise
                    else:
                        self.feedback_exists(delivery, deliverydir, feedback)

    def assignment(self, assignment, info):
        """ Called on each assignment.
        
        Calls :meth:`assignment_new` if the assignment has not been synced
        before, and :meth:`assignment_exists` if not. These two methods do
        nothing by default, and are ment to be overridden in subclasses.
        """
        if os.path.isdir(info.dirpath):
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

    def delivery(self, delivery, deliverydir, filesdir):
        """ Called on each delivery.
        
        Calls :meth:`delivery_new` if the delivery has not been synced
        before, and :meth:`delivery_exists` if not. These two methods do
        nothing by default, and are ment to be overridden in subclasses.
        """
        if os.path.isdir(deliverydir):
            self.delivery_exists(delivery, deliverydir, filesdir)
        else:
            self.delivery_new(delivery, deliverydir, filesdir)

    def delivery_new(self, delivery, deliverydir, filesdir):
        pass
    def delivery_exists(self, delivery, deliverydir, filesdir):
        pass

    def filemeta(self, filemeta, deliverydir, filepath):
        """ Called on each filemeta.
        
        Calls :meth:`filemeta_new` if the filemeta has not been synced
        before, and :meth:`filemeta_exists` if not. These two methods do
        nothing by default, and are ment to be overridden in subclasses.
        """
        if os.path.isfile(filepath):
            self.filemeta_exists(filemeta, deliverydir, filepath)
        else:
            self.filemeta_new(filemeta, deliverydir, filepath)

    def filemeta_new(self, filemeta, deliverydir, filepath):
        pass
    def filemeta_exists(self, filemeta, deliverydir, filepath):
        pass

    def feeback_none(self, delivery, deliverydir):
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
        logging.info('+ %s' % info.dirpath)
        os.mkdir(info.dirpath)
        info.new()
        info.addmany(
                id = assignment['id'],
                short_name = assignment['short_name'],
                long_name = assignment['long_name'],
                path = assignment['path'],
                publishing_time = assignment['publishing_time'])
        info.write()

    def assignment_exists(self, assignment, info):
        logging.debug('%s already exists' % info.dirpath)
        #errorfallback = 'If so, you can backup and delete the directory, ' \
                #'%s, and sync to get a fresh copy from the server.' % \
                #assignmentdir
        info.read()
        if not assignment['xmlrpc_gradeconf']:
            logging.warning(
                    '%s does not support creating feedback using ' \
                    'the command-line' % assignment['path'])


    def assignmentgroup_nodeliveries(self, group, info):
        logging.warning('Group "%s" has no deliveries' %
                info.dirpath)

    def assignmentgroup_new(self, group, info):
        olddir = info.dirpath
        renamed_name = info.rename_if_required(group['id'])
        if renamed_name:
            logging.warning('Renamed %s -> %s to avoid name crash with %s.' % (
                olddir, renamed_name, info.dirpath))
        logging.info('+ %s' % info.dirpath)
        os.mkdir(info.dirpath)
        info.new()
        info.addmany(
                id = group['id'],
                name = group['name'] or '',
                students = ', '.join(group['students']),
                number_of_deliveries = group['number_of_deliveries'])
        info.write()

    def assignmentgroup_exists(self, group, info):
        logging.debug('%s already exists.' % info.dirpath)

    def delivery_new(self, delivery, deliverydir, filesdir):
        logging.info('+ %s' % deliverydir)
        os.mkdir(deliverydir)
        os.mkdir(filesdir)

    def delivery_exists(self, delivery, deliverydir, filesdir):
        logging.debug('%s already exists.' % deliverydir)


    #def filemeta_new(self, filemeta, deliverydir, filepath):
        #logging.info('+ %s' % filepath)
        #url = urljoin(self.serverurl,
            #"/ui/download-file/%s" % filemeta['id'])
        #logging.debug('Downloading file: %s' % url)
        #size = filemeta['size']
        #left_bytes = size
        #input = self.urlopener.open(url)
        #output = open(filepath, 'wb')
        #while left_bytes > 0:
            #out = input.read(self.bufsize)
            #left_bytes -= len(out)
            #if len(out) == 0:
                #break
            #output.write(out)
        #input.close()
        #output.close()

    #def filemeta_exists(self, filemeta, deliverydir, filepath):
        #logging.debug('%s already exists.' % filepath)


    #def feeback_none(self, delivery, deliverydir):
        #pass

    #def feedback_exists(self, delivery, deliverydir, feedback):
        #if feedback['format'] == 'restructuredtext':
            #ext = 'rst'
        #else:
            #ext = 'txt'
        #feedbackfile = os.path.join(deliverydir, 'feedback.server.%s' % ext)
        #open(feedbackfile, 'wb').write(feedback['text'])


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
