# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20150914_1924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deadline',
            name='added_by',
            field=models.PositiveIntegerField(default=None, null=True, blank=True),
        ),
    ]
