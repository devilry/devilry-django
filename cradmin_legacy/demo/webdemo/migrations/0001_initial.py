import datetime

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cradmin_imagearchive', '0003_auto_20151017_0139'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Page",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        verbose_name="ID",
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(verbose_name="Title", max_length=100)),
                (
                    "intro",
                    models.TextField(
                        verbose_name="Intro", help_text="A short introduction."
                    ),
                ),
                (
                    "attachment",
                    models.FileField(
                        null=True, verbose_name="Attachment", upload_to="", blank=True
                    ),
                ),
                ("body", models.TextField(verbose_name="Body")),
                (
                    "publishing_time",
                    models.DateTimeField(
                        default=datetime.datetime(
                            2015, 12, 7, 2, 45, 9, 26449, tzinfo=datetime.timezone.utc
                        ),
                        verbose_name="Publishing time",
                        help_text="The time when this will be visible on the website.",
                    ),
                ),
                (
                    "unpublish_time",
                    models.DateTimeField(
                        default=None,
                        null=True,
                        help_text="Hide the item on the website after this time.",
                        verbose_name="Unpublish time",
                        blank=True,
                    ),
                ),
                (
                    "internal_notes",
                    models.TextField(
                        default="",
                        help_text="Put internal notes here. Will not be visible on the website.",
                        verbose_name="Internal notes",
                        blank=True,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        null=True,
                        verbose_name="Image",
                        blank=True,
                        to="cradmin_imagearchive.ArchiveImage",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Pages",
                "ordering": ("title", "intro"),
                "verbose_name": "Page",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PageTag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        verbose_name="ID",
                        serialize=False,
                    ),
                ),
                ("tag", models.SlugField()),
                (
                    "page",
                    models.ForeignKey(
                        to="webdemo.Page", related_name="tags", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Site",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        verbose_name="ID",
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(default="", blank=True)),
                ("admins", models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="page",
            name="site",
            field=models.ForeignKey(to="webdemo.Site", on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
