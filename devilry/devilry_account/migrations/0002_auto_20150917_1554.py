# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermissionGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='A unique name for this group.', unique=True, max_length=255, verbose_name='Name', blank=True)),
                ('editable', models.BooleanField(default=False, help_text='Is this group editable by non-superusers.', verbose_name='Editable')),
                ('created_datetime', models.DateTimeField(help_text='The time when this group was created.', verbose_name='Created time', auto_now_add=True)),
                ('updated_datetime', models.DateTimeField(help_text='The time when this group last updated.', verbose_name='Last updated time', auto_now=True)),
                ('syncsystem_update_datetime', models.DateTimeField(help_text='The time when this group last updated from a third party sync system.', verbose_name='Last updated from syncsystem time', null=True, editable=False)),
                ('grouptype', models.CharField(help_text='Course and semester administrator groups can only be assigned to a single course or semester. Department administrator groups can be assigned to multiple courses.', max_length=30, verbose_name='Permission group type', choices=[(b'subjectadmin', 'Course administrator group'), (b'periodadmin', 'Semester administrator group'), (b'departmentadmin', 'Department administrator group')])),
            ],
            options={
                'verbose_name': 'Permission group',
                'verbose_name_plural': 'Permission group',
            },
        ),
        migrations.CreateModel(
            name='PermissionGroupUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(to='devilry_account.PermissionGroup')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Permission group user',
                'verbose_name_plural': 'Permission group users',
            },
        ),
        migrations.AddField(
            model_name='permissiongroup',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Users in this group', through='devilry_account.PermissionGroupUser', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='permissiongroupuser',
            unique_together=set([('group', 'user')]),
        ),
    ]
