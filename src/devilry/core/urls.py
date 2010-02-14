from django.conf.urls.defaults import *

urlpatterns = patterns('devilry.core',
    (r'^dashboard/$', 'views.dashboard'),
    #(r'^deliver/(?P<deliveryid>\d+)/form$', 'views.deliver'),
    (r'^deliver/(?P<deliveryid>\d+)/start$', 'views.start_delivery'),
    url(r'^deliver/(?P<deliveryid>\d+)/create$', 'views.create_delivery',
        name='create-delivery'),
    url(r'^deliver/(?P<deliveryid>\d+)/(?P<deliverycand_id>\d+)/edit$',
        'views.create_delivery', name='edit-delivery'),
    #(r'^deliver/(?P<deliveryid>\d+)/edit$', 'views.edit_delivery'),
)
