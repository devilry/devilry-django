# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20150914_1935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='admins',
            field=models.ManyToManyField(to='devilry_account.User', verbose_name=b'Administrators', blank=True),
        ),
        migrations.AlterField(
            model_name='node',
            name='admins',
            field=models.ManyToManyField(to='devilry_account.User', blank=True),
        ),
        migrations.AlterField(
            model_name='period',
            name='admins',
            field=models.ManyToManyField(to='devilry_account.User', blank=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='admins',
            field=models.ManyToManyField(to='devilry_account.User', blank=True),
        ),
    ]
