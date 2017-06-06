from django.conf.urls import include, url

from devilry.devilry_account import crinstance_account

urlpatterns = [
    url(r'^', include(crinstance_account.CrAdminInstance.urls()))
]
