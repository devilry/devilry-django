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
            name='status',
            field=models.SlugField(max_length=30, choices=[(b'ready', 'Ready for export'), (b'almostready', 'Most students are ready for export'), (b'notready', 'Not ready for export (retracted)'), (b'in-progress', 'In progress')]),
        ),
    ]
