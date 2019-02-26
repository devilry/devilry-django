# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_comment', '0003_auto_20160109_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentfile',
            name='created_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
