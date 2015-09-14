# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20150914_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deadline',
            name='added_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='devilry_account.User', null=True),
        ),
    ]
