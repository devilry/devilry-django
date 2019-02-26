# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20160113_2037'),
    ]

    operations = [
        migrations.AddField(
            model_name='relatedexaminer',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
