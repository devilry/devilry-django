# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0009_auto_20160107_1100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupcomment',
            name='part_of_grading',
        ),
        migrations.RemoveField(
            model_name='groupcomment',
            name='visibility',
        ),
        migrations.RemoveField(
            model_name='imageannotationcomment',
            name='part_of_grading',
        ),
        migrations.RemoveField(
            model_name='imageannotationcomment',
            name='visibility',
        ),
    ]
