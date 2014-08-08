from django.db import models


class AbstractApplicationKeyValue(models.Model):
    """ Abstract model for application+Key/value pair. """
    application = models.CharField(max_length=300, db_index=True, help_text="Application identifier. Max 300 chars.")
    key = models.CharField(max_length=300, db_index=True, help_text="Key. Max 300 chars.")
    value = models.TextField(null=True, blank=True, db_index=True, help_text="Value.")

    class Meta:
        abstract = True # This model will then not be used to create any database table. Instead, when it is used as a base class for other models, its fields will be added to those of the child class.

    def __unicode__(self):
        return '{0}.{1}={2}'.format(self.application, self.key, self.value)
