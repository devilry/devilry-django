# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_dbcache', '0005_auto_20160413_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentgroupcacheddata',
            name='first_feedbackset',
            field=models.ForeignKey(related_name='+', blank=True, to='devilry_group.FeedbackSet', null=True),
        ),
    ]
