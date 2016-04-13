# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_dbcache', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='group',
            field=models.OneToOneField(related_name='cached_data', to='core.AssignmentGroup'),
        ),
    ]
