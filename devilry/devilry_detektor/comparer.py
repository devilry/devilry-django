from collections import OrderedDict
import detektor
import itertools

from devilry.devilry_detektor.models import CompareTwoCacheItem
from devilry.devilry_detektor.models import DetektorAssignmentCacheLanguage


class DevilryDetektorCompareMany(detektor.comparer.CompareMany):
    def compare(self, parseresult1, parseresult2):
        if parseresult1.delivery.assignment_group == parseresult2.delivery.assignment_group:
            # Do not compare two deliveries by the same user
            return
        else:
            super(DevilryDetektorCompareMany, self).compare(parseresult1, parseresult2)

    def add_to_results(self, comparetwo):
        # Only add results with any points.
        if comparetwo.get_scaled_points() > 0:
            super(DevilryDetektorCompareMany, self).add_to_results(comparetwo)


class CompareManyCollection(object):
    """
    Takes a :class:`devilry_detektor.models.DetektorAssignment` object,
    groups its :class:`devilry_detektor.models.DetektorDeliveryParseResult`
    by language and runs :class:`DevilryDetektorCompareMany` for each language
    """
    def __init__(self, detektorassignment):
        self.detektorassignment = detektorassignment
        self._bylanguage = self._group_by_language_and_compare(
            self._get_parseresults_queryset())

    def _get_parseresults_queryset(self):
        parseresults = self.detektorassignment.parseresults\
            .order_by('language')\
            .select_related(
                'delivery',
                'delivery__deadline',
                'delivery__deadline__assignment_group',
                'delivery__deadline__assignment_group__parentnode',  # Assignment
                'delivery__deadline__assignment_group__parentnode__parentnode',  # Period
                'delivery__deadline__assignment_group__parentnode__parentnode__parentnode'  # Subject
            )\
            .prefetch_related(
                'delivery__deadline__assignment_group__candidates',
                'delivery__deadline__assignment_group__candidates__student',
                'delivery__deadline__assignment_group__candidates__student__devilryuserprofile')
        return parseresults

    def _group_by_language_and_compare(self, parseresults):
        bylanguage = OrderedDict()
        for language, parseresults in itertools.groupby(parseresults, lambda p: p.language):
            comparemany = DevilryDetektorCompareMany(list(parseresults))
            comparemany.sort_by_points_descending()
            bylanguage[language] = comparemany
        return bylanguage

    # def iteritems(self):
    #     """
    #     Iterate yielding ``(language, DevilryDetektorCompareMany)``.
    #     """
    #     return self._bylanguage.iteritems()

    def save(self):
        self.detektorassignment.cachelanguages.all().delete()
        cacheitems = []
        for language, comparemany in self._bylanguage.iteritems():
            languageobject = DetektorAssignmentCacheLanguage.objects.create(
                detektorassignment=self.detektorassignment,
                language=language)
            for comparetwo in comparemany:
                cacheitems.append(CompareTwoCacheItem.from_comparetwo(
                    comparetwo=comparetwo, language=languageobject))
        CompareTwoCacheItem.objects.bulk_create(cacheitems)
