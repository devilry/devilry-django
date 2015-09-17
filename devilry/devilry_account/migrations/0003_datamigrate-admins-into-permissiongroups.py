# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def datamigrate_admins_into_permissiongroups(apps, schema_editor):
    permissiongroup_model = apps.get_model('devilry_account', 'PermissionGroup')
    permissiongroupuser_model = apps.get_model('devilry_account', 'PermissionGroupUser')
    subject_model = apps.get_model('core', 'Subject')
    subjectpermissiongroup_model = apps.get_model('devilry_account', 'SubjectPermissionGroup')
    period_model = apps.get_model('core', 'Period')
    periodpermissiongroup_model = apps.get_model('devilry_account', 'PeriodPermissionGroup')
    permissiongroupusers = []
    subjectpermissiongroups = []
    periodpermissiongroups = []

    for subject in subject_model.objects.prefetch_related('admins'):
        permissiongroup = permissiongroup_model(
            name=subject.short_name,
            is_custom_manageable=True,
            grouptype='subjectadmin')
        permissiongroup.save()

        subjectpermissiongroups.append(
            subjectpermissiongroup_model(
                subject=subject,
                permissiongroup=permissiongroup))

        for adminuser in subject.admins.all():
            permissiongroupusers.append(
                permissiongroupuser_model(
                    permissiongroup=permissiongroup,
                    user=adminuser))

    for period in period_model.objects\
            .select_related('parentnode')\
            .prefetch_related('admins'):
        permissiongroup = permissiongroup_model(
            name=u'{}.{}'.format(period.parentnode.short_name,
                                 period.short_name),
            is_custom_manageable=True,
            grouptype='periodadmin')
        permissiongroup.save()

        periodpermissiongroups.append(
            periodpermissiongroup_model(
                period=period,
                permissiongroup=permissiongroup))

        for adminuser in period.admins.all():
            permissiongroupusers.append(
                permissiongroupuser_model(
                    permissiongroup=permissiongroup,
                    user=adminuser))

    permissiongroupuser_model.objects.bulk_create(permissiongroupusers)
    subjectpermissiongroup_model.objects.bulk_create(subjectpermissiongroups)
    periodpermissiongroup_model.objects.bulk_create(periodpermissiongroups)


class Migration(migrations.Migration):
    dependencies = [
        ('devilry_account', '0002_auto_20150917_1731'),
        ('core', '0003_auto_20150917_1537'),
    ]

    operations = [
        migrations.RunPython(datamigrate_admins_into_permissiongroups)
    ]
