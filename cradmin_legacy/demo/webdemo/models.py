from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy

from cradmin_legacy.apps.cradmin_imagearchive import models as imagearchivemodels


class Site(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=False, blank=True, default="")
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.name


class Page(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name=gettext_lazy("Title"))
    intro = models.TextField(verbose_name=gettext_lazy("Intro"), help_text=gettext_lazy("A short introduction."))
    image = models.ForeignKey(
        imagearchivemodels.ArchiveImage,
        verbose_name=gettext_lazy("Image"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    attachment = models.FileField(verbose_name=gettext_lazy("Attachment"), null=True, blank=True)
    body = models.TextField(verbose_name=gettext_lazy("Body"))
    publishing_time = models.DateTimeField(
        verbose_name=gettext_lazy("Publishing time"),
        default=timezone.now,
        blank=False,
        null=False,
        help_text=gettext_lazy("The time when this will be visible on the website."),
    )
    unpublish_time = models.DateTimeField(
        verbose_name=gettext_lazy("Unpublish time"),
        default=None,
        blank=True,
        null=True,
        help_text=gettext_lazy("Hide the item on the website after this time."),
    )
    internal_notes = models.TextField(
        verbose_name=gettext_lazy("Internal notes"),
        help_text=gettext_lazy("Put internal notes here. Will not be visible on the website."),
        blank=True,
        null=False,
        default="",
    )
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, verbose_name=gettext_lazy("Subscribed users")
    )
    starred = models.CharField(
        default="no",
        max_length=3,
        choices=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = gettext_lazy("Page")
        verbose_name_plural = gettext_lazy("Pages")
        ordering = ("title", "intro")


class PageTag(models.Model):
    page = models.ForeignKey(Page, related_name="tags", on_delete=models.CASCADE)
    tag = models.SlugField()

    def __str__(self):
        return self.tag
