import pprint
from django.contrib.auth import get_user_model

from devilry.apps.core.models import RelatedExaminer, RelatedStudent, Period, PeriodTag
from devilry.devilry_import_v2database import modelimporter


class ImporterMixin(object):
    def get_model_class(self):
        return None

    def _get_period_from_id(self, period_id):
        try:
            period = Period.objects.get(id=period_id)
        except Period.DoesNotExist:
            raise modelimporter.ModelImporterException(
                'Period with id {} does not exist'.format(period_id))
        return period

    def _get_user_from_id(self, user_id):
        try:
            user = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            raise modelimporter.ModelImporterException(
                'User with id {} does not exist'.format(user_id))
        return user

    def _get_period_tag_queryset(self, period, v2_tags_list):
        return PeriodTag.objects\
            .filter(period=period, tag__in=v2_tags_list)

    def _bulk_create_period_tags(self, period, v2_tags_list, tags_to_exclude):
        """
        Bulk create tags ``PeriodTag``s.

        Args:
            period: The Period the tags are for.
            v2_tags_list: List of strings (Devilry 2.0 tags).
            tags_to_exclude: List of strings of tags that already exists for this period.
        """
        period_tag_list = []
        for tag in v2_tags_list:
            if tag not in tags_to_exclude:
                period_tag_list.append(
                    PeriodTag(period=period, tag=tag)
                )
        PeriodTag.objects.bulk_create(period_tag_list)

    def _get_tags_and_tags_to_exclude(self, period, tags_string):
        """
        Get the tags from v2 separated in a list and a list of tags that should
        be excluded(``PeriodTag``s already exists)

        Note:
            Performs query to fetch the existing ``PeriodTag``s for this ``Period`` passed
            as parameter.

        Args:
            period: The ``Period`` for the ``PeriodTag``s.
            tags: a string of tags separated by a comma, no whitespace(according to v2 RelatedUser.tags).

        Returns:
            tuple (list, list): A list of tags, and a list of tags that should be excluded.
        """
        tags_list = [tag for tag in tags_string.split(',')]
        period_tag_queryset = self._get_period_tag_queryset(period=period, v2_tags_list=tags_list)
        tags_to_exclude = [period_tag.tag for period_tag in period_tag_queryset]
        return tags_list, tags_to_exclude

    def _create_or_update_period_tag_for_related_user_type(self, related_user, period, tags):
        """
        Adds the relatedexaminer to each period tag or creates tags that does not exist.
        """
        tags_list, tags_to_exclude_list = self._get_tags_and_tags_to_exclude(period, tags)
        self._bulk_create_period_tags(
            period=period,
            v2_tags_list=tags_list,
            tags_to_exclude=tags_to_exclude_list
        )
        period_tag_queryset = self._get_period_tag_queryset(period=period, v2_tags_list=tags_list)
        for period_tag in period_tag_queryset:
            if self.get_model_class() == RelatedExaminer:
                period_tag.relatedexaminers.add(related_user)
            else:
                period_tag.relatedstudents.add(related_user)


class RelatedExaminerImporter(ImporterMixin, modelimporter.ModelImporter):
    def get_model_class(self):
        return RelatedExaminer

    def _create_related_examiner_from_object_dict(self, object_dict):
        related_examiner = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=related_examiner,
            object_dict=object_dict,
            attributes=[
                'pk',
            ]
        )
        period = self._get_period_from_id(period_id=object_dict['fields']['period'])
        user = self._get_user_from_id(user_id=object_dict['fields']['user'])
        related_examiner.period = period
        related_examiner.user = user
        related_examiner.full_clean()
        related_examiner.save()
        self._create_or_update_period_tag_for_related_user_type(
            related_user=related_examiner,
            period=period,
            tags=object_dict['fields']['tags']
        )
        self.log_create(model_object=related_examiner, data=object_dict)

    def import_models(self, fake=False):
        directory_parser = self.v2relatedexaminer_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(self.get_model_class())
        for object_dict in directory_parser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_related_examiner_from_object_dict(object_dict=object_dict)


class RelatedStudentImporter(ImporterMixin, modelimporter.ModelImporter):
    def get_model_class(self):
        return RelatedStudent

    def _create_related_student_from_object_dict(self, object_dict):
        related_student = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=related_student,
            object_dict=object_dict,
            attributes=[
                'pk',
                'candidate_id'
            ]
        )
        period = self._get_period_from_id(period_id=object_dict['fields']['period'])
        user = self._get_user_from_id(user_id=object_dict['fields']['user'])
        related_student.period = period
        related_student.user = user
        related_student.full_clean()
        related_student.save()
        self._create_or_update_period_tag_for_related_user_type(
            related_user=related_student,
            period=period,
            tags=object_dict['fields']['tags']
        )
        self.log_create(model_object=related_student, data=object_dict)

    def import_models(self, fake=False):
        directory_parser = self.v2relatedstudent_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(self.get_model_class())
        for object_dict in directory_parser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_related_student_from_object_dict(object_dict=object_dict)
