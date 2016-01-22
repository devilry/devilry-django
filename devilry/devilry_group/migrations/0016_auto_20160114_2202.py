# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0015_auto_20160111_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackset',
            name='feedbackset_type',
            field=models.CharField(default=b'feedbackset_type_first_attempt', max_length=50, db_index=True, choices=[(b'feedbackset_type_first_attempt', b'Feedbackset_type_first_try'), (b'feedbackset_type_new_attempt', b'feedbackset_type_new_attempt'), (b'feedbackset_type_re_edit', b'feedbackset_type_re_edit')]),
        ),
        migrations.AlterField(
            model_name='groupcomment',
            name='visibility',
            field=models.CharField(default=b'visible-to-everyone', max_length=50, db_index=True, choices=[(b'private', b'Private'), (b'visible-to-examiner-and-admins', b'Visible to examiners and admins'), (b'visible-to-everyone', b'Visible to everyone')]),
        ),
        migrations.AlterField(
            model_name='imageannotationcomment',
            name='visibility',
            field=models.CharField(default=b'visible-to-everyone', max_length=50, db_index=True, choices=[(b'private', b'Private'), (b'visible-to-examiner-and-admins', b'Visible to examiners and admins'), (b'visible-to-everyone', b'Visible to everyone')]),
        ),
    ]
