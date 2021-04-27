# Generated by Django 3.1.8 on 2021-04-27 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_message', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='message',
            name='status_data',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='message',
            name='virtual_message_receivers',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='messagereceiver',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='messagereceiver',
            name='status_data',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
