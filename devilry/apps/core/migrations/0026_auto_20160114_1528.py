# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20160114_1525'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='examiner',
            unique_together=set([('relatedexaminer', 'assignmentgroup')]),
        ),
    ]
