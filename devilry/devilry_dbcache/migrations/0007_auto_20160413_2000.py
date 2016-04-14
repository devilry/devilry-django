# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_dbcache', '0006_auto_20160413_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='last_feedbackset',
            field=models.ForeignKey(related_name='+', blank=True, to='devilry_group.FeedbackSet', null=True),
        ),
    ]
