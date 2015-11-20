# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_examiner_relatedexaminer'),
    ]

    operations = [
        migrations.AddField(
            model_name='relatedexaminer',
            name='automatic_anonymous_id',
            field=models.CharField(default=b'', max_length=255, editable=False, blank=True),
        ),
    ]
