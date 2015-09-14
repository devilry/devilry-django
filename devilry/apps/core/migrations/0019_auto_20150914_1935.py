# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20150914_1933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticfeedback',
            name='saved_by',
            field=models.PositiveIntegerField(help_text=b'The user (examiner) who saved this feedback'),
        ),
    ]
