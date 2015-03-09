# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeadlineTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('tag', models.CharField(max_length=30, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeriodTag',
            fields=[
                ('period', models.OneToOneField(primary_key=True, serialize=False, to='core.Period')),
                ('deadlinetag', models.ForeignKey(to='devilry_qualifiesforexam.DeadlineTag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QualifiesForFinalExam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qualifies', models.NullBooleanField()),
                ('relatedstudent', models.ForeignKey(to='core.RelatedStudent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SlugField(max_length=30, choices=[(b'ready', 'Ready for export'), (b'almostready', 'Most students are ready for export'), (b'notready', 'Not ready for export (retracted)')])),
                ('createtime', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(blank=True)),
                ('plugin', models.CharField(max_length=500, null=True, blank=True)),
                ('exported_timestamp', models.DateTimeField(null=True, blank=True)),
                ('period', models.ForeignKey(related_name='qualifiedforexams_status', to='core.Period')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-createtime'],
                'verbose_name': 'Qualified for final exam status',
                'verbose_name_plural': 'Qualified for final exam statuses',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='qualifiesforfinalexam',
            name='status',
            field=models.ForeignKey(related_name='students', to='devilry_qualifiesforexam.Status'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='qualifiesforfinalexam',
            unique_together=set([('relatedstudent', 'status')]),
        ),
    ]
