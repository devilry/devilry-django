from django.contrib import admin

from django_cradmin.demo.cradmin_javascript_demos.models import FictionalFigure, FictionalFigureCollection


@admin.register(FictionalFigure)
class FictionalFigureAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "about",
        "is_godlike",
        "rating",
        "sort_index",
    ]
    search_fields = ["name", "about"]
    list_filter = [
        "is_godlike",
    ]


@admin.register(FictionalFigureCollection)
class FictionalFigureCollectionAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
