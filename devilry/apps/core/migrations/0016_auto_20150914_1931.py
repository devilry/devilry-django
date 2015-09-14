# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20150914_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupinvite',
            name='sent_by',
            field=models.ForeignKey(related_name='groupinvite_sent_by_set', to='devilry_account.User'),
        ),
        migrations.AlterField(
            model_name='groupinvite',
            name='sent_to',
            field=models.ForeignKey(related_name='groupinvite_sent_to_set', to='devilry_account.User'),
        ),
    ]
