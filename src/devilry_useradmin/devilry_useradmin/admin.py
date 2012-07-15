from django.db import transaction
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.admin.util import unquote
from django.core.exceptions import ValidationError
from django.utils.encoding import force_unicode
from django.shortcuts import render, redirect
from django.contrib import messages

from devilry.apps.core.models import DevilryUserProfile

from .forms import CustomUserCreationForm
from .forms import CustomUserChangeForm



csrf_protect_m = method_decorator(csrf_protect)


def _get_setting(attrname, default=None):
    if hasattr(settings, attrname):
        return getattr(settings, attrname)
    else:
        return default


def _get_permissions_fields():
    fields = ('is_active', 'is_staff', 'is_superuser')
    if _get_setting('DEVILRY_USERADMIN_USER_INCLUDE_PERMISSIONFRAMEWORK'):
        fields += ('groups', 'user_permissions')
    return fields


class InlineDevilryUserProfile(admin.StackedInline):
    model = DevilryUserProfile
    readonly_fields = _get_setting('DEVILRY_USERADMIN_DEVILRYUSERPROFILE_READONLY_FIELDS',
                                   default=('languagecode',))
    max_num = 1
    can_delete = False


class DevilryUserAdmin(UserAdmin):

    # Customize the edit/add forms
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    readonly_fields = ('last_login', 'date_joined') + settings.DEVILRY_USERADMIN_USER_READONLY_FIELDS
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email')}),
        #(_('Not used by devilry'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': _get_permissions_fields()}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email')}
        ),
    )

    # Customize the listing
    list_display = ('username', 'full_name', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'devilryuserprofile__languagecode')
    search_fields = ('username', 'devilryuserprofile__full_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('user_permissions',)

    def full_name(self, user):
        return user.devilryuserprofile.full_name

    def queryset(self, request):
        queryset = super(UserAdmin, self).queryset(request)
        return queryset.select_related('devilryuserprofile')

    @sensitive_post_parameters()
    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, *args, **kwargs):
        """
        Do not show InlineDevilryUserProfile on the add form.
        """
        self.inlines = []
        return super(DevilryUserAdmin, self).add_view(*args, **kwargs)

    def _parse_change_form_for_dangerous_attributes(self, request, object_id):
        obj = self.get_object(request, unquote(object_id))
        saved_data = {'is_staff': obj.is_staff,
                      'is_superuser': obj.is_superuser}
        ModelForm = self.get_form(request, obj)
        formsets = []
        inline_instances = self.get_inline_instances(request)
        form = ModelForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            return obj, saved_data, form.cleaned_data
        else:
            raise ValidationError()

    def _check_for_changes_to_dangerous_attributes(self, request, object_id):
        obj, saved_data, cleaned_data = self._parse_change_form_for_dangerous_attributes(request, object_id)
        changed_dangerous_attributes = []
        for attrname in ('is_staff', 'is_superuser'):
            if cleaned_data[attrname] != saved_data[attrname] and cleaned_data[attrname] == True:
                changed_dangerous_attributes.append(attrname)
        return obj, changed_dangerous_attributes

    def _show_confirm_view(self, request, obj, changed_dangerous_attributes):
        warnings = {'is_staff': _('Enable the user to log in to this admin site, which is normally only for administrators.'),
                    'is_superuser': _('Grant the user permission to view, edit and delete EVERYTHING.')}
        warningmessages = [warnings[attrname] for attrname in changed_dangerous_attributes]
        request.session['before_confirm_request_data'] = request.POST

        context = {"title": _('Confirm change {username}').format(username=obj.username),
                   "object_name": force_unicode(self.model._meta.verbose_name),
                   "object": obj,
                   "opts": self.model._meta,
                   "app_label": self.model._meta.app_label,
                   "warningmessages": warningmessages}
        return render(request,
                      'devilry_useradmin/confirm_change_view.django.html',
                      context, current_app=self.admin_site.name)

    @sensitive_post_parameters()
    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, request, object_id, *args, **kwargs):
        """
        Add InlineDevilryUserProfile to change form.
        """
        self.inlines = [InlineDevilryUserProfile]
        if request.method == 'POST':
            if request.POST.get('dangerous_changes_cancel'):
                del request.session['before_confirm_request_data']
                messages.add_message(request, messages.INFO, _('Save cancelled by user. Nothing was saved.'))
                urlname = '{site_name}:auth_user_change'.format(site_name=self.admin_site.name)
                return redirect(urlname, object_id)
            if request.POST.get('dangerous_changes_confirmed'):
                request.POST = request.session['before_confirm_request_data']
                del request.session['before_confirm_request_data']
            else:
                # Check if any dangerous attributes have been changed, and show confirm page if so
                try:
                    obj, changed_dangerous_attributes = self._check_for_changes_to_dangerous_attributes(request, object_id)
                    if changed_dangerous_attributes:
                        return self._show_confirm_view(request, obj, changed_dangerous_attributes)
                except ValidationError:
                    pass # Ignore errors, since they are handled in super.change_view()
        return super(UserAdmin, self).change_view(request, object_id, *args, **kwargs)




admin.site.unregister(User)
if not _get_setting('DEVILRY_USERADMIN_USER_INCLUDE_PERMISSIONFRAMEWORK'):
    admin.site.unregister(Group)
admin.site.register(User, DevilryUserAdmin)
