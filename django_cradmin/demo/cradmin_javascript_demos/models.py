from django.db import models


class FictionalFigure(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField(null=False, blank=True, default="")
    is_godlike = models.BooleanField(default=False)
    rating = models.PositiveIntegerField(default=0)
    sort_index = models.PositiveIntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sort_index", "name"]


class FictionalFigureCollection(models.Model):
    name = models.CharField(max_length=255)
    primary_fictional_figure = models.ForeignKey(FictionalFigure, related_name="+", on_delete=models.CASCADE)
    secondary_fictional_figure = models.ForeignKey(
        FictionalFigure, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    promoted_fictional_figures = models.ManyToManyField(FictionalFigure, blank=True)
