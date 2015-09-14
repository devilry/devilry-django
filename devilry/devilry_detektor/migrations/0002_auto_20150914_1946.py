# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_detektor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detektorassignment',
            name='processing_started_by',
            field=models.ForeignKey(blank=True, to='devilry_account.User', null=True),
        ),
    ]
