# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20150914_1935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticfeedback',
            name='saved_by',
            field=models.ForeignKey(help_text=b'The user (examiner) who saved this feedback', to='devilry_account.User'),
        ),
    ]
