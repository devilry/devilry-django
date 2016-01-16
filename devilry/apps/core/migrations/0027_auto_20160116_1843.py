# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20160114_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='grading_system_plugin_id',
            field=models.CharField(default=b'devilry_gradingsystemplugin_approved', max_length=300, null=True, blank=True, choices=[(b'devilry_gradingsystemplugin_approved', 'PASSED/FAILED. The examiner selects passed or failed.'), (b'devilry_gradingsystemplugin_points', 'POINTS. The examiner types in the number of points to award the student(s) for this assignment.'), (b'schema', 'SCHEMA. The examiner fill in a schema defined by you.')]),
        ),
    ]
