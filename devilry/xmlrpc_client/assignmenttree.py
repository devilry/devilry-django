"""
.. attribute:: ID_SEP

    Separator used to separate id and filenames when handling duplicate
    directory names: ``'+'``.
"""


from StringIO import StringIO
import os
from cookielib import LWPCookieJar
import urllib2
import logging
from urlparse import urljoin
import xmlrpclib
from ConfigParser import SafeConfigParser, NoOptionError


ID_SEP = '+'
log = logging.getLogger('devilry')


def join_dirname_id(dirname, id):
    """ Join ``dirname`` and ``id`` using :attr:`ID_SEP`. """
    return "%s+%s" % (dirname, id)

def overwriteable_filename(filename):
    """
    All files that the sync operations might overwrite without notice
    uses this function to prefix the filename with ``".overwriteable-"``.
    """
    return '.overwriteable-%s' % filename

class OverwriteError(Exception):
    """
    Raised by :func:`overwrite` when trying to overwrite a file not starting
    with ``".overwriteable-"`` without making a backup.
    """

def overwrite(dirname, filename, data):
    """
    Overwrite the given file with the given ``data``. If the file is not
    overwriteable (see :func:`overwriteable_filename`), raise
    :exc:`OverwriteError`.
    """
    filepath = os.path.join(dirname, filename)
    if not filename.startswith('.overwriteable-'):
        raise OverwriteError('Can not overwrite %s.' % filepath)
    open(filepath, 'wb').write(data)


def make_backup(filepath, index=0):
    """
    Create a backup of the file, ``filepath``, named *[filename].bak-[N]*,
    where [N] is the lowest number higher than ``index`` which produces a
    unique filename.
    """
    backupfile = '%s.bak-%d' % (filepath, index)
    if os.path.exists(backupfile):
        make_backup(filepath, index+1)
    else:
        log.warning('%s was overwritten. Backup written to %s.' % (
            filepath, backupfile))
        open(backupfile, 'wb').write(open(filepath, 'rb').read())

def overwrite_with_backup(dirname, filename, data, lastsavefilename=None):
    """
    Overwrite the given file with the given ``data`` and create a backup
    using :func:`make_backup` if the file exists and the contents of the
    existing file does not match ``data``.

    Both ``filename`` and ``lastsavefilename`` are files in the ``dirname``
    directory. They do not have to exist. ``lastsavefilename`` is filtered
    throught :func:`overwriteable_filename`.

    If ``lastsavefilename`` is the name of a existing file, a backup will
    not be created unless the contents of ``filename`` does not match the
    contents of ``lastsavefilename``.
    """
    filepath = os.path.join(dirname, filename)
    if os.path.exists(filepath):
        current_data = open(filepath, 'rb').read()
        if current_data == data:
            log.debug('%s matches the server. No update requried.' %
                    filepath)
            return
        lastsavefile = os.path.join(dirname,
                overwriteable_filename(lastsavefilename))
        if lastsavefilename and os.path.exists(lastsavefile):
            lastsave_data = open(lastsavefile, 'rb').read()
            if lastsave_data == data:
                # No need for data if the server matches our last save,
                # but a warning is needed.
                log.warning('%(dirname)s: %(filename)s has local '\
                        'modifications, but the file on the server ' \
                        'matches your last save, so your local file ' \
                        'remains utouched. Remove %(filename)s and sync to ' \
                        'get the file from the server.' % vars())
                return
            if lastsave_data == current_data:
                # If the file has not changed since last save, we do not
                # need a backup
                log.debug('Last-save data for %s matches current data. No '\
                        'backup required.' % filepath)
            else:
                log.debug('Last-save data for %s does not match current ' \
                        'data. Backup required.' % filepath)
                make_backup(filepath)
        else:
            make_backup(filepath)
    if not os.path.exists(filepath):
        log.info('+ %s' % filepath)
    open(filepath, 'wb').write(data)
    if lastsavefilename:
        overwrite(dirname, overwriteable_filename(lastsavefilename), data)


class Info(object):
    sectionname = 'info'

    class Error(Exception):
        """ Base class for errors with the :class:`Info`-class.
        
        .. attribute:: info

            The info-object where the error occurred.
        """
        def __init__(self, info, msg):
            self.info = info
            super(Exception, self).__init__(msg)

    class FileDoesNotExistError(Exception):
        """ Raised in :meth:`Info.read` when the info-file is missing from
        the expected filesystem location. """

    class FileMissingSectionError(Exception):
        """ Raised in :meth:`Info.read` when the info-file is missing the
        [info]-section. """

    class FileWrongTypeError(Exception):
        """ Raised in :meth:`Info.read` when the *type* stored in the
        info-file does not match the expected type. """


    @classmethod
    def read_open(cls, dirpath, typename=None):
        """ Shortcut to open a Info for reading.
        
        If typename is ``None``, :meth:`read` is called with check_typename
        set to ``False``.
        """
        i = Info(dirpath, typename)
        i.read(typename != None)
        return i

    def __init__(self, dirpath, typename):
        """
        :param dirpath:
            Directory path. If expecting duplicate names, set this to the
            name without a id, and use :meth:`determine_location` and
            :meth:`rename_if_required` to handle duplicates.
        :param typename:
            This is used as a sanity check to make sure we are not syncing
            two different tree. If you, for example, give typename
            ``"Delivery"``, and the :meth:`read`-method reads a file with
            typename ``"Assignment"``, :exc:`Info.FileWrongTypeError` is
            raised.
        """
        self._infofilename = overwriteable_filename('info')
        self._change_dirpath(dirpath)
        self.typename = typename
        self.cfg = SafeConfigParser()

    def set(self, key, value):
        """ Set a value. """
        if value == None:
            value = ''
        if isinstance(value, basestring):
            value = value.encode("utf-8")
        else:
            value = str(value)
        self.cfg.set(self.sectionname, key, value)

    def setmany(self, **values):
        """ Set many values. """
        for key, value in values.iteritems():
            self.set(key, value)

    def get(self, key, default=None):
        """ Get a item, but default to ``default`` if the key is not found. """
        try:
            return self[key]
        except KeyError, e:
            return default

    def __getitem__(self, key):
        """ Get a item. """
        try:
            return self.cfg.get(self.sectionname, key)
        except NoOptionError, e:
            raise KeyError(str(e))

    def get_id(self):
        """ Shortcut to get the id. """
        return self.get('id')

    def get_dirpath(self):
        """ Get the directory where the info-file is stored on disk. """
        return self._dirpath

    def get_infofilepath(self):
        """ Get path to where the info-file is stored on disk. """
        return self._infofilepath

    def new(self):
        """ Initialize a new info-object with mandatory data. If working
        with a existing info-file, use :meth:`read` instead. """
        self.cfg.add_section(self.sectionname)
        self.set('type', self.typename)

    def read(self, check_typename=True):
        """ Read info-file from disk.
        If check_typename is ``False``, no exception is raised if the type
        in the file, and current typename does not match.
        """
        self.cfg.read([self._infofilepath])
        if not os.path.exists(self._infofilepath):
            raise Info.FileDoesNotExistError(self, "The info-file does not exists.")
        if not self.cfg.has_section(self.sectionname):
            raise Info.FileMissingSectionError(self,
                    'The info-file, %s, has no [%s]-section. This could ' \
                    'be because you have changed or overwritten the file.' % (
                        self._infofilepath, self.sectionname))
        if check_typename and self.get('type') != self.typename:
            raise Info.FileWrongTypeError(
                    'The expected type, %s, does not match the existing ' \
                    'type, %s, in %s. This could mean you have managed to ' \
                    'checkout one devilry-tree within another.' % (
                    self.typename, self.get('type'), self._infofilepath))

    def write(self):
        """ Write info-file to disk. """
        self.cfg.write(open(self._infofilepath, 'wb'))

    def __str__(self):
        f = StringIO()
        self.cfg.write(f)
        return f.getvalue()

    def _change_dirpath(self, dirpath):
        self._dirpath = dirpath
        self._infofilepath = os.path.join(dirpath, self._infofilename)

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
                    deliverydir = os.path.join(groupinfo.get_dirpath(),
                            str(delivery['number']))
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
                            self.feedback_none(delivery, deliverydir,
                                    assignment['xmlrpc_gradeconf'])
                        else:
                            raise
                    else:
                        self.feedback_exists(delivery, deliverydir,
                                feedback, assignment['xmlrpc_gradeconf'])

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
        if os.path.isdir(info.get_dirpath()):
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

    def feedback_none(self, delivery, deliverydir, gradeconf):
        """ Called when there is no feedback on a delivery. Does nothing by
        default, and should be overridden in subclasses. """
        pass

    def feedback_exists(self, delivery, deliverydir, feedback, gradeconf):
        """ Called when there is feedback on a delivery. Does nothing by
        default, and should be overridden in subclasses. """
        pass


class AssignmentSync(AssignmentTreeWalker):
    """
    .. attribute:: bufsize

        Buffer size used when downloading files. Defaults to ``65536``, and
        might be overridden in subclasses.
    """
    bufsize = 65536

    def __init__(self, rootdir, cookiepath, server, serverurl,
            authcookiefile=None):
        self.authcookiefile = authcookiefile
        cwd = os.getcwd()
        os.chdir(rootdir)
        try:
            super(AssignmentSync, self).__init__(cookiepath, server,
                    serverurl)
        finally:
            os.chdir(cwd)

    def _assignment_info_refresh(self, assignment, info):
        info.setmany(
                id = assignment['id'],
                short_name = assignment['short_name'],
                long_name = assignment['long_name'],
                path = assignment['path'],
                publishing_time = assignment['publishing_time'])
        gradeconf = assignment['xmlrpc_gradeconf']
        if gradeconf:
            info.setmany(
                gradeconf_help = gradeconf['help'],
                gradeconf_filename = gradeconf['filename'],
                gradeconf_default_filencontents = gradeconf['default_filecontents'])
        info.write()

    def assignment_new(self, assignment, info):
        log.info('+ %s' % info.get_dirpath())
        os.mkdir(info.get_dirpath())
        info.new()
        self._assignment_info_refresh(assignment, info)

    def assignment_exists(self, assignment, info):
        log.debug('%s already exists' % info.get_dirpath())
        info.read()
        self._assignment_info_refresh(assignment, info)
        if not assignment['xmlrpc_gradeconf']:
            log.warning(
                    '%s does not support creating feedback using ' \
                    'the command-line' % assignment['path'])


    def assignmentgroup_nodeliveries(self, group, info):
        log.warning('Group "%s" has no deliveries' %
                info.get_dirpath())


    def _assignmentgroup_info_refresh(self, group, info):
        info.setmany(
                id = group['id'],
                name = group['name'] or '',
                students = ', '.join(group['students']),
                number_of_deliveries = group['number_of_deliveries'])
        info.write()

    def assignmentgroup_new(self, group, info):
        olddir = info.get_dirpath()
        renamed_name = info.rename_if_required(group['id'])
        if renamed_name:
            log.warning('Renamed %s -> %s to avoid name crash with %s.' % (
                olddir, renamed_name, info.get_dirpath()))
        log.info('+ %s' % info.get_dirpath())
        os.mkdir(info.get_dirpath())
        info.new()
        self._assignmentgroup_info_refresh(group, info)

    def assignmentgroup_exists(self, group, info):
        log.debug('%s already exists.' % info.get_dirpath())
        info.read()
        self._assignmentgroup_info_refresh(group, info)


    def _delivery_info_refresh(self, delivery, info):
        info.setmany(
                id = delivery['id'],
                number = delivery['number'],
                time_of_delivery = delivery['time_of_delivery'])
        info.write()

    def _create_feedbackfile_if_notexists(self, deliverydir):
        path = os.path.join(deliverydir, 'feedback.rst')
        if not os.path.exists(path):
            lastsave_filename = overwriteable_filename('feedback.lastsave.rst')
            overwrite(deliverydir, lastsave_filename, '')
            open(path, 'wb').write('')

    def delivery_new(self, delivery, info):
        if not delivery['successful']:
            log.debug('Delivery %s was not successfully completed, and '
                    'is therefore ignored.' % info.get_dirpath())
            return
        log.info('+ %s' % info.get_dirpath())
        os.mkdir(info.get_dirpath())
        os.mkdir(os.path.join(info.get_dirpath(), 'files'))
        info.new()
        self._delivery_info_refresh(delivery, info)
        self._create_feedbackfile_if_notexists(info.get_dirpath())

    def delivery_exists(self, delivery, info):
        log.debug('%s already exists.' % info.get_dirpath())
        info.read()
        self._delivery_info_refresh(delivery, info)
        self._create_feedbackfile_if_notexists(info.get_dirpath())


    def filemeta_new(self, filemeta, filepath):
        log.info('+ %s' % filepath)
        serverurl = self.serverurl
        if self.serverurl.endswith('/'):
            serverurl = serverurl[:-1]
        url = "%s/ui/download-file/%s" % (serverurl, filemeta['id'])
        log.debug('Downloading file: %s' % url)
        size = filemeta['size']
        left_bytes = size
        request = urllib2.Request(url)
        if self.authcookiefile and os.path.isfile(self.authcookiefile):
            for line in open(self.authcookiefile, 'rb').readlines():
                request.add_header("Cookie", line.strip())
        try:
            input = self.urlopener.open(request)
        except urllib2.HTTPError, e:
            log.warning("Could not download file: %s. This is probably "\
                    "because the delivery exists on the server, but the "\
                    "file has been deleted from the file backend by a " \
                    "administrator." % url)
        else:
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
        log.debug('%s already exists.' % filepath)

    def _handle_gradeconf(self, deliverydir, gradeconf,
            grade_as_xmlrpcstring):
        filename = gradeconf.get('filename')
        if filename:
            overwrite_with_backup(deliverydir, filename,
                    grade_as_xmlrpcstring, filename + '.lastsave')

    def feedback_none(self, delivery, deliverydir, gradeconf):
        self._handle_gradeconf(deliverydir, gradeconf,
                gradeconf.get('default_filecontents', ''))

    @classmethod
    def set_feedbackinfo(cls, deliverydir, feedback):
        deliveryinfo = Info.read_open(deliverydir, 'Delivery')
        deliveryinfo.setmany(
            feedback_text = feedback['text'],
            feedback_format = feedback['format'],
            feedback_published = feedback['published'],
            feedback_last_modified = feedback['last_modified'],
            feedback_last_modified_by = feedback['last_modified_by'])
        deliveryinfo.write()

    def feedback_exists(self, delivery, deliverydir, feedback, gradeconf):
        self._handle_gradeconf(deliverydir, gradeconf,
                feedback.get('grade_as_xmlrpcstring'))
        self.__class__.set_feedbackinfo(deliverydir, feedback)
        overwrite_with_backup(deliverydir, 'feedback.rst', feedback['text'],
                'feedback.lastsave.rst')
