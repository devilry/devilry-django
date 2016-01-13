# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_account', '0004_auto_20151222_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permissiongroup',
            name='grouptype',
            field=models.CharField(help_text='Course and semester administrator groups can only be assigned to a single course or semester. Department administrator groups can be assigned to multiple courses. You can not change this for existing permission groups.', max_length=30, verbose_name='Permission group type', choices=[(b'departmentadmin', 'Department administrator group'), (b'subjectadmin', 'Course administrator group'), (b'periodadmin', 'Semester administrator group')]),
        ),
    ]
