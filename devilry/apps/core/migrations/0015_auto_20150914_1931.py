# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20150914_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupinvite',
            name='sent_by',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='groupinvite',
            name='sent_to',
            field=models.PositiveIntegerField(),
        ),
    ]
