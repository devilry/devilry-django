# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_dbcache', '0004_assignmentgroupcacheddata_first_feedbackset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='first_feedbackset',
            field=models.ForeignKey(related_name='+', default=1, to='devilry_group.FeedbackSet'),
            preserve_default=False,
        ),
    ]
