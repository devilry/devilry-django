# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0005_auto_20160107_0958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackset',
            name='gradeform_data_json',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
