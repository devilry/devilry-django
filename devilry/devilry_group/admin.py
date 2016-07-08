from django.contrib import admin
from devilry.devilry_group import models


class FeedbackSetAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.FeedbackSet, FeedbackSetAdmin)


class GroupCommentAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.GroupComment, GroupCommentAdmin)
