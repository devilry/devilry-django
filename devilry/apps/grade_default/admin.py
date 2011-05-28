from django.contrib import admin

from ..core.models import Feedback
from models import CharFieldGrade


class CharFieldGradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'grade', 'get_delivery']
    search_fields = ['grade']

    def get_delivery(self, cfg):
        return Feedback.objects.get(object_id=cfg.id).delivery

admin.site.register(CharFieldGrade, CharFieldGradeAdmin)
