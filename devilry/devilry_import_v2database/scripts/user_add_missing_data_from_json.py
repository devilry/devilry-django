#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import argparse
from dateutil.parser import parse

import django
import json

from django.utils import timezone


def create_minimal_v2_map(json_data):
    """
    Create a minimal map for lookup where each key is a v2 user id (PK).

    Since the map created from the
    """
    v2_user_data_map = {}
    for data in json_data:
        v2_user_data_map[data['pk']] = {
            'username': data['fields']['username'],
            'last_login': data['fields']['last_login']
        }
    return v2_user_data_map


def get_v3_users_from_v2_user_ids(v2_user_ids):
    """
    Get v3 users with last_login==null and has a matching v2 user id
    """
    from django.contrib.auth import get_user_model
    return get_user_model().objects\
        .filter(last_login__isnull=True)\
        .filter(id__in=v2_user_ids)


def add_missing_data_from_json_data(v2_user_data):
    from django.contrib.auth import get_user_model

    # Get v2 user ids.
    v2_user_ids = [data['pk'] for data in v2_user_data]

    # Get v3 users from v2 user ids.
    v3_users_from_v2_users = get_v3_users_from_v2_user_ids(v2_user_ids=v2_user_ids)

    # Create minimal map with v2 user data.
    v2_user_info_map = create_minimal_v2_map(json_data=v2_user_data)

    # Add some counters for info.
    v3_user_count_total = get_user_model().objects.count()
    v3_users_from_v2_users_count = v3_users_from_v2_users.count()
    mismatching_usernames_for_id_count = 0
    successfully_updated_count = 0

    print('Found {}/{} v3 users with existing v2 user IDs with last_login == NULL'.format(
        v3_users_from_v2_users_count,
        v3_user_count_total
    ))
    for v3_user in v3_users_from_v2_users:
        if v3_user.shortname != v2_user_info_map[v3_user.id]['username']:
            mismatching_usernames_for_id_count += 1
        else:
            successfully_updated_count += 1
            v3_user.last_login = timezone.make_aware(
                parse(v2_user_info_map[v3_user.id]['last_login']))
            v3_user.save()
        if successfully_updated_count % 1000 == 0:
            print('{} users updated'.format(successfully_updated_count))
    print('{} users had the same ID in v3 and v2, but mismatching usernames'.format(
        mismatching_usernames_for_id_count
    ))
    print('{} users have been updated with last login datetime'.format(
        successfully_updated_count
    ))


def populate_arguments_and_get_parser():
    parser = argparse.ArgumentParser(description='Set up department permission groups for missing subjects.')
    parser.add_argument(
        '--json-file-path',
        dest='json_file_path',
        required=True,
        help='Path to file.')
    return parser


if __name__ == "__main__":
    # For development:
    os.environ.setdefault('DJANGOENV', 'develop')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devilry.project.settingsproxy")
    django.setup()

    # For production: Specify python path to your settings file here
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devilry_settings')
    # django.setup()

    parser = populate_arguments_and_get_parser()
    args = parser.parse_args()
    arguments_dict = vars(args)

    # Load JSON data
    v2_user_data = json.load(open(arguments_dict['json_file_path']))

    # Update users
    add_missing_data_from_json_data(v2_user_data=v2_user_data)

