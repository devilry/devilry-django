import json

from django.contrib import admin
from django.utils.html import format_html

from devilry.devilry_message.models import MessageReceiver, Message


class MessageReceiverInline(admin.StackedInline):
    model = MessageReceiver
    extra = 0
    fields = ['status']
    readonly_fields = ['status']

    def has_add_permission(self, request):
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
        'created_by',
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
        'created_by',
        'context_type',
        'message_type',
        'get_virtual_message_receivers_pretty',
        'get_metadata_pretty',
        'status',
        'status_data'
    ]
    exclude = [
        'virtual_message_receivers',
        'metadata'
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

    inlines = [
        MessageReceiverInline
    ]

    def has_add_permission(self, request):
        return False


admin.site.register(Message, MessageAdmin)


class MessageReceiverAdmin(admin.ModelAdmin):
    raw_id_fields = [
        'message',
        'user'
    ]
    list_display = [
        'id',
        'send_to',
        'subject',
        'user',
        'status',
        'sent_datetime',
        'message',
        'get_message_sent_by',
    ]
    search_fields = [
        'id',
        'send_to',
        'user__id',
        'message__subject',
        'message__created_by__id',
    ]
    list_filter = [
        'status',
        'sent_datetime',
    ]

    readonly_fields = [
        'send_to',
        'subject',
        'user',
        'status',
        'subject',
        'message_content_html',
        'message_content_plain',
        'status_data',
        'sent_datetime',
        'message',
        'message_type',
        'get_message_sent_by'
    ]

    def get_message_sent_by(self, obj):
        return obj.message.created_by
    get_message_sent_by.short_description = 'Message sent by'

    def has_add_permission(self, request):
        return False

admin.site.register(MessageReceiver, MessageReceiverAdmin)
