import json

from django.contrib import admin
from django.utils.html import format_html

from devilry.devilry_message.models import MessageReceiver, Message


class MessageReceiverInline(admin.StackedInline):
    model = MessageReceiver
    extra = 0
    fields = ['status']
    readonly_fields = ['status']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MessageAdmin(admin.ModelAdmin):
    raw_id_fields = [
        'created_by'
    ]
    list_display = [
        'id',
        'status',
        'created_datetime',
        'virtual_message_receivers',
        'context_type'
    ]
    search_fields = [
        'id',
        'subject',
        'created_by__id',
    ]
    readonly_fields = [
        'created_datetime',
        'context_type',
        'message_type',
        'get_virtual_message_receivers_pretty',
        'get_metadata_pretty',
        'status',
        'get_status_data_pretty'
    ]
    exclude = [
        'virtual_message_receivers',
        'metadata',
        'status_data',
        'created_by'
    ]
    list_filter = [
        'status',
        'context_type',
        'created_datetime'
    ]

    def get_virtual_message_receivers_pretty(self, obj):
        return format_html('<pre>{}</pre>', json.dumps(obj.virtual_message_receivers, indent=2, sort_keys=True))
    get_virtual_message_receivers_pretty.short_description = 'Virtual message receivers pretty'

    def get_metadata_pretty(self, obj):
        return format_html('<pre>{}</pre>', json.dumps(obj.metadata, indent=2, sort_keys=True))
    get_metadata_pretty.short_description = 'Metadata pretty'

    def get_status_data_pretty(self, obj):
        return format_html('<pre>{}</pre>', json.dumps(obj.status_data, indent=2, sort_keys=True))
    get_status_data_pretty.short_description = 'Status data'

    inlines = [
        MessageReceiverInline
    ]

    def has_add_permission(self, request):
        return False


admin.site.register(Message, MessageAdmin)


def message_receiver_send(modeladmin, request, queryset):
    for message_receiver in queryset:
        message_receiver.send()


message_receiver_send.short_description = 'Send message to selected receivers'


class MessageReceiverAdmin(admin.ModelAdmin):
    actions = [message_receiver_send]
    raw_id_fields = [
        'message',
        'user'
    ]
    exclude = [
        'status_data',
        'metadata',
        'send_to',
        'message_type'
    ]
    list_display = [
        'id',
        'created_datetime',
        'subject',
        'user',
        'sending_failed_count',
        'sending_success_count',
        'status',
        'sent_datetime',
        'get_message_context_type'
    ]
    search_fields = [
        'id',
        'user__id',
        'user__shortname',
        'user__fullname'
    ]
    list_filter = [
        'status',
        'sent_datetime',
        'message__context_type'
    ]

    readonly_fields = [
        'created_datetime',
        'send_to',
        'user',
        'status',
        'subject',
        'message_content_html',
        'message_content_plain',
        'get_status_data_pretty',
        'sent_datetime',
        'sending_failed_count',
        'sending_success_count',
        'message',
        'message_type',
        'get_metadata_pretty'
    ]

    def get_message_context_type(self, obj):
        return Message.CONTEXT_TYPE_CHOICES[obj.message.context_type].label
    get_message_context_type.short_description = 'Type'

    def get_status_data_pretty(self, obj):
        return format_html('<pre>{}</pre>', json.dumps(obj.status_data, indent=2, sort_keys=True))
    get_status_data_pretty.short_description = 'Status data'

    def get_metadata_pretty(self, obj):
        return format_html('<pre>{}</pre>', json.dumps(obj.metadata, indent=2, sort_keys=True))
    get_metadata_pretty.short_description = 'Metadata pretty'

    def has_add_permission(self, request):
        return False

admin.site.register(MessageReceiver, MessageReceiverAdmin)
