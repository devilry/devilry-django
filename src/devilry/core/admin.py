from models import Node, Subject, Period, Assignment, \
        Delivery, DeliveryCandidate, FileMeta
from django.contrib import admin



class NodeAdmin(admin.ModelAdmin):
    def queryset(self, request):
        return Node.objects.filter(name__contains='ifi')
    

admin.site.register(Node, NodeAdmin)
admin.site.register(Subject)
admin.site.register(Period)
admin.site.register(Assignment)
admin.site.register(Delivery)
admin.site.register(DeliveryCandidate)
admin.site.register(FileMeta)
