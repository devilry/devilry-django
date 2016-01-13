# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20160112_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='anonymizationmode',
            field=models.CharField(default=b'off', max_length=15, verbose_name='Anonymization mode', db_index=True, choices=[(b'off', 'OFF. Normal assignment where semester and course admins can see everything, and examiners and students can see each others names and contact information.'), (b'semi_anonymous', 'SEMI ANONYMOUS. Students and examiners can not see information about each other. Comments added by course admins are not anonymized. Semester admins do not have access to the assignment in the admin UI. Course admins have the same permissions as for "OFF".'), (b'fully_anonymous', 'FULLY ANONYMIZED. Intended for exams where course admins are examiners. Students and examiners can not see information about each other. Hidden from semester admins. Course admins can not view grading details. Only departmentadmins and superusers can change this back to another "anoymization mode" when feedback has been added to the assignment. Course admins can not edit examiners after the first feedback is provided.')]),
        ),
    ]
