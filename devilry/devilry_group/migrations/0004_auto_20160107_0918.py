# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0003_auto_20160106_1418'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feedbackset',
            old_name='gradeform_json',
            new_name='gradeform_data_json',
        ),
        migrations.RenameField(
            model_name='feedbackset',
            old_name='points',
            new_name='grading_points',
        ),
        migrations.RenameField(
            model_name='feedbackset',
            old_name='published_by',
            new_name='grading_published_by',
        ),
        migrations.RenameField(
            model_name='feedbackset',
            old_name='published_datetime',
            new_name='grading_published_datetime',
        ),
    ]
