# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_datamigrate_anonymous_to_anonymizationmode'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assignment',
            old_name='anonymous',
            new_name='deprecated_field_anonymous',
        ),
    ]
