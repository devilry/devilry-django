import json
from django import forms
from django.contrib import admin
from django.contrib.auth import models as authmodels
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy

from devilry.devilry_account.models import MergedUser, PeriodUserGuidelineAcceptance, SubjectPermissionGroup, PeriodPermissionGroup
from devilry.devilry_account.models import User, UserEmail, UserName, PermissionGroup, PermissionGroupUser


class UserEmailInline(admin.StackedInline):
    model = UserEmail
    extra = 0


class UserNameInline(admin.StackedInline):
    model = UserName
    extra = 0


class UserEditForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=gettext_lazy("Password"),
        help_text=gettext_lazy("Raw passwords are not stored, so there is no way to see "
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
        'is_active',
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


class MergedUserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'source_user',
        'target_user',
    ]

    search_fields = [
        '=id',

        '=source_user__id',
        'source_user__shortname',
        'source_user__fullname',
        'source_user__useremail__email',
        'source_user__username__username',

        '=target_user__id',
        'target_user__shortname',
        'target_user__fullname',
        'target_user__useremail__email',
        'target_user__username__username',
    ]

    raw_id_fields = [
        'source_user',
        'target_user',
    ]

    fields = [
        'source_user',
        'target_user',
        'get_summary_json_pretty',
    ]

    readonly_fields = [
        'source_user',
        'target_user',
        'get_summary_json_pretty',
    ]

    @admin.display(
        description='Summary json'
    )
    def get_summary_json_pretty(self, obj):
        return format_html(
            '<pre>{}</pre>',
            json.dumps(obj.summary_json, indent=2, sort_keys=True)
        )


admin.site.register(MergedUser, MergedUserAdmin)


class PermissionGroupUserInline(admin.TabularInline):
    model = PermissionGroupUser
    raw_id_fields = ['user']
    extra = 0


class SubjectPermissionGroupInline(admin.TabularInline):
    model = SubjectPermissionGroup
    raw_id_fields = ['subject']
    extra = 0


class PeriodPermissionGroupInline(admin.TabularInline):
    model = PeriodPermissionGroup
    raw_id_fields = ['period']
    extra = 0


class PermissionGroupAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'is_custom_manageable',
        'grouptype',
        'get_users',
        'created_datetime',
        'updated_datetime',
        'syncsystem_update_datetime',
    ]

    search_fields = [
        'id',
        'name',
        'grouptype',
    ]

    list_filter = [
        'grouptype',
        'is_custom_manageable',
        'created_datetime',
        'updated_datetime',
        'syncsystem_update_datetime',
    ]

    inlines = [
        PermissionGroupUserInline,
        SubjectPermissionGroupInline,
        PeriodPermissionGroupInline
    ]

    def get_queryset(self, request):
        return super(PermissionGroupAdmin, self).get_queryset(request)\
            .prefetch_related('users')

    def get_users(self, permissiongroup):
        return ', '.join(user.shortname for user in permissiongroup.users.all())
    get_users.short_description = gettext_lazy('Users')

    def get_inline_instances(self, request, obj=None):
        inline_instances = [
            PermissionGroupUserInline(self.model, self.admin_site)
        ]
        if obj:
            if obj.grouptype == PermissionGroup.GROUPTYPE_DEPARTMENTADMIN:
                inline_instances.append(SubjectPermissionGroupInline(self.model, self.admin_site))
            elif obj.grouptype == PermissionGroup.GROUPTYPE_SUBJECTADMIN:
                inline_instances.append(SubjectPermissionGroupInline(self.model, self.admin_site))
            elif obj.grouptype == PermissionGroup.GROUPTYPE_PERIODADMIN:
                inline_instances.append(PeriodPermissionGroupInline(self.model, self.admin_site))
        return inline_instances

    def get_readonly_fields(self, request, permissiongroup=None):
        readonly_fields = [
            'created_datetime',
            'updated_datetime',
            'syncsystem_update_datetime',
        ]
        if permissiongroup is not None:
            readonly_fields.append('grouptype')
        return readonly_fields

admin.site.register(PermissionGroup, PermissionGroupAdmin)


class SubjectPermissionGroupAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'permissiongroup',
        'subject',
    ]

    search_fields = [
        'id',
        'permissiongroup',
        'subject',
    ]

    list_filter = [
        'permissiongroup',
        'subject',
    ]

    raw_id_fields = [
        'permissiongroup',
        'subject'
    ]


admin.site.register(SubjectPermissionGroup, SubjectPermissionGroupAdmin)


class PeriodPermissionGroupAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'permissiongroup',
        'period',
    ]

    search_fields = [
        'id',
        'permissiongroup',
        'period',
    ]

    list_filter = [
        'permissiongroup',
        'period',
    ]

    raw_id_fields = [
        'permissiongroup',
        'period'
    ]


admin.site.register(PeriodPermissionGroup, PeriodPermissionGroupAdmin)


class UserEmailAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'email',
        'is_primary',
    ]

    search_fields = [
        'id',
        'user__shortname',
        'user__fullname',
        'email',
    ]

    list_filter = [
        'is_primary'
    ]


admin.site.register(UserEmail, UserEmailAdmin)


class UserNameAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'username',
        'is_primary',
    ]

    search_fields = [
        'id',
        'user__shortname',
        'user__fullname',
        'username',
    ]

    list_filter = [
        'is_primary'
    ]


admin.site.register(UserName, UserNameAdmin)



class PeriodUserGuidelineAcceptanceAdmin(admin.ModelAdmin):
    readonly_fields = [
        'user',
        'period',
        'devilryrole',
        'accepted_datetime',
        'guidelines_version',
        'matched_regex',
    ]
    search_fields = [
        '=period__short_name',
        '=period__id',
        '=period__parentnode__short_name',
        '=period__parentnode__id',
        '=user__shortname',
    ]
    list_display = [
        'user',
        'period',
        'devilryrole',
        'accepted_datetime',
        'guidelines_version',
        'matched_regex',
    ]
    list_filter = [
        'accepted_datetime',
        'devilryrole',
        'matched_regex',
        'guidelines_version',
    ]

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False


admin.site.register(PeriodUserGuidelineAcceptance, PeriodUserGuidelineAcceptanceAdmin)
