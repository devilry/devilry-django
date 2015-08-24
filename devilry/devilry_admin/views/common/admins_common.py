from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.views.generic.edit import BaseFormView
from django_cradmin.viewhelpers import objecttable
from django.utils.translation import ugettext_lazy as _
from django_cradmin.viewhelpers import delete

from devilry.devilry_admin.views.common import userselect_common


class GetQuerysetForRoleMixin(object):
    #: Must be set in subclasses. Example: ``Subject.admins.through``
    model = None

    #: The field in the many-to-many model pointing to the basenode.
    #: Must be set in subclasses. Example: ``subject``
    basenodefield = None

    def get_queryset_for_role(self, role):
        return self.model.objects \
            .filter(**{self.basenodefield: role}) \
            .order_by('user__shortname')

    def get_basenode_for_object(self, obj):
        return getattr(obj, self.basenodefield)


class AdministratorInfoColumn(objecttable.MultiActionColumn):
    modelfield = 'id'
    template_name = 'devilry_admin/common/administrator-info-column.django.html'

    def get_header(self):
        return _('Administrators')

    def get_buttons(self, obj):
        if not self.view.request.user.is_superuser and obj.user == self.view.request.user:
            return []
        else:
            return [
                objecttable.Button(
                    label=_('Remove'),
                    url=self.reverse_appurl('remove', args=[obj.id]),
                    buttonclass="btn btn-danger btn-sm devilry-admin-adminlist-remove-button"),
            ]

    def get_context_data(self, obj):
        context = super(AdministratorInfoColumn, self).get_context_data(obj=obj)
        context['user'] = obj.user
        return context


class AbstractAdminsListView(GetQuerysetForRoleMixin, objecttable.ObjectTableView):
    columns = [
        AdministratorInfoColumn,
    ]
    searchfields = ['shortname', 'fullname']
    hide_column_headers = True

    def get_buttons(self):
        app = self.request.cradmin_app
        return [
            objecttable.Button(label=_('Add administrator'),
                               url=app.reverse_appurl('add-select-user'),
                               buttonclass='btn btn-primary'),
        ]

    def get_pagetitle(self):
        return _('Administrators for %(what)s') % {
            'what': self.request.cradmin_role.long_name
        }


class AbstractRemoveAdminView(GetQuerysetForRoleMixin, delete.DeleteView):
    """
    View used to remove admins from a basenode.
    """

    def get_queryset_for_role(self, role):
        queryset = super(AbstractRemoveAdminView, self) \
            .get_queryset_for_role(role=role)
        if not self.request.user.is_superuser:
            queryset = queryset.exclude(user=self.request.user)
        return queryset

    def get_object(self, *args, **kwargs):
        if not hasattr(self, '_object'):
            self._object = super(AbstractRemoveAdminView, self).get_object(*args, **kwargs)
        return self._object

    def get_pagetitle(self):
        return _('Remove %(what)s') % {'what': self.get_object().user.get_full_name()}

    def get_success_message(self, object_preview):
        basenode_admin = self.get_object()
        basenode = self.get_basenode_for_object(basenode_admin)
        user = basenode_admin.user
        return _('%(user)s is no longer administrator for %(what)s.') % {
            'user': user.get_full_name(),
            'what': basenode,
        }

    def get_confirm_message(self):
        basenode_admin = self.get_object()
        basenode = self.get_basenode_for_object(basenode_admin)
        user = basenode_admin.user
        return _('Are you sure you want to remove %(user)s as administrator for %(what)s?') % {
            'user': user.get_full_name(),
            'what': basenode,
        }

    def get_action_label(self):
        return _('Remove')


class UserInfoColumn(userselect_common.UserInfoColumn):
    modelfield = 'shortname'
    select_label = _('Add as administrator')


class AdminUserSelectView(userselect_common.AbstractUserSelectView):
    columns = [
        UserInfoColumn,
    ]

    def get_pagetitle(self):
        return _('Please select the user you want to add as administrator for %(what)s') % {
            'what': self.request.cradmin_role.long_name
        }


class AbstractAddAdminView(BaseFormView):
    """
    View used to add an admin to a basenode.
    """
    http_method_names = ['post']

    #: Must be set in subclasses. Example: ``Subject.admins.through``
    model = None

    #: The field in the many-to-many model pointing to the basenode.
    #: Must be set in subclasses. Example: ``subject``
    basenodefield = None

    def get_form_class(self):
        basenode = self.request.cradmin_role
        userqueryset = get_user_model().objects \
            .exclude(pk__in=basenode.admins.values_list('id', flat=True))

        class AddAdminForm(forms.Form):
            user = forms.ModelChoiceField(
                queryset=userqueryset)
            next = forms.CharField(required=False)

        return AddAdminForm

    def __make_user_admin(self, user):
        basenode = self.request.cradmin_role
        self.model.objects.create(user=user,
                                  **{self.basenodefield: basenode})

    def form_valid(self, form):
        user = form.cleaned_data['user']
        self.__make_user_admin(user)

        basenode = self.request.cradmin_role
        successmessage = _('%(user)s added as administrator for %(what)s.') % {
            'user': user.get_full_name(),
            'what': basenode,
        }
        messages.success(self.request, successmessage)

        if form.cleaned_data['next']:
            nexturl = form.cleaned_data['next']
        else:
            nexturl = self.request.cradmin_app.reverse_appindexurl()
        return HttpResponseRedirect(nexturl)

    def form_invalid(self, form):
        messages.error(self.request,
                       _('Error: The user may not exist, or it may already be administrator.'))
        return HttpResponseRedirect(self.request.cradmin_app.reverse_appindexurl())
