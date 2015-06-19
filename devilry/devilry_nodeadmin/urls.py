# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.i18n import javascript_catalog
from devilry.devilry_nodeadmin.views import AppView, RedirectToNodeAdminAppView

from devilry.project.common.i18n import get_javascript_catalog_packages
from devilry.devilry_nodeadmin import cradmin
from devilry.devilry_nodeadmin.crapps import listpermissionnodes
from django.shortcuts import redirect
from django_cradmin import crinstance
from devilry.apps.core.models import node

i18n_packages = get_javascript_catalog_packages(
    'devilry_nodeadmin',
    'devilry_header', 
    'devilry_extjsextras', 
    'devilry.apps.core'
)

# @login_required
# def redirect_to_nodeadmin_frontpage_view(request):
#     return redirect(crinstance.reverse_cradmin_url(
#         instanceid='devilry_nodeadmin',
#         appname='listnodes_index',
#         roleid=1))

urlpatterns = patterns(
    'devilry.devilry_nodeadmin',
    # url('^$', redirect_to_nodeadmin_frontpage_view, name='devilry_nodeadmin'),
    url(r'^', include(cradmin.NodeListingCrAdminInstance.urls())),
    # url('^$',
    #     login_required(csrf_protect(ensure_csrf_cookie(AppView.as_view()))),
    #         name='devilry_nodeadmin'),
    # url('^i18n.js$', javascript_catalog,
    #     kwargs={'packages': i18n_packages},
    #     name='devilry_nodeadmin_i18n'),
    # url('^rest/', include('devilry.devilry_nodeadmin.rest.urls')),
    # url('^node/(?P<id>\d+)',
    #     login_required(RedirectToNodeAdminAppView.as_view(pathformat='/node/{id}')),
    #     name='devilry_nodeadmin_node'),
)
