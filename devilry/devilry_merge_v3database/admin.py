from django.contrib import admin

from devilry.devilry_merge_v3database.models import TempMergeId


class TempMergeIdAdmin(admin.ModelAdmin):
    list_display = [
        'model_name'
    ]


admin.site.register(TempMergeId, TempMergeIdAdmin)
