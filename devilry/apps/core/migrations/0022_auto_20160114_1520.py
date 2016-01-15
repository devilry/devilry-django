# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_examiner_relatedexaminer_replaces_user_field'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='examiner',
            unique_together=set([]),
        ),
    ]
