from django.db import transaction
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

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

    @sensitive_post_parameters()
    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, *args, **kwargs):
        """
        Add InlineDevilryUserProfile to change form.
        """
        self.inlines = [InlineDevilryUserProfile]
        return super(UserAdmin, self).change_view(*args, **kwargs)


admin.site.unregister(User)
if not _get_setting('DEVILRY_USERADMIN_USER_INCLUDE_PERMISSIONFRAMEWORK'):
    admin.site.unregister(Group)
admin.site.register(User, DevilryUserAdmin)
