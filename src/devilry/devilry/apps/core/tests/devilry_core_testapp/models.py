from django.db import models

from devilry.apps.core.models import BulkCreateIdentifier
from devilry.apps.core.models.bulkcreateidentifier import BulkCreateIdentifierField
from devilry.apps.core.models.bulkcreateidentifier import BulkCreateManagerMixin



class BulkCreateIdentifierDemoQuerySet(models.query.QuerySet):
    pass

class BulkCreateIdentifierDemoManager(models.Manager, BulkCreateManagerMixin):
    def get_queryset(self):
        return BulkCreateIdentifierDemoQuerySet(self.model, using=self._db)

    def create_many(self, *names):
        bulkcreate_identifier = BulkCreateIdentifier.objects.create()
        def makemodel(name):
            return BulkCreateIdentifierDemoModel(name=name,
                bulkcreate_identifier=bulkcreate_identifier)
        mymodels = map(makemodel, names)
        self.bulk_create(mymodels)
        return self.filter_by_bulkcreateidentifier(bulkcreate_identifier)


class BulkCreateIdentifierDemoModel(models.Model):
    name = models.CharField(max_length=100)
    bulkcreate_identifier = BulkCreateIdentifierField()
    objects = BulkCreateIdentifierDemoManager()
