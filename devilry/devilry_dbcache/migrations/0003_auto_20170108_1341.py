# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-01-08 13:41


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_dbcache', '0002_auto_20170108_0948'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignmentgroupcacheddata',
            name='public_admin_imageannotationcomment_count',
        ),
        migrations.RemoveField(
            model_name='assignmentgroupcacheddata',
            name='public_examiner_imageannotationcomment_count',
        ),
        migrations.RemoveField(
            model_name='assignmentgroupcacheddata',
            name='public_student_imageannotationcomment_count',
        ),
        migrations.RemoveField(
            model_name='assignmentgroupcacheddata',
            name='public_total_imageannotationcomment_count',
        ),
    ]
