from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy, pgettext_lazy, pgettext
from django_cradmin.viewhelpers import listfilter
from django_cradmin.viewhelpers.listfilter.basefilters.single import abstractradio
from django_cradmin.viewhelpers.listfilter.basefilters.single import abstractselect


class AbstractSearch(listfilter.django.single.textinput.Search):
    def __init__(self, label_is_screenreader_only=True):
        super(AbstractSearch, self).__init__(
            slug='search',
            label=ugettext_lazy('Search'),
            label_is_screenreader_only=label_is_screenreader_only
        )

    def filter(self, queryobject):
        return super(AbstractSearch, self).filter(queryobject=queryobject)


class SearchNotAnonymous(AbstractSearch):
    def get_modelfields(self):
        return [
            'candidates__relatedstudent__user__fullname',
            'candidates__relatedstudent__user__shortname',
        ]


class SearchAnonymous(AbstractSearch):
    def get_modelfields(self):
        return [
            'candidates__relatedstudent__candidate_id',
            'candidates__relatedstudent__automatic_anonymous_id',
        ]


class SearchAnonymousUsesCustomCandidateIds(AbstractSearch):
    def get_modelfields(self):
        return [
            'candidates__candidate_id',
        ]


class AbstractOrderBy(listfilter.django.single.select.AbstractOrderBy):
    def __init__(self, include_points=True, label_is_screenreader_only=False):
        self.include_points = include_points
        super(AbstractOrderBy, self).__init__(
            slug='orderby',
            label=pgettext_lazy('orderby', 'Sort'),
            label_is_screenreader_only=label_is_screenreader_only
        )

    def get_user_ordering_options(self):
        return []

    def get_common_ordering_options(self):
        ordering_options_list = []
        if self.include_points:
            ordering_options_list.append(
                (pgettext_lazy('orderby', 'By points'), (
                    ('points_descending', {
                        'label': pgettext_lazy('orderby', 'Points (highest first)'),
                        'order_by': ['-cached_data__last_published_feedbackset__grading_points'],
                    }),
                    ('points_ascending', {
                        'label': pgettext_lazy('orderby', 'Points (lowest first)'),
                        'order_by': ['cached_data__last_published_feedbackset__grading_points'],
                    }),
                )),
            )
        ordering_options_list.append(
            (pgettext_lazy('orderby', 'By activity'), (
                ('last_commented_by_student_descending', {
                    'label': pgettext_lazy('orderby', 'Recently commented by student'),
                    'order_by': [],  # Handled with custom query in filter()
                }),
                ('last_commented_by_student_ascending', {
                    'label': pgettext_lazy('orderby', 'Least recently commented by student'),
                    'order_by': [],  # Handled with custom query in filter()
                }),
                ('last_commented_by_examiner_descending', {
                    'label': pgettext_lazy('orderby', 'Recently commented by examiner'),
                    'order_by': [],  # Handled with custom query in filter()
                }),
                ('last_commented_by_examiner_ascending', {
                    'label': pgettext_lazy('orderby', 'Least recently commented by examiner'),
                    'order_by': [],  # Handled with custom query in filter()
                }),
            ))
        )
        return ordering_options_list

    def get_ordering_options(self):
        ordering_options = [(
            pgettext_lazy('orderby', 'By student name'),
            self.get_user_ordering_options()
        )]
        ordering_options.extend(self.get_common_ordering_options())
        return ordering_options

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == 'last_commented_by_student_ascending':
            return queryobject.order_by('cached_data__last_public_comment_by_student_datetime')
        elif cleaned_value == 'last_commented_by_student_descending':
            return queryobject.order_by('-cached_data__last_public_comment_by_student_datetime')
        elif cleaned_value == 'last_commented_by_examiner_ascending':
            return queryobject.order_by('cached_data__last_public_comment_by_examiner_datetime')
        elif cleaned_value == 'last_commented_by_examiner_descending':
            return queryobject.order_by('-cached_data__last_public_comment_by_examiner_datetime')
        return super(AbstractOrderBy, self).filter(queryobject=queryobject).distinct()


class OrderByNotAnonymous(AbstractOrderBy):
    def get_user_ordering_options(self):
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            shortname_ascending_label = pgettext_lazy('orderby', 'Email')
            shortname_descending_label = pgettext_lazy('orderby', 'Email (descending)')
        else:
            shortname_ascending_label = pgettext_lazy('orderby', 'Username')
            shortname_descending_label = pgettext_lazy('orderby', 'Username (descending)')
        return [
            ('', {
                'label': pgettext_lazy('orderby', 'Name'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('name_descending', {
                'label': pgettext_lazy('orderby', 'Name (descending)'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('shortname_ascending', {
                'label': shortname_ascending_label,
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('shortname_descending', {
                'label': shortname_descending_label,
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('lastname_ascending', {
                'label': pgettext_lazy('orderby', 'Last name'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('lastname_descending', {
                'label': pgettext_lazy('orderby', 'Last name (descending)'),
                'order_by': [],  # Handled with custom query in filter()
            }),
        ]

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == '':
            return queryobject.extra_order_by_fullname_of_first_candidate()
        elif cleaned_value == 'name_descending':
            return queryobject.extra_order_by_fullname_of_first_candidate(descending=True)
        elif cleaned_value == 'shortname_ascending':
            return queryobject.extra_order_by_shortname_of_first_candidate()
        elif cleaned_value == 'shortname_descending':
            return queryobject.extra_order_by_shortname_of_first_candidate(descending=True)
        elif cleaned_value == 'lastname_ascending':
            return queryobject.extra_order_by_lastname_of_first_candidate()
        elif cleaned_value == 'lastname_descending':
            return queryobject.extra_order_by_lastname_of_first_candidate(descending=True)
        else:
            return super(OrderByNotAnonymous, self).filter(queryobject=queryobject)


class OrderByAnonymous(AbstractOrderBy):
    def get_user_ordering_options(self):
        return [
            ('', {
                'label': pgettext_lazy('orderby', 'Anonymous ID'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('name_descending', {
                'label': pgettext_lazy('orderby', 'Anonymous ID (descending)'),
                'order_by': [],  # Handled with custom query in filter()
            }),
        ]

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == '':
            return queryobject.extra_order_by_relatedstudents_anonymous_id_of_first_candidate()
        elif cleaned_value == 'name_descending':
            return queryobject.extra_order_by_relatedstudents_anonymous_id_of_first_candidate(descending=True)
        else:
            return super(OrderByAnonymous, self).filter(queryobject=queryobject)


class OrderByAnonymousUsesCustomCandidateIds(AbstractOrderBy):
    def get_user_ordering_options(self):
        return [
            ('', {
                'label': pgettext_lazy('orderby', 'Candidate ID'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('name_descending', {
                'label': pgettext_lazy('orderby', 'Candidate ID (descending)'),
                'order_by': [],  # Handled with custom query in filter()
            }),
        ]

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == '':
            return queryobject.extra_order_by_candidates_candidate_id_of_first_candidate()
        elif cleaned_value == 'name_descending':
            return queryobject.extra_order_by_candidates_candidate_id_of_first_candidate(descending=True)
        else:
            return super(OrderByAnonymousUsesCustomCandidateIds, self).filter(queryobject=queryobject)


class StatusRadioFilter(abstractradio.AbstractRadioFilter):
    def __init__(self, **kwargs):
        self.view = kwargs.pop('view', None)
        super(StatusRadioFilter, self).__init__(**kwargs)

    def copy(self):
        copy = super(StatusRadioFilter, self).copy()
        copy.view = self.view
        return copy

    def get_slug(self):
        return 'status'

    def get_label(self):
        return pgettext_lazy('group status', 'Status')

    def __count_html(self, count, has_count_cssclass):
        cssclass = 'label-default'
        if count and has_count_cssclass:
            cssclass = has_count_cssclass
        return u'<span class="label {}">{}</span>'.format(cssclass, count)

    def __make_label(self, label, count, has_count_cssclass=None):
        return mark_safe(u'{label} {count}'.format(
            label=label,
            count=self.__count_html(count=count, has_count_cssclass=has_count_cssclass)))

    def get_choices(self):
        return [
            ('',
             self.__make_label(
                 label=pgettext('group status', 'all students'),
                 count=self.view.get_filtered_all_students_count()
             )),
            ('waiting-for-feedback',
             self.__make_label(
                 label=pgettext('group status', 'waiting for feedback'),
                 count=self.view.get_filtered_waiting_for_feedback_count(),
                 has_count_cssclass='label-warning'
             )),
            ('waiting-for-deliveries',
             self.__make_label(
                 label=pgettext('group status', 'waiting for deliveries'),
                 count=self.view.get_filtered_waiting_for_deliveries_count()
             )),
            ('corrected',
             self.__make_label(
                 label=pgettext('group status', 'corrected'),
                 count=self.view.get_filtered_corrected_count()
             )),
        ]

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == 'waiting-for-feedback':
            queryobject = queryobject.filter(annotated_is_waiting_for_feedback__gt=0)
        elif cleaned_value == 'waiting-for-deliveries':
            queryobject = queryobject.filter(annotated_is_waiting_for_deliveries__gt=0)
        elif cleaned_value == 'corrected':
            queryobject = queryobject.filter(annotated_is_corrected__gt=0)
        return queryobject


class StatusSelectFilter(abstractselect.AbstractSelectFilter):
    def get_slug(self):
        return 'status'

    def get_label(self):
        return pgettext_lazy('group status', 'Status')

    def get_choices(self):
        return [
            ('', ''),
            ('waiting-for-feedback', pgettext('group status', 'waiting for feedback')),
            ('waiting-for-deliveries', pgettext('group status', 'waiting for deliveries')),
            ('corrected', pgettext('group status', 'corrected')),
        ]

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == 'waiting-for-feedback':
            queryobject = queryobject.filter(annotated_is_waiting_for_feedback__gt=0)
        elif cleaned_value == 'waiting-for-deliveries':
            queryobject = queryobject.filter(annotated_is_waiting_for_deliveries__gt=0)
        elif cleaned_value == 'corrected':
            queryobject = queryobject.filter(annotated_is_corrected__gt=0)
        return queryobject


class PointsFilter(listfilter.django.single.textinput.IntSearch):
    def get_slug(self):
        return 'points'

    def get_label(self):
        return pgettext_lazy('group points filter', 'Points')

    def get_modelfields(self):
        return ['cached_data__last_published_feedbackset__grading_points']

    # def get_placeholder(self):
    #     return pgettext_lazy('group points filter', 'Type a number ...')


class IsPassingGradeFilter(abstractselect.AbstractBoolean):
    def get_slug(self):
        return 'is_passing_grade'

    def get_label(self):
        return pgettext_lazy('group is passing grade filter',
                             'Passing grade?')

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value()
        if cleaned_value in ('true', 'false'):
            query = models.Q(is_passing_grade=False)
            queryobject = queryobject.annotate_with_is_passing_grade_count()
            if cleaned_value == 'true':
                queryobject = queryobject.exclude(query)
            elif cleaned_value == 'false':
                queryobject = queryobject.filter(query)
        return queryobject


class ExaminerFilter(abstractselect.AbstractSelectFilter):
    def __init__(self, **kwargs):
        self.view = kwargs.pop('view', None)
        super(ExaminerFilter, self).__init__(**kwargs)

    def copy(self):
        copy = super(ExaminerFilter, self).copy()
        copy.view = self.view
        return copy

    def get_slug(self):
        return 'examiner'

    def get_label(self):
        return pgettext_lazy('group examiner filter', 'Examiner')

    def __get_examiner_name(self, relatedexaminer):
        return relatedexaminer.user.get_full_name()

    def __get_choices_cached(self):
        if not hasattr(self, '_choices'):
            self._choices = [(str(relatedexaminer.id), self.__get_examiner_name(relatedexaminer))
                             for relatedexaminer in self.view.get_distinct_relatedexaminers()]
        return self._choices

    def __get_valid_values(self):
        return {str(choice[0])
                for choice in self.__get_choices_cached()}

    def get_choices(self):
        choices = [
            ('', '')
        ]
        choices.extend(self.__get_choices_cached())
        return choices

    def get_cleaned_value(self):
        cleaned_value = super(ExaminerFilter, self).get_cleaned_value()
        if cleaned_value:
            if cleaned_value in self.__get_valid_values():
                return cleaned_value
        return None

    def apply_filter(self, queryobject, cleaned_value):
        queryobject = queryobject.filter(examiners__relatedexaminer_id=cleaned_value)
        return queryobject

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value()
        if cleaned_value is not None:
            queryobject = self.apply_filter(queryobject=queryobject, cleaned_value=cleaned_value)
        return queryobject


class ExaminerCountFilter(abstractselect.AbstractSelectFilter):
    def __init__(self, **kwargs):
        self.view = kwargs.pop('view', None)
        super(ExaminerCountFilter, self).__init__(**kwargs)

    def copy(self):
        copy = super(ExaminerCountFilter, self).copy()
        copy.view = self.view
        return copy

    def get_slug(self):
        return 'examinercount'

    def get_label(self):
        return pgettext_lazy('group examiner filter', 'Number of examiners')

    def __get_examiner_name(self, relatedexaminer):
        return relatedexaminer.user.get_full_name()

    def __get_choices_cached(self):
        if not hasattr(self, '_choices'):
            self._choices = [(str(index), str(index))
                             for index in range(0, len(self.view.get_distinct_relatedexaminers()) + 1)]
        return self._choices

    def __get_valid_values(self):
        return {str(choice[0])
                for choice in self.__get_choices_cached()}

    def get_choices(self):
        choices = [
            ('', '')
        ]
        choices.extend(self.__get_choices_cached())
        return choices

    def get_cleaned_value(self):
        cleaned_value = super(ExaminerCountFilter, self).get_cleaned_value()
        if cleaned_value:
            if cleaned_value in self.__get_valid_values():
                return cleaned_value
        return None

    def apply_filter(self, queryobject, cleaned_value):
        queryobject = queryobject\
            .filter(cached_data__examiner_count=int(cleaned_value))
        return queryobject

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value()
        if cleaned_value is not None:
            queryobject = self.apply_filter(queryobject=queryobject, cleaned_value=cleaned_value)
        return queryobject


class CandidateCountFilter(abstractselect.AbstractSelectFilter):
    def __init__(self, **kwargs):
        self.view = kwargs.pop('view', None)
        super(CandidateCountFilter, self).__init__(**kwargs)

    def copy(self):
        copy = super(CandidateCountFilter, self).copy()
        copy.view = self.view
        return copy

    def get_slug(self):
        return 'candidatecount'

    def get_label(self):
        return pgettext_lazy('group student filter', 'Number of students')

    def __get_student_name(self, relatedstudent):
        return relatedstudent.user.get_full_name()

    def __get_choices_cached(self):
        if not hasattr(self, '_choices'):
            self._choices = [(str(index), str(index))
                             for index in range(0, len(self.view.get_distinct_relatedstudents()) + 1)]
        return self._choices

    def __get_valid_values(self):
        return {str(choice[0])
                for choice in self.__get_choices_cached()}

    def get_choices(self):
        choices = [
            ('', '')
        ]
        choices.extend(self.__get_choices_cached())
        return choices

    def get_cleaned_value(self):
        cleaned_value = super(CandidateCountFilter, self).get_cleaned_value()
        if cleaned_value:
            if cleaned_value in self.__get_valid_values():
                return cleaned_value
        return None

    def apply_filter(self, queryobject, cleaned_value):
        queryobject = queryobject\
            .filter(cached_data__candidate_count=int(cleaned_value))
        return queryobject

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value()
        if cleaned_value is not None:
            queryobject = self.apply_filter(queryobject=queryobject, cleaned_value=cleaned_value)
        return queryobject


class ActivityFilter(abstractselect.AbstractSelectFilter):
    def get_slug(self):
        return 'activity'

    def get_label(self):
        return pgettext_lazy('group activity',
                             'Activity')

    def get_choices(self):
        return [
            ('', ''),
            (pgettext_lazy('group activity', 'From student'), (
                ('studentcomment', pgettext_lazy('group activity',
                                                 'Has comment(s) from student')),
                ('studentfile', pgettext_lazy('group activity',
                                              'Has file(s) from student')),
                ('no-studentcomment', pgettext_lazy('group activity',
                                                    'No comments from student')),
                ('no-studentfile', pgettext_lazy('group activity',
                                                 'No files from student')),
            )),
            (pgettext_lazy('group activity', 'From examiner'), (
                ('examinercomment', pgettext_lazy('group activity',
                                                  'Has comment(s) from examiner')),
                ('unpublishedfeedback', pgettext_lazy('group activity',
                                                      'Has unpublished feedback draft')),
                ('privatecomment', pgettext_lazy('group activity',
                                                 'Has unpublished comment(s) from YOU')),
                ('no-examinercomment', pgettext_lazy('group activity',
                                                     'No comments from examiner')),
            )),
            (pgettext_lazy('group activity', 'From administrator'), (
                ('admincomment', pgettext_lazy('group activity',
                                               'Has comment(s) from administrator')),
            ))
        ]

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value()
        if cleaned_value == 'studentcomment':
            queryobject = queryobject.filter(cached_data__public_student_comment_count__gt=0)
        elif cleaned_value == 'no-studentcomment':
            queryobject = queryobject.filter(cached_data__public_student_comment_count=0)
        elif cleaned_value == 'studentfile':
            queryobject = queryobject.filter(cached_data__public_student_file_upload_count__gt=0)
        elif cleaned_value == 'no-studentfile':
            queryobject = queryobject.filter(cached_data__public_student_file_upload_count=0)
        elif cleaned_value == 'examinercomment':
            queryobject = queryobject.filter(cached_data__public_examiner_comment_count__gt=0)
        elif cleaned_value == 'no-examinercomment':
            queryobject = queryobject.filter(cached_data__public_examiner_comment_count=0)
        elif cleaned_value == 'unpublishedfeedback':
            queryobject = queryobject.annotate_with_has_unpublished_feedbackdraft_count()
            queryobject = queryobject.filter(annotated_has_unpublished_feedbackdraft__gt=0)
        elif cleaned_value == 'admincomment':
            queryobject = queryobject.filter(cached_data__public_admin_comment_count__gt=0)
        elif cleaned_value == 'privatecomment':
            queryobject = queryobject.filter(
                models.Q(number_of_private_groupcomments_from_user__gt=0) |
                models.Q(number_of_private_imageannotationcomments_from_user__gt=0))
        return queryobject
