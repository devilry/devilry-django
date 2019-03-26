from os.path import splitext
from os.path import basename
from django.conf import settings
from django.db import models

from devilry.apps.core.models import Deadline
from devilry.apps.core.models import Delivery
from devilry.devilry_account.models import User


def uploaded_deliveryfile_path(uploaded_deliveryfile, filename):
    if uploaded_deliveryfile.id is None:
        raise ValueError('Can not add the file to UploadedDeliveryFile before it has an ID.')
    return 'devilry_student/incomplete_deliveries/{id}'.format(id=uploaded_deliveryfile.id)


class UploadedDeliveryFileQuerySet(models.QuerySet):
    """
    QuerySet for :class:`.UploadedDeliveryFileManager`.
    """

    def delete_objects_and_files(self):
        """
        Delete all UploadedDeliveryFile objects in the queryset along
        with their physical files.
        """
        for uploaded_deliveryfile in self:
            uploaded_deliveryfile.uploaded_file.delete()
        self.delete()


class UploadedDeliveryFileManager(models.Manager):
    """
    Manager for :class:`.UploadedDeliveryFile`.
    """

    def get_queryset(self):
        return UploadedDeliveryFileQuerySet(self.model, using=self._db)

    def filter_for_deadline(self, deadline, user):
        """
        Filter all uploaded files for the given user on the given deadline.
        """
        return self.get_queryset().filter(deadline=deadline, user=user)

    def convert_to_delivery(self, deadline, user):
        """
        Convert all the UploadedDeliveryFile objects mathing the given deadline and user to a Delivery.

        Typical usage::

            from django.db import transaction
            with transaction.commit_on_success():
                delivery, files = UploadedDeliveryFile.objects.convert_to_delivery(mydeadline, myuser)
            with transaction.commit_on_success():
                files.delete_objects_and_files()


        :return:
            A (delivery, queryset) tuple where the ``delivery`` is the created Delivery,    
            the ``queryset` is a :class:`.UploadedDeliveryFileQuerySet` with the
            files that was made into a delivery.
        """
        queryset = self.filter_for_deadline(deadline, user)
        if not queryset.exists():
            raise UploadedDeliveryFile.DoesNotExist('No UploadedDeliveryFile with the given deadline and user exists.')

        candidate = deadline.assignment_group.candidates.filter(relatedstudent__user=user).get()
        delivery = Delivery(
            deadline=deadline,
            delivered_by=candidate,
            successful=False
        )
        delivery.set_number()
        delivery.save()

        for uploaded_deliveryfile in queryset:
            delivery.add_file(uploaded_deliveryfile.filename,
                              uploaded_deliveryfile.uploaded_file)

        delivery.successful = True
        delivery.save()

        return delivery, queryset

    def create_with_file(self, deadline, user, filename, filecontent):
        """
        Use this to create a UploadedDeliveryFile. It handles creating a new
        UploadedDeliveryFile without any content to get an ID that can be used
        to save the actual file content.

        Example::

            from django.core.files.base import ContentFile
            UploadedDeliveryFile.objects.create_with_file(
                deadline=mydeadline,
                user=myuser,
                filename='test.txt',
                filecontent=ContentFile('Hello world')
            )

        .. note::

            Do not use ContentFile in production code, use ``django.core.files.File``.
        """
        uploaded_deliveryfile = UploadedDeliveryFile.objects.create(
            deadline=deadline,
            user=user,
            filename=filename
        )
        uploaded_deliveryfile.uploaded_file.save(filename, filecontent)
        return uploaded_deliveryfile


class UploadedDeliveryFile(models.Model):
    """
    A temporary file uploaded by a user on a deadline.

    Can be turned into a Delivery using
    :meth:`.UploadedDeliveryFileManager.convert_to_delivery`.
    """
    objects = UploadedDeliveryFileManager()

    #: The :class:`devilry.apps.core.models.Deadline` that the file was uploaded to.
    deadline = models.ForeignKey(Deadline, on_delete=models.CASCADE)

    #: The User that uploaded the file. Only this user has access to the file.
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    #: The datetime when this UploadedDeliveryFile was created.
    uploaded_datetime = models.DateTimeField(auto_now_add=True)

    #: The uploaded file
    uploaded_file = models.FileField(upload_to=uploaded_deliveryfile_path)

    #: Filename. Max 255 chars (just like FileMeta).
    filename = models.CharField(max_length=255)

    class Meta:
        unique_together = ('deadline', 'user', 'filename')

    @staticmethod
    def prepare_filename(filename):
        filename = basename(filename)
        if len(filename) > 255:
            name, ext = splitext(filename)
            return '{}{}'.format(name[:255 - len(ext)], ext)
        else:
            return filename
