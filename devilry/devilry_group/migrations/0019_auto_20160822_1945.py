# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0018_auto_20160122_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackset',
            name='created_by',
            field=models.ForeignKey(related_name='created_feedbacksets', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
