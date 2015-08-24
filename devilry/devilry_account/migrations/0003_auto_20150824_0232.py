# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_account', '0002_datamigrate_auth_user_to_devilry_account_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='shortname',
            field=models.CharField(help_text='The short name for the user. This is set automatically to the email or username depending on the method used for authentication.', unique=True, max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='useremail',
            name='is_primary',
            field=models.NullBooleanField(help_text='Your primary email is the email address used when we need to display a single email address.', verbose_name='Is this your primary email?', choices=[(None, 'No'), (True, 'Yes')]),
            preserve_default=True,
        ),
    ]
