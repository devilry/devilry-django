from __future__ import unicode_literals

from django.db import models

from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_admin.views.period.manage_tags import bulk_manage_tags
from devilry.apps.core.models import relateduser
from devilry.apps.core.models import PeriodTag

#
# class GetQuerySetForRoleMixin(object):
#     model = relateduser.RelatedStudent
#
#     def __get_tag_queryset(self):
#         return relateduser.RelatedStudentTag.objects\
#             .select_related('relatedstudent__user')
#
#     def get_queryset_for_role(self, role):
#         period = role
#         return self.model.objects\
#             .filter(period=period)\
#             .select_related('user', 'period', 'period__parentnode')\
#             .prefetch_related(
#                 models.Prefetch(
#                     'relatedstudenttag_set',
#                     queryset=self.__get_tag_queryset()))\
#             .order_by('user__shortname')
#
#
# class GetTagListQuerySetForRoleMixin(object):
#     model = relateduser.RelatedStudentTag
#
#     def get_queryset_for_role(self, role):
#         period = role
#         return self.model.objects\
#             .get_all_distinct_tags_in_period(period=period)
#
#
class SelectMethod(bulk_manage_tags.SelectMethodView):
    """
    Select how to manage tags.
    """
    def get_context_data(self, **kwargs):
        context_data = super(SelectMethod, self).get_context_data(**kwargs)
        context_data['relateduser_type'] = 'student'
        return context_data

#
# class TagListItemFrame(bulk_manage_tags.TagItemFrame):
#     def get_url(self):
#         return reverse_cradmin_url(
#             instanceid='devilry_admin_periodadmin',
#             appname='manage_tags_students',
#             roleid=self.kwargs.get('period').id,
#             viewname='remove-tag',
#             kwargs={
#                 'tag': self.value
#             }
#         )
#
#
# class ReplaceTagListItemFrame(bulk_manage_tags.TagItemFrame):
#     def get_url(self):
#         return reverse_cradmin_url(
#             instanceid='devilry_admin_periodadmin',
#             appname='manage_tags_students',
#             roleid=self.kwargs.get('period').id,
#             viewname='replace-tag',
#             kwargs={
#                 'tag': self.value
#             }
#         )
#
#
# class RemoveTagListBuilderView(GetTagListQuerySetForRoleMixin, bulk_manage_tags.BaseTagListbuilderView):
#     """
#     List distinct tags to remove.
#     """
#     model = relateduser.RelatedStudentTag
#     frame_renderer_class = TagListItemFrame
#
#
# class ReplaceTagListBuilderView(GetTagListQuerySetForRoleMixin, bulk_manage_tags.BaseTagListbuilderView):
#     """
#     List distinct tags to replace.
#     """
#     model = relateduser.RelatedStudentTag
#     frame_renderer_class = ReplaceTagListItemFrame
#
#
# class AddTagMultiSelectView(GetQuerySetForRoleMixin, bulk_manage_tags.AddTagMultiSelectView):
#     """
#     Add tags.
#     """
#     model = relateduser.RelatedStudent
#     tag_model = relateduser.RelatedStudentTag
#
#     def instantiate_tag_class(self, tag, related_user):
#         return relateduser.RelatedStudentTag(tag=tag, relatedstudent=related_user)
#
#     def get_success_url(self):
#         return reverse_cradmin_url(
#             instanceid='devilry_admin_periodadmin',
#             appname='students',
#             viewname=crapp.INDEXVIEW_NAME,
#             roleid=self.request.cradmin_role.id
#         )
#
#
# class RemoveTagMultiselectView(GetQuerySetForRoleMixin, bulk_manage_tags.RemoveTagMultiSelectView):
#     """
#     Remove tag.
#     """
#     model = relateduser.RelatedStudent
#     tag_model = relateduser.RelatedStudentTag
#
#     def get_queryset_for_role(self, role):
#         tag_relateduser_ids = relateduser.RelatedStudentTag.objects\
#             .filter(tag=self.tag, prefix='')\
#             .values_list('relatedstudent_id', flat=True)
#         relateduser_queryset = super(RemoveTagMultiselectView, self)\
#             .get_queryset_for_role(role).filter(id__in=tag_relateduser_ids)
#         return relateduser_queryset
#
#     def get_tag_queryset_to_delete(self, form):
#         return relateduser.RelatedStudentTag.objects\
#             .filter(relatedstudent_id__in=self.get_relateduser_ids_list(form))
#
#     def get_success_url(self):
#         return reverse_cradmin_url(
#             instanceid='devilry_admin_periodadmin',
#             appname='students',
#             viewname=crapp.INDEXVIEW_NAME,
#             roleid=self.request.cradmin_role.id
#         )
#
#
# class ReplaceTagMultiSelectView(GetQuerySetForRoleMixin, bulk_manage_tags.ReplaceTagMultiSelectView):
#     """
#     Replace and add tags.
#     """
#     model = relateduser.RelatedStudent
#     tag_model = relateduser.RelatedStudentTag
#
#     def instantiate_tag_class(self, tag, related_user):
#         return relateduser.RelatedStudentTag(tag=tag, relatedstudent=related_user)
#
#     def get_related_user_ids_from_tags(self):
#         return self.tag_model.objects \
#             .filter(tag=self.tag, prefix='').values_list('relatedstudent_id', flat=True)
#
#     def get_queryset_for_role(self, role):
#         tag_relateduser_ids = self.get_related_user_ids_from_tags()
#         relateduser_queryset = super(ReplaceTagMultiSelectView, self) \
#             .get_queryset_for_role(role) \
#             .filter(id__in=tag_relateduser_ids)
#         return relateduser_queryset
#
#     def get_transaction_error_redirect_url(self):
#         return reverse_cradmin_url(
#                 instanceid='devilry_admin_periodadmin',
#                 appname='manage_tags_students',
#                 roleid=self.request.cradmin_role.id,
#                 viewname='replace-tag',
#                 kwargs={
#                     'tag': self.tag
#                 }
#             )
#
#     def get_tags_for_users_to_replace(self, related_users_ids):
#         return self.tag_model.objects\
#             .filter(tag=self.tag, relatedstudent_id__in=related_users_ids)
#
#     def get_success_url(self):
#         return reverse_cradmin_url(
#             instanceid='devilry_admin_periodadmin',
#             appname='students',
#             viewname=crapp.INDEXVIEW_NAME,
#             roleid=self.request.cradmin_role.id
#         )
#
#
# class App(bulk_manage_tags.App):
#     @classmethod
#     def get_index_view_class(cls):
#         return SelectMethod
#
#     @classmethod
#     def get_add_tag_view_class(cls):
#         return AddTagMultiSelectView
#
#     @classmethod
#     def get_choose_remove_tag_list_view_class(cls):
#         return RemoveTagListBuilderView
#
#     @classmethod
#     def get_choose_replace_tag_list_view_class(cls):
#         return ReplaceTagListBuilderView
#
#     @classmethod
#     def get_remove_tag_select_view_class(cls):
#         return RemoveTagMultiselectView
#
#     @classmethod
#     def get_replace_tag_select_view_class(cls):
#         return ReplaceTagMultiSelectView
