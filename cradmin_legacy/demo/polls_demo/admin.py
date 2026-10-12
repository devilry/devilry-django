from django.contrib import admin
from cradmin_legacy.demo.polls_demo.models import Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    list_display = ("question_text", "pub_date", "was_published_recently")
    inlines = [ChoiceInline]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)
