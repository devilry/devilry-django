from django.db import transaction
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.conf import settings

from .forms import UserCreationForm
from .forms import UserChangeForm

csrf_protect_m = method_decorator(csrf_protect)


class UserAdmin(admin.ModelAdmin):
    #add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('username', 'email')}),
        (_('Devilry metadata'), {'fields': ('first_name',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',)}
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('username', 'full_name', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'devilryuserprofile__full_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('user_permissions',)
    readonly_fields = ('last_login', 'date_joined') + settings.DEVILRY_USERADMIN_USER_READONLY_FIELDS

    def full_name(self, user):
        return user.devilryuserprofile.full_name

    def queryset(self, request):
        queryset = super(UserAdmin, self).queryset(request)
        return queryset.select_related('devilryuserprofile')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(UserAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
                'fields': admin.util.flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(UserAdmin, self).get_form(request, obj, **defaults)


    @sensitive_post_parameters()
    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': self.model._meta.get_field('username').help_text,
        }
        extra_context.update(defaults)
        return super(UserAdmin, self).add_view(request, form_url,
                                               extra_context)


def register_useradmin(adminsite):
    adminsite.register(User, UserAdmin)
