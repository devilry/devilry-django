# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20160114_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examiner',
            name='relatedexaminer',
            field=models.ForeignKey(to='core.RelatedExaminer'),
        ),
    ]
