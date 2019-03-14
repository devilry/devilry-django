# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0015_auto_20160111_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackset',
            name='feedbackset_type',
            field=models.CharField(default='feedbackset_type_first_attempt', max_length=50, db_index=True, choices=[('feedbackset_type_first_attempt', 'Feedbackset_type_first_try'), ('feedbackset_type_new_attempt', 'feedbackset_type_new_attempt'), ('feedbackset_type_re_edit', 'feedbackset_type_re_edit')]),
        ),
        migrations.AlterField(
            model_name='groupcomment',
            name='visibility',
            field=models.CharField(default='visible-to-everyone', max_length=50, db_index=True, choices=[('private', 'Private'), ('visible-to-examiner-and-admins', 'Visible to examiners and admins'), ('visible-to-everyone', 'Visible to everyone')]),
        ),
        migrations.AlterField(
            model_name='imageannotationcomment',
            name='visibility',
            field=models.CharField(default='visible-to-everyone', max_length=50, db_index=True, choices=[('private', 'Private'), ('visible-to-examiner-and-admins', 'Visible to examiners and admins'), ('visible-to-everyone', 'Visible to everyone')]),
        ),
    ]
