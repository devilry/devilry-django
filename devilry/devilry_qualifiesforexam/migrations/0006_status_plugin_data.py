# Generated by Django 4.2.7 on 2023-11-27 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_qualifiesforexam', '0005_deletedqualifiesforfinalexam'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='plugin_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
