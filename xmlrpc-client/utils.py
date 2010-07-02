from os import makedirs
from os.path import isfile, isdir, join
from cookielib import LWPCookieJar
import urllib2
import logging
from urlparse import urljoin


DATETIME_FORMAT = '%Y-%m-%d_%H:%M:%S'


class AssignmentTreeWalker(object):
    def __init__(self, cookiepath, server, serverurl):
        self.cookiepath = cookiepath
        self.server = server
        self.serverurl = serverurl
        cj = LWPCookieJar()
        if isfile(cookiepath):
            cj.load(cookiepath)
        self.urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        for assignment in server.list_active_assignments():
            assignmentdir = '%(path)s_id-%(id)d' % assignment
            self.assignment(assignment, assignmentdir)

            for group in server.list_assignmentgroups(assignment['id']):
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
