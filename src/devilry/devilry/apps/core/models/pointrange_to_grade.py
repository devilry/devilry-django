from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

from .assignment import Assignment


class PointRangeToGradeMapQueryset(models.query.QuerySet):
    def filter_overlapping_ranges(self, start, end):
        return self.filter(
            Q(minimum_points__lte=start, maximum_points__gte=start) |
            Q(minimum_points__lte=end, maximum_points__gte=end) |
            Q(minimum_points__gte=start, maximum_points__lte=end))


class PointRangeToGradeMapManager(models.Manager):
    """
    Reflect custom QuerySet methods for custom QuerySet
    more info: https://github.com/devilry/devilry-django/issues/491
    """

    def get_queryset(self):
        return PointRangeToGradeMapQueryset(self.model, using=self._db)

    def filter_overlapping_ranges(self, start, end):
        """
        Matches all PointRangeToGrade objects where start or end is
        between the start and the end.

        This is perfect for checking if a range can be added to an assignment
        (needs ``.filter(assignment=assignment)`` in addition to this filter).
        """
        return self.get_queryset().filter_overlapping_ranges(start, end)



class PointRangeToGrade(models.Model):
    """
    Data structure to store the mapping from point to grade when using custom-table.

    First described in https://github.com/devilry/devilry-django/issues/511.

    .. attribute:: assignment

        Foreign Key to the assignment.

    .. attribute:: minimum_points

        Minimum value for points that matches this table entry.

    .. attribute:: maximum_points
        Minimum value for points that matches this table entry.

    .. attribute:: grade

        The grade that this entry represents a match for.
    """
    objects = PointRangeToGradeMapManager()
    assignment = models.ForeignKey(Assignment)
    minimum_points = models.IntegerField()
    maximum_points = models.IntegerField()
    grade = models.CharField(max_length=12)
    
    class Meta:
        unique_together = ('assignment', 'grade')
        app_label = 'core'
        ordering = ['minimum_points']

    def clean(self):
        if self.minimum_points >= self.maximum_points:
            raise ValidationError('Minimum points can not be equal to or greater than maximum points.')
        overlapping_ranges = self.__class__.objects\
            .filter_overlapping_ranges(self.minimum_points, self.maximum_points) \
            .filter(assignment=self.assignment)
        if self.id != None:
            overlapping_ranges = overlapping_ranges.exclude(id=self.id)
        if overlapping_ranges.exists():
            raise ValidationError('One or more PointRangeToGrade overlaps with this range.')

    def __unicode__(self):
        return u'{0}: {1}-{2}={3}'.format(self.assignment.get_path(),
            self.minimum_points, self.maximum_points, self.grade)
