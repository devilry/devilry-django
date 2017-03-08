from django.db import models


class DevelopEmail(models.Model):
    raw_content = models.TextField()
    created_datetime = models.DateTimeField(auto_now_add=True)
