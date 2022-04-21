# -*- coding: utf-8 -*-


from django.conf import settings
from django.core import files
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import pgettext_lazy


class Comment(models.Model):
    """Main class for a comment.

    A comment made by an user.
    """
    #: the text of the comment
    text = models.TextField(null=False, blank=True, default='')

    #: This is used for autosave. We do not change :obj:`~.Comment.text` on autosave,
    #: instead we store the changes here, and restore them when the user returns
    #: We may then ask them if they want to restore the draft or the old text.
    draft_text = models.TextField(null=False, blank=True, default='')

    #: the user who posted the comment
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True,
                             on_delete=models.SET_NULL)

    #: if this comment is a reply to another comment, that comment will be parent
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    #: when was the comment created
    created_datetime = models.DateTimeField(null=False, blank=False, default=timezone.now)

    #: when was the comment published.
    published_datetime = models.DateTimeField(null=False, blank=False, default=timezone.now)

    #: Use this as value for :obj:`~.Comment.user_role` if the user
    #: is commenting as a student.
    USER_ROLE_STUDENT = 'student'

    #: Use this as value for :obj:`~.Comment.user_role` if the user
    #: is commenting as an examiner.
    USER_ROLE_EXAMINER = 'examiner'

    #: Use this as value for :obj:`~.Comment.user_role` if the user
    #: is commenting as an admin.
    USER_ROLE_ADMIN = 'admin'

    #: Choices for the :obj:`~.Comment.user_role` field.
    USER_ROLE_CHOICES = (
        (USER_ROLE_STUDENT, pgettext_lazy('comment user_role_choices','Student')),
        (USER_ROLE_EXAMINER, pgettext_lazy('comment user_role_choices','Examiner')),
        (USER_ROLE_ADMIN, pgettext_lazy('comment user_role_choices','Admin')),
    )

    #: What role did the user publish as? This determines the style of the comment
    user_role = models.CharField(choices=USER_ROLE_CHOICES, max_length=42)

    #: Use this as value for :obj:`~.Comment.comment_type` if the comment
    #: is an :class:`devilry.devilry_group.models.ImageAnnotationComment`.
    COMMENT_TYPE_IMAGEANNOTATION = 'imageannotationcomment'

    #: Use this as value for :obj:`~.Comment.comment_type` if the comment
    #: is a :class:`devilry.devilry_group.models.GroupComment`.
    COMMENT_TYPE_GROUPCOMMENT = 'groupcomment'

    #: Choices for the :obj:`~.Comment.comment_type` field.
    COMMENT_TYPE_CHOICES = (
        (COMMENT_TYPE_IMAGEANNOTATION, 'ImageAnnotationComment'),
        (COMMENT_TYPE_GROUPCOMMENT, 'GroupComment'),
    )

    #: What type of comment is this. Used for reverse mapping to subclasses.
    comment_type = models.CharField(choices=COMMENT_TYPE_CHOICES, max_length=42)

    def __str__(self):
        return '{}'.format(self.user)

    def add_commentfile_from_temporary_file(self, tempfile):
        """
        Converts a temporary file to a :class:`~.CommentFile` and saves it.

        Args:
            tempfile (TemporaryFile): Temporary file to convert.
        """
        commentfile = CommentFile.objects.create(filename=tempfile.filename,
                                                 mimetype=tempfile.mimetype,
                                                 filesize=tempfile.file.size,
                                                 comment=self)

        commentfile.file = files.File(tempfile.file, tempfile.filename)
        commentfile.clean()
        commentfile.save()

    def user_can_edit_comment(self, user):
        """
        Check if a user can edit the comment.

        Args:
            user: A user instance, (usually a request user).

        Returns:
            bool: ``True`` if user can edit, else ``False``
        """
        if user != self.user:
            return False
        if self.user_role == self.USER_ROLE_STUDENT and settings.DEVILRY_COMMENT_STUDENTS_CAN_EDIT:
            return True
        if self.user_role == self.USER_ROLE_ADMIN:
            return True
        if self.user_role == self.USER_ROLE_EXAMINER:
            return True
        return False

    def delete_comment(self):
        """
        Delete this comment. Will delete all :class:`.CommentFile`s referencing it, and all
        class :class:`.CommentFileImage`s referencing the `CommentFile`s.

        See :meth:`.CommentFile.delete_comment_file`.
        """
        comment_files = CommentFile.objects.filter(comment_id=self.id)
        for comment_file in comment_files:
            comment_file.delete_comment_file()
        self.delete()


class CommentEditHistory(models.Model):
    """
    Model for logging changes in a :class:`.Comment`.
    """

    #: The comment this history entry is for.
    comment = models.ForeignKey(
        to=Comment,
        on_delete=models.CASCADE
    )

    #: Who edited the comment.
    #: Currently, this will always be the user that created the comment.
    edited_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    #: When the comment was edited.
    edited_datetime = models.DateTimeField(
        default=timezone.now,
        null=False, blank=False
    )

    #: The result of the edited comment text.
    post_edit_text = models.TextField(
        null=False, blank=True, default=''
    )

    #: The comment text before it was edited.
    pre_edit_text = models.TextField(
        null=False, blank=True, default=''
    )

    def __str__(self):
        return 'Comment: {} - {}'.format(self.comment.user_role, self.comment.user)


def get_comment_directory_path_unlimited_files_per_directory(comment_id):
    return 'devilry_comment/{}'.format(comment_id)


def get_comment_directory_path_restrict_files_per_directory(comment_id):
    interval = 1000
    toplevel = comment_id / (interval * interval)
    sublevel = (comment_id - (toplevel * interval * interval)) / interval
    return 'devilry_comment/{toplevel}/{sublevel}/{comment_id}'.format(
        toplevel=toplevel,
        sublevel=sublevel,
        comment_id=comment_id)


def get_comment_directory_path(comment_id):
    if getattr(settings, 'DEVILRY_RESTRICT_NUMBER_OF_FILES_PER_DIRECTORY', False):
        return get_comment_directory_path_restrict_files_per_directory(comment_id=comment_id)
    else:
        return get_comment_directory_path_unlimited_files_per_directory(comment_id=comment_id)


def commentfile_directory_path(instance, filename):
    """The ``upload_to`` function for :obj:`.CommentFile.file`.

    Args:
        instance: The :class:`.CommentFile` instance.
        filename: Not used to generate the ``upload_to`` path.

    Raises:
        ValidationError: If ``instance.id`` is ``None``.
    """
    if instance.id is None:
        raise ValueError('Can not save a CommentFile.file on a CommentFile without an id.')
    comment_directory = get_comment_directory_path(comment_id=instance.comment_id)
    return '{}/file/{}'.format(comment_directory, instance.id)


class CommentFileQuerySet(models.QuerySet):
    def delete(self):
        raise NotImplementedError(
            'Bulk deletion not supported. Delete each CommentFile instead. This is because '
            'multiple CommentFiles can point to the same FileField.path, and this check is '
            'handled in a pre_delete signal.'
        )


class CommentFile(models.Model):
    """
    Main class for a file uploaded to a :class:`Comment`
    """
    objects = CommentFileQuerySet.as_manager()

    MAX_FILENAME_LENGTH = 255

    mimetype = models.CharField(max_length=255)

    #: The file uploaded to the comment. Note that this is ``blank=True`` because the
    #: comment must first be created with this field set to ``''`` to get an ID
    #: for :meth:`.commentfile_directory_path`, then updated with
    #: a file set to something.
    file = models.FileField(upload_to=commentfile_directory_path, max_length=512,
                            null=False, blank=True, default='', db_index=True)

    #: The name of the file - this is the name of the file that was uploaded.
    filename = models.CharField(max_length=MAX_FILENAME_LENGTH)

    #: The size of the file in bytes
    filesize = models.PositiveIntegerField()

    #: The comment owning this CommentFile. Permissions are inherited from the comment.
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    processing_started_datetime = models.DateTimeField(null=True, blank=True)
    processing_completed_datetime = models.DateTimeField(null=True, blank=True)
    processing_successful = models.BooleanField(default=False)

    #: The datetime when the CommentFile was created.
    created_datetime = models.DateTimeField(default=timezone.now)

    #: This is only here to make it possible to debug and fix
    #: v2 migrations if anything goes wrong.
    #:
    #: For CommentFiles imported from StaticFeedbackFileAttachment,
    #: the format of the string is
    #: ``staticfeedbackfileattachment__<StaticFeedback.id>__<StaticFeedbackFileAttachment.id>``
    #:
    #: For CommentFiles imported from FileMeta, the format of the string
    #: is ``filemeta__<FileMeta.id>``.
    v2_id = models.CharField(
        max_length=255,
        null=False, blank=True, default="")

    def __str__(self):
        return '{} - {}'.format(self.comment.user, self.filename)

    def copy_into_comment(self, target):
        """
        Copy CommentFile to ``target`` comment

        Args:
            target: :class:`~devilry_comment.Comment`

        """
        commentfilecopy = CommentFile(
            comment=target,
            filename=self.filename,
            filesize=self.filesize,
            mimetype=self.mimetype,
            file=self.file,
            processing_started_datetime=self.processing_started_datetime,
            processing_completed_datetime=self.processing_completed_datetime,
            processing_successful=self.processing_successful,
            created_datetime=self.created_datetime
        )
        commentfilecopy.save()

    def delete_comment_file(self):
        """
        Deletes the comment file and all :class:`.CommentFileImage`s that references it.
        """
        comment_file_images = CommentFileImage.objects.filter(comment_file_id=self.id)
        for comment_file_image in comment_file_images:
            comment_file_image.delete()
        self.delete()

    def get_filename_as_unique_string(self):
        """
        Get a unique filename from the file. Returns the a string with
        the format <id>-<created_datetime><filename>. The <created_datetime>-part is
        formatted with ``'%b.%m.%Y-%X.%f``.

        Notes:
            This does not change the actual filename, only builds a unique one.

        Returns:
            str: Unique version of the filename.
        """
        return '{}-{}-{}'.format(
            self.id,
            self.created_datetime.strftime('%b.%m.%Y-%X.%f'),
            self.filename
        )


def commentfileimage_directory_path(instance, filename):
    """The ``upload_to`` function for :obj:`.CommentFileImage.file`.

    Args:
        instance: The :class:`.CommentFileImage` instance.
        filename: Not used to generate the ``upload_to`` path.

    Raises:
        ValidationError: If ``instance.id`` is ``None``.
    """
    if instance.id is None:
        raise ValueError('Can not save a CommentFileImage.image on a CommentFileImage without an id.')
    comment_directory = get_comment_directory_path(comment_id=instance.comment_file.comment_id)
    return '{}/image/{}_{}'.format(comment_directory, instance.comment_file.id, instance.id)


def commentfileimage_thumbnail_directory_path(instance, filename):
    """The ``upload_to`` function for :obj:`.CommentFileImage.file`.

    Args:
        instance: The :class:`.CommentFileImage` instance.
        filename: Not used to generate the ``upload_to`` path.

    Raises:
        ValidationError: If ``instance.id`` is ``None``.
    """
    if instance.id is None:
        raise ValueError('Can not save a CommentFileImage.thumbnail on a CommentFile without an id.')
    comment_directory = get_comment_directory_path(comment_id=instance.comment_file.comment_id)
    return '{}/thumbnail/{}_{}'.format(comment_directory, instance.comment_file.id, instance.id)


class CommentFileImageQuerySet(models.QuerySet):
    def delete(self):
        raise NotImplementedError(
            'Bulk deletion not supported. Delete each CommentFileImage instead. This is because '
            'multiple CommentFileImages can point to the same FileField.path, and this check is '
            'handled in a pre_delete signal.'
        )


class CommentFileImage(models.Model):
    """
    An image representing a single page of a :class:`CommentFile`.
    """
    objects = CommentFileImageQuerySet.as_manager()

    comment_file = models.ForeignKey(CommentFile, on_delete=models.CASCADE)

    image = models.FileField(upload_to=commentfileimage_directory_path,
                             max_length=512,
                             null=False, blank=True, default='', db_index=True)

    image_width = models.PositiveIntegerField()
    image_height = models.PositiveIntegerField()

    thumbnail = models.FileField(upload_to=commentfileimage_thumbnail_directory_path,
                                 max_length=512,
                                 null=False, blank=True, default='', db_index=True)
    thumbnail_width = models.PositiveIntegerField()
    thumbnail_height = models.PositiveIntegerField()


@receiver(pre_delete, sender=CommentFile)
def on_post_delete_commentfile(sender, instance, **kwargs):
    commentfile = instance
    if commentfile.file:
        if not CommentFile.objects.exclude(id=commentfile.id).filter(file=commentfile.file).exists():
            commentfile.file.delete()


@receiver(pre_delete, sender=CommentFileImage)
def on_post_delete_commentfileimage(sender, instance, **kwargs):
    commentfileimage = instance
    queryset = CommentFileImage.objects.exclude(id=commentfileimage.id)
    if commentfileimage.image:
        if not queryset.filter(image=commentfileimage.image).exists():
            commentfileimage.image.delete()
    if commentfileimage.thumbnail:
        if not queryset.filter(thumbnail=commentfileimage.thumbnail).exists():
            commentfileimage.thumbnail.delete()
