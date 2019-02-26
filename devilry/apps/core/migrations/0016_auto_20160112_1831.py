# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_assignment_uses_custom_candidate_ids'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='student',
            new_name='old_reference_not_in_use_student',
        ),
    ]
