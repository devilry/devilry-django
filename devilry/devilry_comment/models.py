from django.conf import settings
from django.db import models
from django.core import files


class Comment(models.Model):
    """
    Main class for a comment.

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
    published_datetime = models.DateTimeField(null=True, blank=True)

    USER_ROLE_CHOICES = (
        ('student', 'Student'),
        ('examiner', 'Examiner'),
        ('admin', 'Admin'),
    )

    #: What role did the user publish as? This determines the style of the comment
    user_role = models.CharField(choices=USER_ROLE_CHOICES, max_length=42)

    COMMENT_TYPE_CHOICES = (
        ('imageannotationcomment', 'ImageAnnotationComment'),
        ('groupcomment', 'GroupComment'),
    )

    #: What type of comment is this. Used for reverse mapping to subclasses
    comment_type = models.CharField(choices=COMMENT_TYPE_CHOICES, max_length=42)


    def add_commentfile_from_temporary_file(self, tempfile):
        print "running add_commentfile_from_temporary_file"
        commentfile = CommentFile.objects.create(filename=tempfile.filename,
                                                 mimetype=tempfile.mimetype,
                                                 filesize=tempfile.file.size,
                                                 comment=self)

        commentfile.file = files.File(tempfile.file, tempfile.filename)
        commentfile.save()
        print "returning from add_commentfile_from_temporary_file"


def commentfile_directory_path(instance, filename):
    if instance.id is None:
        raise ValueError('Can not save a comment file for a comment without an id.')
    return 'devilry_comment/{}/{}'.format(instance.comment.id, instance.id)


class CommentFile(models.Model):
    """
    Main class for a file uploaded to a :class:`Comment`

    This file will be interperated by celery-tasks based on mimetype, and images
    for annotation will be created where possible.
    """
    MAX_FILENAME_LENGTH = 255

    mimetype = models.CharField(max_length=42)
    file = models.FileField(upload_to=commentfile_directory_path, max_length=512)
    filename = models.CharField(max_length=MAX_FILENAME_LENGTH)
    filesize = models.PositiveIntegerField()
    comment = models.ForeignKey(Comment)
    processing_started_datetime = models.DateTimeField(null=True, blank=True)
    processing_completed_datetime = models.DateTimeField(null=True, blank=True)
    processing_successful = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{} - {}'.format(self.comment.user, self.filename)


def commentfileimage_directory_path(instance, filename):
    return 'devilry_comment/{}/{}_{}'.format(instance.comment_file.comment.id, instance.comment_file.id, instance.id)


def commentfileimage_thumbnail_directory_path(instance, filename):
    return 'devilry_comment/{}/{}_{}_thumbnail'.format(instance.comment_file.comment.id,
                                                       instance.comment_file.id,
                                                       instance.id)


class CommentFileImage(models.Model):
    """
    An image representing a single page of a :class:`CommentFile`. These will be generated
    by celery-tasks based on the uploaded file.
    """
    comment_file = models.ForeignKey(CommentFile)

    image = models.FileField(upload_to=commentfileimage_directory_path, max_length=512)
    image_width = models.PositiveIntegerField()
    image_height = models.PositiveIntegerField()

    thumbnail = models.FileField(upload_to=commentfileimage_thumbnail_directory_path, max_length=512)
    thumbnail_width = models.PositiveIntegerField()
    thumbnail_height = models.PositiveIntegerField()
