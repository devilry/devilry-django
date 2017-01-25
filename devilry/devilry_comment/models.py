# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core import files
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone


class Comment(models.Model):
    """Main class for a comment.

    A comment will be made by a user, then published a few seconds later by a celery-task to make
    it possible for users to cancel publishing a comment.
    """
    #: the text of the comment
    text = models.TextField(null=False, blank=True, default='')

    #: This is used for autosave. We do not change :obj:`~.Comment.text` on autosave,
    #: instead we store the changes here, and restore them when the user returns
    #: We may then ask them if they want to restore the draft or the old text.
    draft_text = models.TextField(null=False, blank=True, default='')

    #: the user who posted the comment
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    #: if this comment is a reply to another comment, that comment will be parent
    parent = models.ForeignKey('self', null=True, blank=True)

    #: when was the comment created
    created_datetime = models.DateTimeField(auto_now_add=True)

    #: when was the comment published by celery
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
        (USER_ROLE_STUDENT, 'Student'),
        (USER_ROLE_EXAMINER, 'Examiner'),
        (USER_ROLE_ADMIN, 'Admin'),
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

    def __unicode__(self):
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
    return 'devilry_comment/{}/{}'.format(instance.comment.id, instance.id)


class CommentFile(models.Model):
    """Main class for a file uploaded to a :class:`Comment`

    This file will be interperated by celery-tasks based on mimetype, and images
    for annotation will be created where possible.
    """
    MAX_FILENAME_LENGTH = 255

    mimetype = models.CharField(max_length=42)

    #: The file uploaded to the comment. Note that this is ``blank=True`` because the
    #: comment must first be created with this field set to ``''`` to get an ID
    #: for :meth:`.commentfile_directory_path`, then updated with
    #: a file set to something.
    file = models.FileField(upload_to=commentfile_directory_path, max_length=512,
                            null=False, blank=True, default='')

    #: The name of the file - this is the name of the file that was uploaded.
    filename = models.CharField(max_length=MAX_FILENAME_LENGTH)

    #: The size of the file in bytes
    filesize = models.PositiveIntegerField()

    #: The comment owning this CommentFile. Permissions are inherited from the comment.
    comment = models.ForeignKey(Comment)

    processing_started_datetime = models.DateTimeField(null=True, blank=True)
    processing_completed_datetime = models.DateTimeField(null=True, blank=True)
    processing_successful = models.BooleanField(default=False)

    #: The datetime when the CommentFile was created.
    created_datetime = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return u'{} - {}'.format(self.comment.user, self.filename)

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

def commentfileimage_directory_path(instance, filename):
    if instance.id is None:
        raise ValueError('Can not save a CommentCommentFileImageFile.image '
                         'on a CommentFileImage without an id.')
    return 'devilry_comment/{}/{}_{}'.format(instance.comment_file.comment.id, instance.comment_file.id, instance.id)


def commentfileimage_thumbnail_directory_path(instance, filename):
    if instance.id is None:
        raise ValueError('Can not save a CommentCommentFileImageFile.thumbnail '
                         'on a CommentFileImage without an id.')
    return 'devilry_comment/{}/{}_{}_thumbnail'.format(instance.comment_file.comment.id,
                                                       instance.comment_file.id,
                                                       instance.id)


class CommentFileImage(models.Model):
    """An image representing a single page of a :class:`CommentFile`.

    These will be generated by celery-tasks based on the uploaded file.
    """
    comment_file = models.ForeignKey(CommentFile)

    image = models.FileField(upload_to=commentfileimage_directory_path,
                             max_length=512,
                             null=False, blank=True, default='')

    image_width = models.PositiveIntegerField()
    image_height = models.PositiveIntegerField()

    thumbnail = models.FileField(upload_to=commentfileimage_thumbnail_directory_path,
                                 max_length=512,
                                 null=False, blank=True, default='')
    thumbnail_width = models.PositiveIntegerField()
    thumbnail_height = models.PositiveIntegerField()


@receiver(post_delete, sender=CommentFile)
def on_post_delete_commentfile(sender, instance, **kwargs):
    commentfile = instance
    if commentfile.file:
        commentfile.file.delete()


@receiver(post_delete, sender=CommentFileImage)
def on_post_delete_commentfileimage(sender, instance, **kwargs):
    commentfileimage = instance
    if commentfileimage.image:
        commentfileimage.image.delete()
    if commentfileimage.thumbnail:
        commentfileimage.thumbnail.delete()
