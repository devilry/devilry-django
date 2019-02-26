# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0017_auto_20160122_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackset',
            name='created_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
