# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0016_auto_20160114_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackset',
            name='feedbackset_type',
            field=models.CharField(default=b'first_attempt', max_length=50, db_index=True, choices=[(b'first_attempt', b'first attempt'), (b'new_attempt', b'new attempt'), (b're_edit', b're edit')]),
        ),
    ]
