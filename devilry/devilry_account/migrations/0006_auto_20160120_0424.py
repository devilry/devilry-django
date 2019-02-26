# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_account', '0005_auto_20160113_2037'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='periodpermissiongroup',
            options={'verbose_name': 'Semester permission group', 'verbose_name_plural': 'Semester permission groups'},
        ),
        migrations.AlterModelOptions(
            name='subjectpermissiongroup',
            options={'verbose_name': 'Course permission group', 'verbose_name_plural': 'Course permission groups'},
        ),
    ]
