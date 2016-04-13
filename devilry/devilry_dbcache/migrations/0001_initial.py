# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0018_auto_20160122_1712'),
        ('core', '0028_auto_20160119_0337'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentGroupCachedData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.OneToOneField(to='core.AssignmentGroup')),
                ('last_feedbackset', models.ForeignKey(related_name='+', to='devilry_group.FeedbackSet')),
                ('last_published_feedbackset', models.ForeignKey(related_name='+', to='devilry_group.FeedbackSet')),
            ],
        ),
    ]
