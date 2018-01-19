# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import detektor.parseresult
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompareTwoCacheItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scaled_points', models.IntegerField()),
                ('summary_json', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='DetektorAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'unprocessed', max_length=12, choices=[(b'unprocessed', b'unprocessed'), (b'running', b'running'), (b'finished', b'finished')])),
                ('processing_started_datetime', models.DateTimeField(null=True, blank=True)),
                ('assignment', models.OneToOneField(to='core.Assignment')),
                ('processing_started_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DetektorAssignmentCacheLanguage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=255, db_index=True)),
                ('detektorassignment', models.ForeignKey(related_name='cachelanguages', to='devilry_detektor.DetektorAssignment')),
            ],
            options={
                'ordering': ['language'],
            },
        ),
        migrations.CreateModel(
            name='DetektorDeliveryParseResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=255, db_index=True)),
                ('operators_string', models.TextField()),
                ('keywords_string', models.TextField()),
                ('number_of_operators', models.IntegerField()),
                ('number_of_keywords', models.IntegerField()),
                ('operators_and_keywords_string', models.TextField()),
                ('normalized_sourcecode', models.TextField(null=True, blank=True)),
                ('parsed_functions_json', models.TextField(null=True, blank=True)),
                ('delivery', models.ForeignKey(to='core.Delivery')),
                ('detektorassignment', models.ForeignKey(related_name='parseresults', to='devilry_detektor.DetektorAssignment')),
            ],
            bases=(models.Model, detektor.parseresult.ParseResult),
        ),
        migrations.AddField(
            model_name='comparetwocacheitem',
            name='language',
            field=models.ForeignKey(related_name='comparetwo_cacheitems', to='devilry_detektor.DetektorAssignmentCacheLanguage'),
        ),
        migrations.AddField(
            model_name='comparetwocacheitem',
            name='parseresult1',
            field=models.ForeignKey(related_name='+', to='devilry_detektor.DetektorDeliveryParseResult'),
        ),
        migrations.AddField(
            model_name='comparetwocacheitem',
            name='parseresult2',
            field=models.ForeignKey(related_name='+', to='devilry_detektor.DetektorDeliveryParseResult'),
        ),
        migrations.AlterUniqueTogether(
            name='detektordeliveryparseresult',
            unique_together=set([('delivery', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='detektorassignmentcachelanguage',
            unique_together=set([('detektorassignment', 'language')]),
        ),
    ]
