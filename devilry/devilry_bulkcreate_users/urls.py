from django.urls import path, re_path

from .views import submit_bulk_users

urlpatterns = [
    path('add',
        submit_bulk_users.SubmitUsers.as_view(),
        name='bulkcreate_users_by_email'),
    path('confirm',
        submit_bulk_users.ConfirmUsers.as_view(),
        name='confirm_bulkcreated_users'),
    re_path(r'^save/(?P<userdata>.*)',
        submit_bulk_users.SaveConfirmedUsers.as_view(),
        name='save_bulkcreated_users'),
    re_path(r'^show/(?P<created_users>.*)',
        submit_bulk_users.DisplayCreatedUsers.as_view(),
        name='display_bulkcreated_users'),
]
