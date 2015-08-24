from django_cradmin.viewhelpers import objecttable
from django.utils.translation import ugettext_lazy as _
from django_cradmin.viewhelpers import delete


class GetQuerysetForRoleMixin(object):
    #: Must be set in subclasses. Example: ``Subject.admins.through``
    model = None

    #: The field in the many-to-many model pointing to the basenode.
    #: Must be set in subclasses. Example: ``subject``
    basenodefield = 'subject'

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

    # def get_buttons(self):
    #     app = self.request.cradmin_app
    #     return [
    #         objecttable.Button(label=_('Add administrator'),
    #                            url=app.reverse_appurl('add'),
    #                            buttonclass='btn btn-primary'),
    #     ]

    def get_pagetitle(self):
        return _('Administrators for %(what)s') % {
            'what': self.request.cradmin_role.long_name
        }


class AbstractRemoveAdminView(GetQuerysetForRoleMixin, delete.DeleteView):
    """
    View used to remove admins from a basenode.
    """

    def get_queryset_for_role(self, role):
        queryset = super(AbstractRemoveAdminView, self)\
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
