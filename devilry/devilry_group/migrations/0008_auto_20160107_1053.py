# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0007_auto_20160107_1031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupcomment',
            name='visibility',
            field=models.CharField(default=b'visible-to-everyone', max_length=100, db_index=True, choices=[(b'visible-to-examiner-and-admins', b'Visible to examiners and admins'), (b'visible-to-everyone', b'visible-to-everyone')]),
        ),
        migrations.AlterField(
            model_name='imageannotationcomment',
            name='visibility',
            field=models.CharField(default=b'visible-to-everyone', max_length=100, db_index=True, choices=[(b'visible-to-examiner-and-admins', b'Visible to examiners and admins'), (b'visible-to-everyone', b'visible-to-everyone')]),
        ),
    ]
