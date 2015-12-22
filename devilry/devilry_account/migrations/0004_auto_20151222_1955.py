# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_account', '0003_datamigrate-admins-into-permissiongroups'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='periodpermissiongroup',
            options={'verbose_name': 'Period permission group', 'verbose_name_plural': 'Period permission groups'},
        ),
        migrations.AlterModelOptions(
            name='subjectpermissiongroup',
            options={'verbose_name': 'Subject permission group', 'verbose_name_plural': 'Subject permission groups'},
        ),
    ]
