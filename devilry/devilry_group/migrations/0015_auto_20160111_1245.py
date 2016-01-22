# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0014_feedbackset_grading_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedbackset',
            name='grading_status',
        ),
        migrations.AddField(
            model_name='feedbackset',
            name='feedbackset_type',
            field=models.CharField(default=b'feedbackset_type_first_attempt', max_length=50, db_index=True, choices=[(b'feedbackset_type_first_attempt', b'feedbackset_type_first_attempt'), (b'feedbackset_type_new_attempt', b'feedbackset_type_new_attempt'), (b'feedbackset_type_re_edit', b'feedbackset_type_re_edit')]),
        ),
    ]
