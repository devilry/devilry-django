# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_assignment_examiners_publish_feedbacks_directly'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='feedback_workflow',
            field=models.CharField(default=b'', max_length=30, verbose_name='Feedback workflow', blank=True, choices=[(b'', 'Simple - Examiners write feedback, and publish it whenever they want. Does not handle coordination of multiple examiners at all.'), (b'bulk-publish', 'Administrator publish in bulk - Examiners can only save feedback drafts. When an administrator is notified by their examiners that they have finished correcting, they can publish the drafts via the administrator UI.')]),
            preserve_default=True,
        ),
    ]
