# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cradmin_temporaryfileuploadstore', '0003_temporaryfilecollection_max_filesize_bytes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temporaryfilecollection',
            name='max_filesize_bytes',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
            preserve_default=True,
        ),
    ]
