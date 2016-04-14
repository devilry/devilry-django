# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0018_auto_20160122_1712'),
        ('devilry_dbcache', '0003_auto_20160413_0216'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignmentgroupcacheddata',
            name='first_feedbackset',
            field=models.ForeignKey(related_name='+', blank=True, to='devilry_group.FeedbackSet', null=True),
        ),
    ]
