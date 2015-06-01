# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150601_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='feedback_workflow',
            field=models.CharField(default=b'', max_length=50, verbose_name='Feedback workflow', blank=True, choices=[(b'', 'Simple - Examiners write feedback, and publish it whenever they want. Does not handle coordination of multiple examiners at all.'), (b'trusted-cooperative-feedback-editing', 'Trusted cooperative feedback editing - Examiners can only save feedback drafts. Examiners share the same feedback drafts, which means that one examiner can start writing feedback and another can continue. When an administrator is notified by their examiners that they have finished correcting, they can publish the drafts via the administrator UI. If you want one examiner to do the bulk of the work, and just let another examiner read it over and adjust the feedback, make the first examiner the only examiner, and reassign the students to the other examiner when the first examiner is done.')]),
            preserve_default=True,
        ),
    ]
