# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-01-08 09:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_dbcache', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='first_feedbackset',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='devilry_group.FeedbackSet'),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='group',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='cached_data', to='core.AssignmentGroup'),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='last_feedbackset',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='devilry_group.FeedbackSet'),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='last_published_feedbackset',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='devilry_group.FeedbackSet'),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='new_attempt_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='public_admin_comment_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='public_admin_imageannotationcomment_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='public_examiner_comment_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='public_examiner_imageannotationcomment_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='public_student_comment_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='public_student_file_upload_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='public_student_imageannotationcomment_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='public_total_comment_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='public_total_imageannotationcomment_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]