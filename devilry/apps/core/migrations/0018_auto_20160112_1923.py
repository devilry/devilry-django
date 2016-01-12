# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_candidate_relatedstudent_replaces_student_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='old_reference_not_in_use_student',
            field=models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='relatedstudent',
            field=models.ForeignKey(to='core.RelatedStudent'),
        ),
    ]
