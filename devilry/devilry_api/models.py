from django.db import models
from django.utils import timezone
from devilry.devilry_account.models import User


class ApiKey(models.Model):
    """
    A class representing a given api key for a `user`.


    .. attribute:: user
    A devilry.devilry_account.models.User that is the owner of the key.

    .. attribute:: key
    A django.db.models.CharField that holds the key.

    .. attribute:: created_datetime
    A django.db.models.DateTimeField that holds the date and time
    the key was created on.

    .. attribute:: expiration_date
    A django.db.models.DateTimeField that holds the date and time
    the key expires on.


    Extra stuff: when, where, who the key was last used.

    """
    class Meta:
        app_label = 'api key'
        db_table = 'api-key'

    #: The owner of the key
    user = models.ForeignKey(User, null=False)

    #: api key
    key = models.CharField(max_length=64, unique=True, blank=False)

    #: created timestamp
    created_datetime = models.DateTimeField(default=timezone.now)

    #: the key expire this date
    expiration_date = models.DateTimeField(blank=False)

    def has_expired(self):
        """
        Returns true if the key has expired, false if not.

        """
        return self.expiration_date <= timezone.now()

    @property
    def user(self):
        return self.user

    @property
    def key(self):
        return self.key

    @property
    def created(self):
        return self.created

    @property
    def expiration_date(self):
        return self.expiration_date
