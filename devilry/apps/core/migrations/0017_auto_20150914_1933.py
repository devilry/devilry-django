# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20150914_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relatedexaminer',
            name='user',
            field=models.PositiveIntegerField(help_text=b'The related user.'),
        ),
        migrations.AlterField(
            model_name='relatedstudent',
            name='user',
            field=models.PositiveIntegerField(help_text=b'The related user.'),
        ),
    ]
