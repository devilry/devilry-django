#!/usr/bin/env python
import argparse
import os
import re

import django


# Map departmentadmin permission group names to regexes for matching courses that should be added to a
# permission group.
permission_group_map = {
    # <permission-group-name>: <course short_name regex>
    'ifi': r'^inf?\d+[a-z]?$',
    'fys': r'^(fys|fysmed|fysmek)\d+[a-z]?$'
}


def check_permission_groups_exists():
    from devilry.devilry_account.models import PermissionGroup
    for group_name in list(permission_group_map.keys()):
        if not PermissionGroup.objects.filter(name=group_name).exists():
            raise SystemExit('PermissionGroup with name {} does not exist.'.format(group_name))


def add_subject_to_permission_group(group_name, subject, pretend=True):
    from devilry.devilry_account.models import PermissionGroup, SubjectPermissionGroup
    permission_group = PermissionGroup.objects.get(name=group_name, grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
    if not SubjectPermissionGroup.objects.filter(permissiongroup=permission_group, subject=subject).exists():
        if pretend:
            print('PRETEND ({}): Adding {}'.format(permission_group.name, subject.short_name))
        else:
            print('({}): Adding {}'.format(permission_group.name, subject.short_name))
            subject_permission_group = SubjectPermissionGroup(permissiongroup=permission_group, subject=subject)
            subject_permission_group.full_clean()  # Do not remove this
            subject_permission_group.save()
    else:
        print('({}): {} already exists'.format(subject.short_name, permission_group.name))


def create_subject_permission_groups():
    from devilry.apps.core.models import Subject

    no_matches_list = []
    for subject in Subject.objects.all():
        match = False
        for group_name, subject_short_name_regex in list(permission_group_map.items()):
            if re.match(subject_short_name_regex, subject.short_name):
                match = True
                add_subject_to_permission_group(group_name, subject, pretend=pretend)
        if not match:
            no_matches_list.append(subject.short_name)

    if no_matches_list:
        print('\nCourses that did not match any regexes: ')
        print(', '.join(no_matches_list))


def populate_arguments_and_get_parser():
    parser = argparse.ArgumentParser(description='Set up department permission groups for missing subjects.')
    parser.add_argument('--no-pretend', action='store_false',
                        default=True, dest='pretend',
                        help='Actually update the database with changes. If this is flag is not provided, '
                             'we just pretend run the script and print information.')
    return parser


if __name__ == "__main__":
    """
    Add subjects to department admin permission groups if missing.
    """

    # For development:
    # os.environ.setdefault("DJANGOENV", 'develop')
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devilry.project.settingsproxy")
    # django.setup()

    # For production: Specify python path to your settings file here
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devilry_settings")
    django.setup()

    parser = populate_arguments_and_get_parser()
    args = parser.parse_args()
    arguments_dict = vars(args)
    pretend = arguments_dict['pretend']

    # Exit if no permission groups names matches the keys in permission_group_map
    check_permission_groups_exists()

    #
    create_subject_permission_groups()

