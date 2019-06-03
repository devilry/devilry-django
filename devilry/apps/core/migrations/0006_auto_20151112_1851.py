# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_relatedexaminer_automatic_anonymous_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentgroup',
            name='name',
            field=models.CharField(default='', help_text='An optional name for the group. Typically used a project name on project assignments.', max_length=30, blank=True),
        ),
    ]
