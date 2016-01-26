# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_comment', '0004_commentfile_created_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='published_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
