from django.conf.urls.defaults import *

urlpatterns = patterns('devilry.addons.grade_rstschema',
    url(r'^edit-schema/(?P<assignment_id>\d+)$', 'views.edit_schema',
        name='devilry-grade_rstschema-edit_schema'),
    url(r'^successful-save/(?P<assignment_id>\d+)$',
        'views.edit_schema',
        name='devilry-grade_rstschema-edit_schema-success',
        kwargs={'save_successful':True}),
    url(r'^subject-summary/(?P<subject_id>\d+)$',
        'views.subject_summary',
        name='devilry-grade_rstschema-subject_summary'),
    url(r'^preview_rstschemadef$', 'views.preview_rstschemadef',
        name='devilry-grade_rstschema-preview_rstschemadef')
)
