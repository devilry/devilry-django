from django.conf.urls import url

from views import submit_bulk_users

urlpatterns = [
    url(r'^add',
        submit_bulk_users.SubmitUsers.as_view(),
        name='bulkcreate_users_by_email'),

    url(r'^confirm',
        submit_bulk_users.ConfirmUsers.as_view(),
        name='confirm_bulkcreated_users'),

    url(r'^save/(?P<userdata>.*)',
        submit_bulk_users.SaveConfirmedUsers.as_view(),
        name='save_bulkcreated_users'),

    url(r'^show/(?P<created_users>.*)',
        submit_bulk_users.DisplayCreatedUsers.as_view(),
        name='display_bulkcreated_users'),
]
