# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cradmin_temporaryfileuploadstore', '0002_temporaryfilecollection_singlemode'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporaryfilecollection',
            name='max_filesize_bytes',
            field=models.PositiveIntegerField(null=True, default=None),
            preserve_default=True,
        ),
    ]
