# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20160111_2021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='automatic_anonymous_id',
        ),
        migrations.RemoveField(
            model_name='examiner',
            name='automatic_anonymous_id',
        ),
    ]
