# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0004_auto_20160107_0918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackset',
            name='gradeform_data_json',
            field=models.TextField(default=b''),
        ),
    ]
