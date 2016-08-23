#!/usr/bin/env python
import argparse
import os
import sys

import django
import shutil


class DownloadAllDeliveriesOnAssignment(object):
    DEADLINE_FORMAT = "%Y-%m-%dT%H_%M_%S"

    def __init__(self, assignment, arguments_dict):
        super(DownloadAllDeliveriesOnAssignment, self).__init__()
        self.assignment = assignment
        self.arguments_dict = arguments_dict
        self.tmp_rootdir_name = self.assignment.get_path().encode('ascii', 'replace')

    def create_directory_structure_of_all_deliveries_on_assignment(self):
        self._create_delivery_files()

    def make_tarball_of_deliveries_directory(self):
        command = "tar -cvzf {tarball_filename} {comress_filename}".format(
            tarball_filename=self.tmp_rootdir_name + ".tar.gz",
            comress_filename=self.tmp_rootdir_name
        )
        os.system(command)
        self.__remove_directory()

    def __remove_directory(self):
        shutil.rmtree(self.tmp_rootdir_name)

    def _create_delivery_files(self):
        for group in self._get_assignmentgroup_queryset():
            groupname = '{} (groupid={})'.format(group.short_displayname, group.id)
            for deadline in group.deadlines.all():
                for delivery in deadline.deliveries.all():
                    for filemeta in delivery.filemetas.all():
                        file_content = filemeta.deliverystore.read_open(filemeta)
                        filenametpl = '{tmp_rootdir_name}/{groupname}/deadline-{deadline}/delivery-{delivery_number}/{filename}'
                        filename = filenametpl.format(
                            tmp_rootdir_name=self.tmp_rootdir_name,
                            groupname=groupname,
                            deadline=deadline.deadline.strftime(self.DEADLINE_FORMAT),
                            delivery_number="%.3d" % delivery.number,
                            filename=filemeta.filename.encode('utf-8'))
                        directory = os.path.dirname(filename)
                        print "### " + directory
                        if not arguments_dict.get('dry_run'):
                            if not os.path.exists(directory):
                                os.makedirs(directory)
                            delivery_file = open(filename, 'w')
                            delivery_file.write(file_content.read())
                            delivery_file.close()

    def _get_assignmentgroup_queryset(self):
        return AssignmentGroup.objects.filter(parentnode=self.assignment)


def populate_arguments_and_get_parser():
    parser = argparse.ArgumentParser(description='Create a directory structure of all deliveries on an assignment')
    parser.add_argument('--dry-run', action='store_true',
                        help='run the script without performing the directory structure creation')
    parser.add_argument('--subject', type=str,
                        help='the short name of the subject example: inf1000')
    parser.add_argument('--period', type=str,
                        help='the short name of the period example: 2015v')
    parser.add_argument('--assignment', type=str,
                        help='the short name of the assignment example: oblig1')
    return parser


if __name__ == "__main__":
    os.environ.setdefault("DJANGOENV", 'develop')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devilry.project.settingsproxy")
    django.setup()

    from devilry.apps.core.models import Assignment, AssignmentGroup

    parser = populate_arguments_and_get_parser()
    args = parser.parse_args()
    arguments_dict = vars(args)

    assignment = Assignment.objects.filter(parentnode__short_name=arguments_dict.get('period')). \
        filter(parentnode__parentnode__short_name=arguments_dict.get('subject')). \
        filter(short_name=arguments_dict.get('assignment')). \
        first()

    if not assignment:
        print "There is no assignment matching the arguments of the script"
        print arguments_dict
        sys.exit(-1)

    download_manager = DownloadAllDeliveriesOnAssignment(assignment, arguments_dict)
    download_manager.create_directory_structure_of_all_deliveries_on_assignment()
    if not arguments_dict.get("dry_run"):
        download_manager.make_tarball_of_deliveries_directory()
