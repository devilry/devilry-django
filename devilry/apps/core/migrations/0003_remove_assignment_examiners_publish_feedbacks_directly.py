# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_deadline_feedbacks_published'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='examiners_publish_feedbacks_directly',
        ),
    ]
