import os
import posixpath
import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy

from cradmin_legacy import crsettings


def archiveimage_upload_to(archiveimage, filename):
    if archiveimage.id is None:
        raise ValueError("Can not set image until after the ArchiveImage object has been created.")
    name, extension = os.path.splitext(filename)
    filenamepattern = getattr(
        settings, "CRADMIN_LEGACY_IMAGEARCHIVE_FILENAMEPATTERN", "cradmin_imagearchive_images/{id}-{uuid}{extension}"
    )
    return filenamepattern.format(id=archiveimage.id, uuid=uuid.uuid1(), extension=extension)


class ArchiveImageManager(models.Manager):
    def filter_owned_by_role(self, role):
        return self.get_queryset().filter(
            role_object_id=role.id, role_content_type=ContentType.objects.get_for_model(role.__class__)
        )


class ArchiveImage(models.Model):
    objects = ArchiveImageManager()

    role_content_type = models.ForeignKey(
        ContentType,
        verbose_name=gettext_lazy("role"),
        help_text=gettext_lazy("The role owning this image."),
        on_delete=models.CASCADE,
    )
    role_object_id = models.PositiveIntegerField()
    role = GenericForeignKey("role_content_type", "role_object_id")

    #: The image.
    image = models.ImageField(
        max_length=255,
        null=True,
        blank=False,
        height_field="image_height",
        width_field="image_width",
        verbose_name=gettext_lazy("image"),
        help_text=gettext_lazy("Select an image to add to the archive."),
        upload_to=archiveimage_upload_to,
    )

    #: The height of the :obj:`.image`. Autopopulated by the :obj:`.image` field.
    image_height = models.IntegerField(null=True, blank=True, editable=False)

    #: The width of the :obj:`.image`. Autopopulated by the :obj:`.image` field.
    image_width = models.IntegerField(null=True, blank=True, editable=False)

    #: The file extension
    file_extension = models.CharField(max_length=255, blank=False, null=False, editable=False)

    #: The file size in bytes.
    file_size = models.PositiveIntegerField(blank=True, null=True)

    #: The name of the image file.
    #:
    #: Can be None. This is both because this was added
    #: after cradmin was in use in production, and because
    #: calculating size can be expensive if uploading
    #: huge amounts of images in bulk. All the cradmin views
    #: provided by the app sets this.
    name = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        verbose_name=gettext_lazy("name"),
        # help_text=gettext_lazy('A good name helps search engines find the image, '
        #             'and it helps visually impaired users.')
    )

    #: An optional description of the image.
    description = models.TextField(
        blank=True,
        null=False,
        default="",
        verbose_name=gettext_lazy("description"),
        help_text=gettext_lazy(
            "An optional description of the image. Think if this as a description "
            "of the image for visually impaired users. This means that you should describe "
            "the information carried in the image (if any). A good description also helps "
            "search engines find the image."
        ),
    )

    #: Create datetime.
    created_datetime = models.DateTimeField(editable=False, auto_now_add=True)

    class Meta:
        verbose_name = gettext_lazy("archive image")
        verbose_name_plural = gettext_lazy("archive images")

    def clean(self):
        if not self.name:
            if self.image:
                self.name = os.path.splitext(posixpath.basename(self.image.name))[0]
        if self.name:
            self.file_extension = os.path.splitext(self.name)[1]

    def __str__(self):
        return self.name

    def __repr__(self):
        return "ArchiveImage(name={name}, image_width={image_width}, image_height={image_height})".format(
            name=self.name.encode("ascii", "replace"), image_width=self.image_width, image_height=self.image_height
        )

    def get_preview_html(self, request, imagetype=None):
        """
        Get HTML that can be used to show a preview of the image.

        Parameters:
            request: A HttpRequest object which is used to create an
                absolute URI for the image.
        """
        if not imagetype:
            imagetype = crsettings.get_setting("CRADMIN_LEGACY_IMAGEARCHIVE_PREVIEW_IMAGETYPE")
        context = {"archiveimage": self, "imagetype": imagetype, "fallbackoptions": {"width": 300, "height": 300}}
        return render_to_string(
            "cradmin_legacy/apps/cradmin_imagearchive/preview.django.html", context, request=request
        )

    @property
    def screenreader_text(self):
        """
        Get screen reader text for the image. Typically added to the "alt"
        or "aria-label" HTML attributes.

        Defaults to description, but falls back to name.
        """
        if self.description:
            return self.description
        else:
            return self.name
