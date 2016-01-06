# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20151112_1851'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='gradeform_setup_json',
            field=models.TextField(null=True, blank=True),
        ),
    ]
