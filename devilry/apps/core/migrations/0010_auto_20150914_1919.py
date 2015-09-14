# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20150914_1914'),
        ('devilry_account', '0002_datamigrate_auth_user_to_devilry_account_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examiner',
            name='user',
            field=models.ForeignKey(to='devilry_account.User'),
        ),
    ]
