# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20160114_1520'),
    ]

    operations = [
        migrations.RenameField(
            model_name='examiner',
            old_name='user',
            new_name='old_reference_not_in_use_user',
        ),
    ]
