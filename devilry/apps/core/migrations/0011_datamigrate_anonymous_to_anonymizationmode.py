# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def datamigrate_anonymous_to_anonymizationmode(apps, schema_editor):
    assignment_model = apps.get_model('core', 'Assignment')
    assignment_model.objects\
        .filter(anonymous=True)\
        .update(anonymizationmode='semi_anonymous')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_assignment_anonymizationmode'),
    ]

    operations = [
        migrations.RunPython(datamigrate_anonymous_to_anonymizationmode)
    ]
