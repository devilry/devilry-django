# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0013_auto_20160110_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedbackset',
            name='grading_status',
            field=models.CharField(default='grading_status_first_try', max_length=50, db_index=True, choices=[('grading_status_first_try', 'grading_status_first_try'), ('grading_status_new_try', 'grading_status_new_try'), ('grading_status_re_edit', 'grading_status_re_edit')]),
        ),
    ]
