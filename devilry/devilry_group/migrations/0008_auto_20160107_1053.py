# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0007_auto_20160107_1031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupcomment',
            name='visibility',
            field=models.CharField(default='visible-to-everyone', max_length=100, db_index=True, choices=[('visible-to-examiner-and-admins', 'Visible to examiners and admins'), ('visible-to-everyone', 'visible-to-everyone')]),
        ),
        migrations.AlterField(
            model_name='imageannotationcomment',
            name='visibility',
            field=models.CharField(default='visible-to-everyone', max_length=100, db_index=True, choices=[('visible-to-examiner-and-admins', 'Visible to examiners and admins'), ('visible-to-everyone', 'visible-to-everyone')]),
        ),
    ]
