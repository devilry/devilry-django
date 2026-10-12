from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=False, blank=True, default="")

    def __str__(self):
        return self.name
