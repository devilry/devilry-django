# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cradmin_temporaryfileuploadstore', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporaryfilecollection',
            name='singlemode',
            field=models.BooleanField(help_text='If this is True, only a single file can be added to the collection. This means that the last file added to the collection will be the only file in the collection.', default=False),
            preserve_default=True,
        ),
    ]
