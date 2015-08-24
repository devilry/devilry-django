from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import models as authmodels
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _

from devilry.devilry_account.models import User, UserEmail, UserName


class UserEmailInline(admin.StackedInline):
    model = UserEmail
    extra = 0


class UserNameInline(admin.StackedInline):
    model = UserName
    extra = 0


class UserEditForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class DevilryUserAdmin(UserAdmin):
    form = UserEditForm
    list_display = [
        'id',
        'shortname',
        'fullname',
        'lastname',
        'primary_email',
        'primary_username',
        'is_superuser',
        'suspended_datetime',
    ]
    search_fields = [
        'id',
        'shortname',
        'fullname',
        'useremail__email',
        'username__username',
    ]
    list_filter = [
        'is_superuser',
        'suspended_datetime',
    ]
    fieldsets = [
        (None, {'fields': ['shortname', 'fullname', 'lastname', 'languagecode', 'password']}),
        ('Permissions', {'fields': [
            'is_superuser',
        ]}),
        ('Suspend the user', {'fields': [
            'suspended_datetime',
            'suspended_reason',
        ]}),
        ('Metadata', {'fields': [
            'datetime_joined',
            'last_login',
            'lastname',
        ]})
    ]
    readonly_fields = ['datetime_joined', 'last_login']
    filter_horizontal = []
    ordering = ('shortname',)
    inlines = [
        UserEmailInline,
        UserNameInline,
    ]

    def get_queryset(self, request):
        return super(DevilryUserAdmin, self).get_queryset(request)\
            .prefetch_related_primary_email()\
            .prefetch_related_primary_username()

    def has_add_permission(self, request):
        return False

admin.site.unregister(authmodels.Group)
admin.site.register(User, DevilryUserAdmin)
