from models import *
#from models import Node, Subject, Period, Assignment, \
        #Delivery, DeliveryCandidate, FileMeta
from django.contrib import admin
from django.db.models import Q
from django import forms



class InstanceAuthModelAdminMixin(object):
    """ Mixin for ModelAdmin where the obj-argument in has_change_permission and
    has_delete_permission is forwarded to the auth backend. Must be mixed in *before*
    modeladmin. Example::
        >>> class ExampleModelAdmin(InstanceAuthModelAdmin, admin.ModelAdmin):
        ...    list_display = ['test', 'field']
    """

    def queryset(self, request):
        if request.user.is_superuser:
            return self.model.objects.all()
        else:
            return self.model.get_changelist(request.user)

    #def has_change_permission(self, request, obj=None):
        #"""
        #Returns True if the given request has permission to change the given
        #Django model instance.

        #If `obj` is None, this should return True if the given request has
        #permission to change *any* object of the given type.
        #"""
        #print 'has_change_permission', obj
        #opts = self.opts
        #return request.user.has_perm(
                #opts.app_label + '.' + opts.get_change_permission(), obj)

    #def has_delete_permission(self, request, obj=None):
        #"""
        #Returns True if the given request has permission to change the given
        #Django model instance.

        #If `obj` is None, this should return True if the given request has
        #permission to delete *any* object of the given type.
        #"""
        #print 'has_delete_permission', obj
        #opts = self.opts
        #return request.user.has_perm(
                #opts.app_label + '.' + opts.get_delete_permission(), obj)



class InstanceAuthModelAdmin(InstanceAuthModelAdminMixin, admin.ModelAdmin):
    """ ModelAdmin where the obj-argument in has_change_permission and
    has_delete_permission is forwarded to the auth backend. """


class BaseNodeAdmin(InstanceAuthModelAdmin):
    list_display = ('short_name', 'long_name', 'get_path')
    search_fields = ['short_name', 'long_name']

    #def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        #if request:
            #meta = self.model._meta
            #perm = '%s.%s' % (meta.app_label, meta.get_add_permission())
            #if not request.user.is_superuser and request.user.has_perm(perm):
                #pcls = self.model.parentnode.field.related.parent_model
                #db_field.rel.limit_choices_to = pcls.qry_where_is_admin(request.user)
        #return db_field.formfield(**kwargs)


    #def get_readonly_fields(self, request, obj=None):
        #if obj:
            #meta = self.model._meta
            #perm = '%s.%s' % (meta.app_label, meta.get_add_permission())
            #if not request.user.has_perm(perm):
                #r = ['parentnode']
                #r.extend(self.readonly_fields)
                #return r
        #return self.readonly_fields


class NodeAdmin(BaseNodeAdmin):

    @classmethod
    def get_admnodes(cls, user):
        admnodes = Node.objects.filter(admins=user)
        l = []
        def add_admnodes(admnodes):
            for a in admnodes.all():
                l.append(a.id)
                add_admnodes(a.node_set)
        add_admnodes(admnodes)
        return l


class SubjectAdmin(BaseNodeAdmin):
    pass


class PeriodAdmin(BaseNodeAdmin):
    list_display = ['parentnode', 'short_name', 'start_time', 'end_time', 'admins_unicode']
    search_fields = ['short_name', 'long_name', 'parentnode__short_name']
    list_filter = ['start_time', 'end_time']
    ordering = ['parentnode']


class AssignmentAdmin(BaseNodeAdmin):
    pass

class DeliveryAdmin(admin.ModelAdmin):
    pass



class FileMetaInline(admin.TabularInline):
    model = FileMeta
    extra = 1
class DeliveryCandidateAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'id']
    inlines = (FileMetaInline,)


admin.site.register(Node, NodeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Assignment, AssignmentAdmin)

admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(DeliveryCandidate, DeliveryCandidateAdmin)
