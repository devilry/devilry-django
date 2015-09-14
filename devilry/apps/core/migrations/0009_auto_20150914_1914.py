# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150914_1905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examiner',
            name='user',
            field=models.PositiveIntegerField(),
        ),
    ]
