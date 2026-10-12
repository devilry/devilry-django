import fnmatch
import math
import mimetypes
import os
import time
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import Storage, storages
from django.db import models
from django.utils.translation import gettext_lazy

from cradmin_legacy.utils import crhumanize


class TemporaryFileCollectionQuerySet(models.query.QuerySet):
    def filter_for_user(self, user):
        return self.filter(user=user)


class TemporaryFileCollectionManager(models.Manager):
    def get_queryset(self):
        return TemporaryFileCollectionQuerySet(self.model, using=self._db)

    def filter_for_user(self, user):
        return self.get_queryset().filter_for_user(user)


def html_input_accept_match(accept, mimetype, filename):
    filename = filename.lower()
    for pattern in accept.split(","):
        if "/" in pattern:
            if mimetype and fnmatch.fnmatch(mimetype, pattern):
                return True
        elif pattern.startswith("."):
            if os.path.splitext(filename)[1] == pattern:
                return True
        else:
            if fnmatch.fnmatch(filename, pattern):
                return True
    return False


def truncate_filename(filename, maxlength, ellipsis="..."):
    if len(filename) <= maxlength:
        return filename
    elif maxlength < 12:
        return filename[-maxlength:]
    else:
        max_length_noellipsis = maxlength - len(ellipsis)
        startlength = int(math.floor(max_length_noellipsis / 2.0))
        endlength = int(math.ceil(max_length_noellipsis / 2.0))
        start = filename[0:startlength]
        end = filename[-endlength:]
        return f"{start}{ellipsis}{end}"


def _make_unique_filename(filename_set, wanted_filename, generated_filename, max_filename_length, ellipsis):
    if generated_filename in filename_set:
        generated_uuid = str(uuid.uuid4())
        if max_filename_length:
            filename = truncate_filename(
                filename=wanted_filename, maxlength=max_filename_length - len(generated_uuid) - 1, ellipsis=ellipsis
            )
        else:
            filename = wanted_filename
        generated_filename = f"{generated_uuid}-{filename}"
        return _make_unique_filename(
            filename_set,
            wanted_filename=wanted_filename,
            generated_filename=generated_filename,
            max_filename_length=max_filename_length,
            ellipsis=ellipsis,
        )
    else:
        return generated_filename


def make_unique_filename(filename_set, wanted_filename, max_filename_length=None, ellipsis="..."):
    if (
        max_filename_length
        and max_filename_length < TemporaryFileCollection.MAX_FILENAME_LENGTH_MINVALUE_WITH_UNIQUE_FILENAMES
    ):
        raise ValueError("make_unique_filename requires max_filename_length to be at least 45.")
    else:
        return _make_unique_filename(
            filename_set=filename_set,
            wanted_filename=wanted_filename,
            generated_filename=wanted_filename,
            max_filename_length=max_filename_length,
            ellipsis=ellipsis,
        )


class TemporaryFileCollection(models.Model):
    """
    A collection of temporary files uploaded by a user.

    This model is used by apps to store temporary files
    uploaded through the temporary file upload API. The typical
    workflow is:

    1. Upload some files (a collection of files) file via the API.
    2. Use the IDs returned by the API to POST a form that uses
       file uploads.
    3. In the code handling the form POST request, retrieve the temporary
       file(s), move them into some form of persistent storage (perhaps
       after manipulating the file in some way).
    4. Delete the collection.

    The ``accept``, ``max_filename_length`` and ``prevent_filename_duplicates``
    attributes are set by the client. This means that you can not trust them
    and have to perform error checking when you process temporary files. This
    is not really a problem since:

    1. You should have error checking in the views that
       use TemporaryFileCollection.
    2. If you have error checking in your views, the only thing
       the user can do by manipulating the API call is to cause
       themselves a less user-friendly experience - they will typically
       get an error when they post the form containing the
       hidden field with the collection-id instead of when they upload
       a file.
    """

    #: Minimum value of ``max_filename_length`` when ``unique_filenames`` is ``True``.
    #: It is 45 because ``len(str(uuid.uuid4()))`` is 36, and we need some room over for
    #: the file extension.
    MAX_FILENAME_LENGTH_MINVALUE_WITH_UNIQUE_FILENAMES = 45

    objects = TemporaryFileCollectionManager()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text="The user that owns this temporary file. Users should not"
        "be allowed access to other users temporary files.",
        on_delete=models.CASCADE,
    )
    created_datetime = models.DateTimeField(auto_now_add=True)
    minutes_to_live = models.PositiveIntegerField(
        default=60,
        help_text="The number of minutes the app requests that this "
        "file collection should be kept before automatic removal. "
        "This is used by automatic cleanup jobs to determine "
        "what to delete. You should not rely on the file beeing "
        "automatically deleted after this number of minutes, and "
        "you should always delete files explicitly as part of the "
        "file upload process.",
    )
    accept = models.TextField(
        null=False,
        blank=True,
        default="",
        help_text="An html input field accept attribute formatted string. This is validated by the API on upload.",
    )
    max_filename_length = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        help_text="If specified, we shorten filenames to maximum the specified length. "
        "This is validated by the API on upload.",
    )
    unique_filenames = models.BooleanField(
        null=False,
        default=False,
        help_text="If this is True, we add random data when we "
        "detect duplicate filenames. The duplicate prevention "
        "algorithm handles max_filename."
        "This is validated by the API on upload.",
    )

    #: Max file size in bytes.
    max_filesize_bytes = models.PositiveIntegerField(null=True, default=None, blank=True)

    #: If this is True, only a single file can be added to the collection.
    #: This means that the last file added to the collection will be the
    #: only file in the collection.
    singlemode = models.BooleanField(
        null=False,
        default=False,
        help_text="If this is True, only a single file can be added to the "
        "collection. This means that the last file added to the "
        "collection will be the only file in the collection.",
    )

    def clear_files(self):
        for temporaryfile in self.files.all():
            temporaryfile.delete_object_and_file()

    def clear_files_and_delete(self):
        self.clear_files()
        self.delete()

    def is_supported_filetype(self, mimetype, filename):
        if self.accept:
            return html_input_accept_match(self.accept, mimetype, filename)
        else:
            return True

    def get_filename_set(self):
        return set(self.files.values_list("filename", flat=True))

    def clean(self):
        if self.max_filename_length and self.unique_filenames:
            if self.max_filename_length < self.MAX_FILENAME_LENGTH_MINVALUE_WITH_UNIQUE_FILENAMES:
                raise ValidationError(
                    "max_filename_length must be at least {} when unique_filenames is True".format(
                        self.MAX_FILENAME_LENGTH_MINVALUE_WITH_UNIQUE_FILENAMES
                    )
                )


def temporary_file_upload_to(instance, filename):
    filename, extension = os.path.splitext(filename)
    if instance.collection_id is None:
        raise AttributeError(
            "temporary_file_upload_to() requires a TemporaryFile with a collection that has been saved to the database."
        )
    return "{directory}/{collectionid}/{uuid}_{timestamp}{extension}".format(
        directory=getattr(
            settings, "CRADMIN_TEMPORARYFILEUPLOADSTORE_UPLOAD_DIRECTORY", "cradmin_temporaryfileuploadstore"
        ),
        collectionid=instance.collection_id,
        uuid=uuid.uuid4(),
        timestamp=time.time(),
        extension=extension,
    )


def validate_max_file_size(max_filesize_bytes, fieldfile):
    if fieldfile.size > max_filesize_bytes:
        raise ValidationError(
            gettext_lazy("Can not upload files larger than %(max_filesize)s.")
            % {
                "max_filesize": crhumanize.human_readable_filesize(max_filesize_bytes),
            },
            code="max_filesize_bytes_exceeded",
        )


def get_temporary_file_storage() -> Storage:
    storage_name = getattr(settings, "CRADMIN_LEGACY_TEMPORARY_FILE_STORAGE_BACKEND", "default")
    return storages[storage_name]


class TemporaryFile(models.Model):
    """
    A temporary file uploaded by a user.
    """

    collection = models.ForeignKey(TemporaryFileCollection, on_delete=models.CASCADE, related_name="files")
    filename = models.TextField(db_index=True)
    file = models.FileField(upload_to=temporary_file_upload_to, storage=get_temporary_file_storage)
    mimetype = models.TextField(null=False, blank=True, default="")

    def delete_object_and_file(self):
        self.file.delete()
        self.delete()

    def set_mimetype_from_filename(self):
        self.mimetype = mimetypes.guess_type(self.filename)[0] or ""

    def clean(self):
        if not self.mimetype and self.filename:
            self.set_mimetype_from_filename()
        if self.collection:
            if self.filename and self.collection.max_filename_length:
                self.filename = truncate_filename(filename=self.filename, maxlength=self.collection.max_filename_length)
            if not self.collection.is_supported_filetype(self.mimetype, self.filename):
                raise ValidationError(gettext_lazy("Unsupported filetype."), code="unsupported_mimetype")
            if self.collection.singlemode:
                other_temporaryfiles_queryset = self.collection.files.all()
                if self.id is not None:
                    other_temporaryfiles_queryset = other_temporaryfiles_queryset.exclude(id=self.id)
                for temporaryfile in other_temporaryfiles_queryset:
                    temporaryfile.file.delete()
                    temporaryfile.delete()
            if self.collection.max_filesize_bytes and self.file:
                validate_max_file_size(max_filesize_bytes=self.collection.max_filesize_bytes, fieldfile=self.file)
