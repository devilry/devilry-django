#!/usr/bin/env python
import argparse
import os
import sys

import django


class DownloadAllDeliveriesOnAssignment(object):
    DEADLINE_FORMAT = "%Y-%m-%dT%H_%M_%S"

    def __init__(self, assignment, args_dict):
        super(DownloadAllDeliveriesOnAssignment, self).__init__()
        self.assignment = assignment
        self.args_dict = args_dict

    def create_directory_structure_of_all_deliveries_on_assignment(self):
        tmp_rootdir_name = self.assignment.get_path().encode('ascii', 'replace')
        self._create_delivery_files(tmp_rootdir_name)

    def _create_delivery_files(self, tmp_rootdir_name):
        for group in self._get_assignmentgroup_queryset():
            groupname = '{} (groupid={})'.format(group.short_displayname, group.id)
            for deadline in group.deadlines.all():
                for delivery in deadline.deliveries.all():
                    for filemeta in delivery.filemetas.all():
                        file_content = filemeta.deliverystore.read_open(filemeta)
                        filenametpl = '{tmp_rootdir_name}/{groupname}/deadline-{deadline}/delivery-{delivery_number}/{filename}'
                        filename = filenametpl.format(
                            tmp_rootdir_name=tmp_rootdir_name,
                            groupname=groupname,
                            deadline=deadline.deadline.strftime(self.DEADLINE_FORMAT),
                            delivery_number="%.3d" % delivery.number,
                            filename=filemeta.filename.encode('utf-8'))
                        directory = os.path.dirname(filename)
                        print "### " + directory
                        if not args_dict.get('dry_run'):
                            if not os.path.exists(directory):
                                os.makedirs(directory)
                            delivery_file = open(filename, 'w')
                            delivery_file.write(file_content.read())
                            delivery_file.close()

    def _get_assignmentgroup_queryset(self):
        return AssignmentGroup.objects.filter(parentnode=self.assignment)


if __name__ == "__main__":
    os.environ.setdefault("DJANGOENV", 'develop')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devilry.project.settingsproxy")
    django.setup()

    from devilry.apps.core.models import Assignment, AssignmentGroup

    parser = argparse.ArgumentParser(description='Create a directory structure of all deliveries on an assignment')
    parser.add_argument('--dry-run', action='store_true',
                        help='run the script without performing the directory structure creation')
    parser.add_argument('--subject', type=str,
                        help='the short name of the subject example: inf1000')
    parser.add_argument('--period', type=str,
                        help='the short name of the period example: 2015v')
    parser.add_argument('--assignment', type=str,
                        help='the short name of the assignment example: oblig1')

    args = parser.parse_args()
    args_dict = vars(args)

    assignment = Assignment.objects.filter(parentnode__short_name=args_dict.get('period')). \
        filter(parentnode__parentnode__short_name=args_dict.get('subject')). \
        filter(short_name=args_dict.get('assignment')). \
        first()

    if not assignment:
        print "There is no assignment matching the arguments of the script"
        print args_dict
        sys.exit(-1)

    # ALL YOUR CODE MUST BE BELOW THIS LINE, AFTER CORRECT SETUP

    download_manager = DownloadAllDeliveriesOnAssignment(assignment, args_dict)
    download_manager.create_directory_structure_of_all_deliveries_on_assignment()
