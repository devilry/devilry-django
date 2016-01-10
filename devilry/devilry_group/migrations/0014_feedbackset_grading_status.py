# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0013_auto_20160110_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedbackset',
            name='grading_status',
            field=models.CharField(default=b'grading_status_first_try', max_length=50, db_index=True, choices=[(b'grading_status_first_try', b'grading_status_first_try'), (b'grading_status_new_try', b'grading_status_new_try'), (b'grading_status_re_edit', b'grading_status_re_edit')]),
        ),
    ]
