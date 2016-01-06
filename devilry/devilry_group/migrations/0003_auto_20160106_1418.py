# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0002_feedbackset_gradeform_json'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackset',
            name='points',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='feedbackset',
            name='published_by',
            field=models.ForeignKey(related_name='published_feedbacksets', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
