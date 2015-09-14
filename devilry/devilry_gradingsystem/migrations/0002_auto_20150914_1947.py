# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_gradingsystem', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackdraft',
            name='saved_by',
            field=models.ForeignKey(related_name='devilry_gradingsystem_feedbackdraft_set', to='devilry_account.User'),
        ),
        migrations.AlterField(
            model_name='feedbackdraftfile',
            name='saved_by',
            field=models.ForeignKey(related_name='+', to='devilry_account.User'),
        ),
    ]
