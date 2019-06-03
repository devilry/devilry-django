# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20160112_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='uses_custom_candidate_ids',
            field=models.BooleanField(default=False, help_text='If this is enabled, the assignment does not inherit candidate IDs from the semester, and instead have their own set of candidate IDs only for this assignment.'),
        ),
    ]
