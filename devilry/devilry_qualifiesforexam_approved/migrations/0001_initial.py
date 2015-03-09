# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_qualifiesforexam', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SelectedAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assignment', models.ForeignKey(to='core.Assignment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubsetPluginSetting',
            fields=[
                ('status', models.OneToOneField(related_name='devilry_qualifiesforexam_approved_subsetpluginsetting', primary_key=True, serialize=False, to='devilry_qualifiesforexam.Status')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='selectedassignment',
            name='subset',
            field=models.ForeignKey(to='devilry_qualifiesforexam_approved.SubsetPluginSetting'),
            preserve_default=True,
        ),
    ]
