# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0011_auto_20160107_1111'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupcomment',
            name='instant_publish',
        ),
        migrations.RemoveField(
            model_name='groupcomment',
            name='visible_for_students',
        ),
        migrations.RemoveField(
            model_name='imageannotationcomment',
            name='instant_publish',
        ),
        migrations.RemoveField(
            model_name='imageannotationcomment',
            name='visible_for_students',
        ),
    ]
