# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20160119_0337'),
        ('devilry_group', '0019_auto_20160822_1945'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentGroupCachedData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feedbackset_count', models.PositiveIntegerField(default=0)),
                ('public_total_comment_count', models.PositiveIntegerField()),
                ('public_student_comment_count', models.PositiveIntegerField()),
                ('public_examiner_comment_count', models.PositiveIntegerField()),
                ('public_admin_comment_count', models.PositiveIntegerField()),
                ('public_total_imageannotationcomment_count', models.PositiveIntegerField()),
                ('public_student_imageannotationcomment_count', models.PositiveIntegerField()),
                ('public_examiner_imageannotationcomment_count', models.PositiveIntegerField()),
                ('public_admin_imageannotationcomment_count', models.PositiveIntegerField()),
                ('file_upload_count_total', models.PositiveIntegerField()),
                ('file_upload_count_student', models.PositiveIntegerField()),
                ('file_upload_count_examiner', models.PositiveIntegerField(default=0)),
                ('first_feedbackset', models.ForeignKey(related_name='+', blank=True, to='devilry_group.FeedbackSet', null=True)),
                ('group', models.OneToOneField(related_name='cached_data', to='core.AssignmentGroup')),
                ('last_feedbackset', models.ForeignKey(related_name='+', blank=True, to='devilry_group.FeedbackSet', null=True)),
                ('last_published_feedbackset', models.ForeignKey(related_name='+', blank=True, to='devilry_group.FeedbackSet', null=True)),
            ],
        ),
    ]
