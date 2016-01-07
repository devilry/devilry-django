# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0006_auto_20160107_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupcomment',
            name='part_of_grading',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='groupcomment',
            name='visibility',
            field=models.CharField(default=b'visible-to-everyone', max_length=100, choices=[(b'visible-to-examiner-and-admins', b'Visible to examiners and admins'), (b'visible-to-everyone', b'Visible to everyone')]),
        ),
        migrations.AddField(
            model_name='imageannotationcomment',
            name='part_of_grading',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='imageannotationcomment',
            name='visibility',
            field=models.CharField(default=b'visible-to-everyone', max_length=100, choices=[(b'visible-to-examiner-and-admins', b'Visible to examiners and admins'), (b'visible-to-everyone', b'Visible to everyone')]),
        ),
    ]
