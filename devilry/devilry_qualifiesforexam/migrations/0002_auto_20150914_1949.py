# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_qualifiesforexam', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='user',
            field=models.ForeignKey(to='devilry_account.User'),
        ),
    ]
