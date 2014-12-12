from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .assignment import Assignment



class NonzeroSmallesMinimalPointsValidationError(ValidationError):
    pass

class InvalidLargestMaximumPointsValidationError(ValidationError):
    pass

class GapsInMapValidationError(ValidationError):
    pass

class DuplicateGradeError(Exception):
    pass


class PointToGradeMap(models.Model):
    """
    Data structure to store the mapping from a point ranges to grades
    when using custom-table.

    The basic idea is described in https://github.com/devilry/devilry-django/issues/511,
    but we decided to add this OneToOne table to represent a mapping table
    to avoid adding complexity to Assignment that is only needed when the
    custom-table ``points_to_grade_mapper`` is used.

    .. attribute:: assignment

        Foreign Key to the assignment.

    .. attribute:: invalid

        This is set to ``True`` when the map has been invalidated because of 
        changes to :attr:`devilry.apps.core.models.Assignment.max_points`,
        or when the map has been created, but it is empty.
    """
    assignment = models.OneToOneField(Assignment)
    invalid = models.BooleanField(default=True)


    class Meta:
        app_label = 'core'

    def clean(self):
        mapentries = list(self.pointrangetograde_set.all())
        if len(mapentries) == 0:
            self.invalid = True
        else:
            first_entry = mapentries[0]
            if first_entry.minimum_points != 0:
                raise NonzeroSmallesMinimalPointsValidationError(
                    _('The smallest entry in the map must have minimum points set to 0 (current value is {minimum_points}).').format(
                        minimum_points=first_entry.minimum_points))
            last_entry = mapentries[-1]
            if last_entry.maximum_points != self.assignment.max_points:
                raise InvalidLargestMaximumPointsValidationError('The last entry in the map must have maximum_points set to the maximum points allowed on the assignment ({}).'.format(
                    self.assignment.max_points))
            expected_minimum_points = 0
            for mapentry in mapentries:
                if mapentry.minimum_points != expected_minimum_points:
                    raise GapsInMapValidationError(u'{} must have minimum_points set to {} to avoid gaps in the point to grade map.'.format(
                        mapentry, expected_minimum_points))
                expected_minimum_points = mapentry.maximum_points + 1
            self.invalid = False


    def create_map(self, *minimum_points_to_grade_list):
        gradeset = set()
        for index, entry in enumerate(minimum_points_to_grade_list):
            minimum_points, grade = entry
            if grade in gradeset:
                raise DuplicateGradeError(
                    _('{grade} occurs multiple times in the map. A grade must be unique within the map.'.format(
                        grade=grade)))
            gradeset.add(grade)
            if index == len(minimum_points_to_grade_list) - 1:
                maximum_points = self.assignment.max_points
            else:
                maximum_points = minimum_points_to_grade_list[index+1][0] - 1
            self.pointrangetograde_set.create(
                grade=grade,
                minimum_points=minimum_points,
                maximum_points=maximum_points
            )

    def clear_map(self):
        self.pointrangetograde_set.all().delete()

    def recreate_map(self, *minimum_points_to_grade_list):
        """
        """
        self.clear_map()
        self.create_map(*minimum_points_to_grade_list)

    def points_to_grade(self, points):
        """
        Convert the given ``points`` to a grade using this PointToGradeMap.

        :raises PointRangeToGrade.DoesNotExist:
            If no grade matching the given points exist.
        """
        return PointRangeToGrade.objects\
            .filter_grades_matching_points(points)\
            .filter(point_to_grade_map=self).get()


    def as_choices(self):
        """
        Get as a list of tuples compatible with the choices argument for
        django ChoiceField and TypedChoiceField with coerce set to ``int``.
        """
        return [(pointrange.minimum_points, pointrange.grade) \
            for pointrange in self.pointrangetograde_set.all()]


    def __unicode__(self):
        return u'Point to grade map for {}'.format(self.assignment.get_path())




class PointRangeToGradeMapQueryset(models.query.QuerySet):
    def filter_overlapping_ranges(self, start, end):
        return self.filter(
            Q(minimum_points__lte=start, maximum_points__gte=start) |
            Q(minimum_points__lte=end, maximum_points__gte=end) |
            Q(minimum_points__gte=start, maximum_points__lte=end))

    def filter_grades_matching_points(self, points):
        return self.filter(
            minimum_points__lte=points,
            maximum_points__gte=points
        )


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
        (needs ``.filter(point_to_grade_map=assignment.pointtogrademap)`` in addition to this filter).
        """
        return self.get_queryset().filter_overlapping_ranges(start, end)

    def filter_grades_matching_points(self, points):
        """
        Filter all PointRangeToGrade objects where ``points`` is between
        ``minimum_points`` and ``maximum_points`` including both ends.
        """
        return self.get_queryset().filter_grades_matching_points(points)



class PointRangeToGrade(models.Model):
    """
    Data structure to store the mapping from a single point-range to grade
    when using custom-table.

    First described in https://github.com/devilry/devilry-django/issues/511.

    .. attribute:: point_to_grade_map

        Foreign Key to the PointToGradeMap.

    .. attribute:: minimum_points

        Minimum value for points that matches this table entry.

    .. attribute:: maximum_points
        Minimum value for points that matches this table entry.

    .. attribute:: grade

        The grade that this entry represents a match for.
    """
    objects = PointRangeToGradeMapManager()
    point_to_grade_map = models.ForeignKey(PointToGradeMap)
    minimum_points = models.PositiveIntegerField()
    maximum_points = models.PositiveIntegerField()
    grade = models.CharField(max_length=12)
    
    class Meta:
        unique_together = ('point_to_grade_map', 'grade')
        app_label = 'core'
        ordering = ['minimum_points']

    def clean(self):
        if self.minimum_points >= self.maximum_points:
            raise ValidationError('Minimum points can not be equal to or greater than maximum points.')
        overlapping_ranges = self.__class__.objects\
            .filter_overlapping_ranges(self.minimum_points, self.maximum_points) \
            .filter(point_to_grade_map=self.point_to_grade_map)
        if self.id != None:
            overlapping_ranges = overlapping_ranges.exclude(id=self.id)
        if overlapping_ranges.exists():
            raise ValidationError('One or more PointRangeToGrade overlaps with this range.')

    def __unicode__(self):
        return u'{}-{}={}'.format(self.minimum_points, self.maximum_points, self.grade)
