from django.contrib import admin
from devilry.devilry_comment import models


class CommentAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Comment, CommentAdmin)

class CommentFileadmin(admin.ModelAdmin):
    pass

admin.site.register(models.CommentFile, CommentFileadmin)
