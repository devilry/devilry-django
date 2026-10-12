# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cradmin_imagearchive', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='archiveimage',
            name='file_size',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
