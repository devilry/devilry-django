# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-06-30 01:09


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_comment', '0006_auto_20170621_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentfile',
            name='mimetype',
            field=models.CharField(max_length=255),
        ),
    ]
