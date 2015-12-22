# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20151112_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='parentnode',
            field=models.ForeignKey(related_name='subjects', blank=True, to='core.Node', null=True),
        ),
    ]
