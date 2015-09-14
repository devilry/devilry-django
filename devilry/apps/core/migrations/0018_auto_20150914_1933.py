# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20150914_1933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relatedexaminer',
            name='user',
            field=models.ForeignKey(help_text=b'The related user.', to='devilry_account.User'),
        ),
        migrations.AlterField(
            model_name='relatedstudent',
            name='user',
            field=models.ForeignKey(help_text=b'The related user.', to='devilry_account.User'),
        ),
    ]
