import datetime

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webdemo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="subscribers",
            field=models.ManyToManyField(
                verbose_name="Subscribed users", to=settings.AUTH_USER_MODEL
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="page",
            name="publishing_time",
            field=models.DateTimeField(
                verbose_name="Publishing time",
                default=datetime.datetime(
                    2015, 12, 7, 2, 51, 14, 601552, tzinfo=datetime.timezone.utc
                ),
                help_text="The time when this will be visible on the website.",
            ),
            preserve_default=True,
        ),
    ]
