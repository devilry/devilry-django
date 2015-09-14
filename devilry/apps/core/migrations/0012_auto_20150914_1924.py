# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20150914_1924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='student',
            field=models.ForeignKey(to='devilry_account.User'),
        ),
    ]
