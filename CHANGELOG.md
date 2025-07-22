## 6.5.0a2 (2025-07-22)

### Fix

- **applicationstate**: Correct import path for redis Sentinel.

## 6.5.0a1 (2025-07-22)

### Fix

- **applicationstate**: Update readiness check for Redis to handle sentinel

## 6.5.0a0 (2025-07-22)

### Feat

- **migration_guides**: add migration guide for upgrading from 6.4.0 to 6.5.0 feat(changelog): add changelog for Devilry 6.5.0 with new features and fixes
- **locale**: update translations
- **rq_handlers**: add RQ timeout exception handler for better error reporting feat(tasks): implement simulate_timeout_task for testing timeout scenarios feat(settings): add comment for RQ exception handler configuration closes #1310
- **qualification_preview**: #1324 add CSV download functionality for qualified students
- **examiner_feedback**: #1287 update grade editing logic to redirect with warning message
- **comment_email**: #1323 include course name in comment email subjects and templates
- **core**: #1303 - applicationstate readyness probe now checks rq redis connections for all rq queues and database healthcheck now also handle other exceptions which might occur as well
- **devilry_dbcache**: #1328 - New cache field public_student_attempts_with_delivered_files feat(devilry_admin): #1328 - New sheet Number of attempts
- **pyrproject**: upgrade to django>=5.2.3,<5.3.0
- **docker-compose**: update minio to work on postgres 16
- **tests_datetime_format**: Use format module path for test settings

### Fix

- **core**: bulk_create_groups adds started_by to batch operation
- **settings**: #1327 - added blockquote to the HTML_SANITIZERS.devilry used by markdown
- **test_dashboard.py**: update num queries
- **settings**: Remove USE_L10N and SHA1PasswordHasher as they are no longer in use
- **tests**: Remove USE_L10N as it no longer in use.

## 6.4.0 (2025-04-11)

## 6.4.0rc5 (2025-04-10)

### Fix

- Update attempt number assertions in student item value tests
- Correct attempt number calculation for Norwegian ordinal formatting

## 6.4.0rc4 (2025-04-09)

### Fix

- Update attempt number formatting to use ordinal representation
- Simplify attempt number formatting for Norwegian and English languages #1305
- Enhance attempt number formatting with Norwegian ordinals and English support #1305

## 6.4.0rc3 (2025-04-07)

### Fix

- Correct dependencies broken by 6.4 branch merge.

## 6.4.0rc2 (2025-04-01)

### Fix

- **command**: Empty commit to proceed 6.4.0rc2

## 6.4.0rc1 (2025-04-01)

### Fix

- **deadline_management**: Refactor __give_new_attempt method to simplify feedback set creation and improve variable naming
- **devilry_dbcache**: Simplify attempt number formatting and support Norwegian translations
- **devilry_dbcache**: Update admin display to use readonly_fields and adjust list_display for AssignmentGroupCachedData
- Enhance attempt number formatting to support Norwegian ordinals based on session language
- **devilry_group**: Raise exception when feedbackset compress action fails to execute.
- Add redirect view for the email notification URL sent when students add a comment (sent to examiners/admins)
- Add system messages support just like the other "branding" templating.
- Add content-disposition for file downloads.
- **devilry.devilry_cradmin.devilry_listfilter.lists**: created DevilryVertical listfilter list that useses the custom FiltersHandler DevilryFiltersHandler
- **AssignmentBatchMixin**: changed feedback_set_path to correct formating
- **AssignmentGroupCacheData**: fixed weird 4st try problem
- **nb/LC_MESSAGES/django.po**: fixed 4st error
- **ManageDeadlineView**: added missing __create_groupcomment to __give_new_attempt
- **devilry_account.crapps.account.utils**: small fix to make codebase compatible with pycountry > 17
- **develop-settings**: moved out model bakery class to own file
- **devilry_deadlinemanagement.views.manage_deadline_view.ManageDeadlineView**: changed __give_new_attempt to update deadline if there is no published feedback in feedbackset instead of always creating a new feedbackset
- **devilry_dbcache.customsql_sqlcode.groupcomment.triggers**: added ON CONFLICT clause to on_group_comment_text_update
- **StreamZipBackend**: removed specified file mode from opening files when creating zip
- **devilry_dataporten_allauth.views**: fixed imports
- **GroupCommentDeleteView**: moved custom delete logic from delete to form_valid
- **devilry_group/views/examiner/feedbackfeed_examiner.py**: change from 404 to redirect when last_feedback has been published

## 6.3.8 (2024-10-14)

### Fix

- Use local version of Fira Sans instead of googlefonts.

## 6.3.7 (2024-09-30)

### Fix

- Make it possible to configure separate storage backend for single file download URLs.
- Make it possible to configure separate storage backend for archive download URLs.

## 6.3.6 (2024-09-10)

### Fix

- Add setting to optionally disable CSRF for certain API views.

## 6.3.5 (2024-08-20)

### Fix

- Support downloading archives via S3 presigned URL

## 6.3.4 (2024-08-20)

### Fix

- **compressionutil**: Add logging to file downloads (loglevel DEBUG, no not visible by default)

## 6.3.3 (2024-06-29)

### Fix

- **dataporten_allauth**: Fix get_client call.
- Remove .zip from archive download filenames for admins and examiners.

## 6.3.2 (2024-06-25)

### Feat

- **archive_download_message.django.html**: added an informational message about the use of tar.gz files

### Fix

- psycopg3 update for RawSQL query
- Show configurable message when archive download is complete.
- Change zip backend to TAR format. Because of issues with S3 and zipfile.
- More S3 tuning, including docs.
- **compressionutil**: Make zip file creation work with S3 storage.
- Move whitenoise into hard dependencies since we have it in MIDDLEWARE.
- **settings.py**: fix to allow migrations from allauth to run
- **devilry_dataporten_allauth.views**: fixed imports
- Further dependency and releasenotes cleanup
- Replace dj-static with whitenoise.
- Remove old unused delivery and gradingsystem models.
- Make storage for all the models.FileField fields configurabe via settings.
- Update cradmin_legacy to 5.0.1,<6.0.0
- Change ZIP backend so it uses storage (which can be blob storage) instead of streaming.

## 6.3.1 (2024-04-19)

### Fix

- **comment_email.py**: fixed send_student_comment_email getting unexpected keyword argument

## 6.3.0 (2024-04-12)

## 6.3.0rc7 (2024-04-12)

### Fix

- **DevilrySocialAccountAdapter**: added 'profilephoto' to extra_data_to_keep

## 6.3.0rc6 (2024-04-12)

### Fix

- **FileDownloadFeedbackfeedView**: change groupcomment visibility check to a more comprehensive check

## 6.3.0rc5 (2024-04-11)

### Fix

- **download_archive.py**: Change from StreamingHttpResponse to FileResponse

## 6.3.0rc4 (2024-04-11)

### Fix

- **backend_base.py**: fixed not closing filedescriptors

## 6.3.0rc3 (2024-04-03)

### Fix

- **StudentFeedbackFeedView**: changed from self.model.... to self.assignment_group.... in before_original_deadline check
- **devilry_compressionutil**: added if check for save_to_disk if DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY should be used

## 6.3.0rc2 (2024-04-02)

### Perf

- **devilry_compressionutil**: optimization of gathering of files of feedbacksets and assignments for zip generation

## 6.3.0rc1 (2024-03-12)

### Fix

- **StreamZipBackend**: Added missing if test to _create_path_if_not_exists

## 6.3.0rc0 (2024-03-11)

### Feat

- **devilry_compressionutil**: added the ability to stream the creation of zip files

### Fix

- **comment_email.py**: added check for if comment is empty and made before first deadline of assignment then it should not send email to examiner
- **allauth_adapter.py**: removed logging of value, only logs key
- **allauth_adapter.py**: added removal of unwanted extra_data
- **qualification_preview_view.py**: re-labeled print buttons and removed order by candidate number

## 6.2.4 (2024-02-15)

### Fix

- Added settings to allow spans to have class attribute and to not merge spans when sanitizing input

## 6.2.3 (2024-02-14)

### Fix

- for #1281

## 6.2.2 (2024-02-05)

### Fix

- Set connecting argument when saving in allauth_adapter.

## 6.2.1 (2023-12-05)

### Fix

- **devilry_qualifiesforexam.QualificationPreviewView**: fixed KeyError causing saving to fail

## 6.2.0 (2023-12-04)

## 6.2.0rc3 (2023-12-04)

### Fix

- **devilry_examiner.assignmentgroup**: fixed duplicate filters in OrderByDelivery

## 6.2.0rc2 (2023-12-04)

### Fix

- **devilry_examiner.selfassign.py**: fixed added sorting to wrong view

## 6.2.0rc1 (2023-12-01)

### Fix

- **devilry_examiner.assignment**: Added missing sorting on delivery time
- **feedbackfeed_examiner.py**: fixed defaulting to feedback

## 6.2.0rc0 (2023-11-29)

### Feat

- **devilry_qualifiesforexam**: added listing of required exams on status report
- **devilry_examiner**: added sorting by delivery time and filter if assignment has an delivery with file attachment to examiner dashboard
- **devilry-comment-editor**: added button for image markdown

### Fix

- **settings/develop.py**: Added mediacopy of files missing to work with whitenoise
- **feedbackfeed_examiner.ExaminerPublicDiscussView**: set feedback to default open tab instead of discuss
- **devilry_admin.asignment.student.overwiev**: changed to 'students' to 'groups' to better reflect actual content of view
- **devilry_listfilter.user.Search**: force encoding of search input to hopefully fix #1077
- **devilry_markup**: added sanitizer step after markdown conversion

## 6.1.1 (2023-11-02)

### Fix

- **DevilryOAuth2CallbackView**: get_app() to .app

## 6.1.0 (2023-11-01)

### Fix

- **Translation**: added missing translations
- **PrintStatusView**: hide footer when printing
- **pyproject.toml**: removed certifi requirement

## 6.1.0rc0 (2023-10-31)

### Feat

- **PrintStatusView**: propper sorting and more data displayed

### Fix

- **pyproject.toml**: upped the version of gunicorn to 21
- **devilry_authenticate**: changed allauthloginview to support allauth version > 0.55

## 6.0.1 (2023-10-26)

### Fix

- **AssignmentGradingConfigurationUpdateView**: corrected changing grading for assignments

## 6.0.0 (2023-07-21)

### BREAKING CHANGE

- This will be a major release

### Feat

- Django 4.2 and python 3.10 support     - Add health-check endpoints.     - Group invitations: Now using the devilry_message backend for storing messages.     - WCAG: Contrast-issue with link in "No access" warning-box.     - Translations: Various translation errors.     - Self-assign: Issue with duplicate rows from query when examiner is self-assigning.     - Self-assign: Missing CSRF-token.     - Comment-notification to examiners: When examiner posts comments all admins are notified.

## 6.0.0rc2 (2023-07-20)

### Feat

- Add endpoints readiness and liveness probing

### Fix

- Use CSRF-middleware to ensure CSRF-cookie is set everywhere
- If user is admin and examiner, the user should receive a notification as examiner if they post a comment as an admin.
- E-mail sent to admins when comment-poster was the only examiner in the group
- Group invite - email translations
- Group invite - use devilry_message system
- Use distinct to filter out duplicate rows from AssignmentGroup-query
- translation errors
- Contrast level adjustment for "danger"-box anchor-tag
- Update sphinx and related packages
- readthedocs testing
- **.readthedocs.yml**: Python version 3.8
- **.readthedocs.yml**: Python version 3.10
- Add pip-tools

## 6.0.0rc1 (2023-05-31)

### BREAKING CHANGE

- Django 4.2 support

## 5.5.3 (2022-12-06)

## 5.5.2 (2022-09-20)

## 5.5.1 (2022-06-14)

## 5.5.0 (2022-06-07)

## 5.4.2 (2022-04-21)

## 5.4.1 (2022-03-11)

## 5.4.0 (2022-03-09)

## 5.4.0rc4 (2022-03-03)

## 5.4.0rc3 (2022-03-03)

## 5.4.0rc2 (2022-03-02)

## 5.4.0rc1 (2022-03-02)

## 5.3.1 (2021-09-07)

## 5.3.0 (2021-09-07)

## 5.2.0 (2021-09-03)

## 5.2.0rc2 (2021-09-02)

## 5.2.0rc1 (2021-08-31)

## 5.1.0 (2021-04-30)

## 5.1.0rc4 (2021-04-29)

## 5.1.0rc3 (2021-04-28)

## 5.1.0rc2 (2021-04-27)

## 5.1.0rc1 (2021-04-23)

## 5.0.1 (2021-03-16)

## 5.0.0 (2020-09-25)

## 5.0.0rc1 (2020-09-09)

## 4.0.3 (2019-11-07)

## 5.0.0b2 (2019-07-24)

## 4.0.2 (2019-07-24)

## 5.0.0b1 (2019-06-24)

## 4.0.1 (2019-06-03)

## 4.0.0 (2019-04-23)

## 4.0.0b2 (2019-03-14)

## 4.0.0b1 (2019-03-12)

## 3.7.3 (2019-02-15)

## 3.7.2 (2019-02-11)

## 3.7.1 (2019-01-30)

## 3.7.0 (2019-01-30)

## 3.7.0b1 (2019-01-22)

## 3.6.0 (2019-01-09)

## 3.6.0b1 (2019-01-03)

## 3.5.2 (2018-11-28)

## 3.5.1 (2018-11-23)

## 3.5.0 (2018-11-22)

## 3.4.6 (2018-11-07)

## 3.4.5 (2018-10-30)

## 3.4.4 (2018-10-23)

## 3.4.3 (2018-10-18)

## 3.4.2 (2018-10-18)

## 3.4.1 (2018-10-11)

## 3.4.0 (2018-10-02)

## 3.3.3 (2018-09-25)

## 3.3.2 (2018-09-25)

## 3.3.1 (2018-09-11)

## 3.3.0 (2018-09-06)

## 3.3.0b11 (2018-09-06)

## 3.3.0b10 (2018-08-31)

## 3.3.0b9 (2018-08-28)

## 3.3.0b8 (2018-08-22)

## 3.3.0b7 (2018-08-17)

## 3.3.0b6 (2018-08-15)

## 3.3.0b5 (2018-08-09)

## 3.3.0b4 (2018-08-08)

## 3.3.0b3 (2018-08-07)

## 3.3.0b2 (2018-08-03)

## 3.3.0b1 (2018-07-26)

## 3.1.6 (2018-03-02)

## 3.1.5 (2018-03-01)

## 3.1.4 (2018-02-22)

## 3.1.3 (2018-02-20)

## 3.1.2 (2018-02-19)

## 3.1.1 (2018-02-19)

## 3.1.0 (2018-02-15)

## 3.0.3 (2018-01-31)

## 3.0.2 (2018-01-31)

## 3.0.1 (2018-01-29)

## 3.0.0 (2018-01-19)

## 3.0.0a25 (2017-07-02)

## 3.0.0a24 (2017-07-01)

## 3.0.0a23 (2017-06-30)

## 3.0.0a22 (2017-06-30)

## 3.0.0a8 (2017-06-14)

## 3.0.0a7 (2017-06-14)

## 3.0.0a5 (2017-06-14)

## 3.0.0a4 (2017-06-14)

## 3.0.0a3 (2017-06-13)

## 3.0.0a2 (2017-03-08)

## 2.1.0-beta.016 (2015-06-04)

## 2.1.0-beta.014 (2015-06-03)

## 2.1.0-beta.013 (2015-06-02)

## 2.1.0-beta.012 (2015-06-01)

## 2.1.0-beta.011 (2015-06-01)

## release-2.1.0-beta.010 (2015-06-01)

## release-2.1.0-beta.009 (2015-05-31)

## release-2.1.0-beta.008 (2015-05-31)

## release-2.1.0-beta.007 (2015-05-31)

## release-2.1.0-beta.006 (2015-05-31)

## release-2.1.0-beta.005 (2015-05-31)

## release-2.1.0-beta.003 (2015-05-31)

## release-2.1.0-beta.002 (2015-05-31)

## release-2.1.0-beta.001 (2015-05-30)

## 2.0.0 (2015-02-25)

## 2.0.0-rc.004 (2015-02-25)

## 2.0.0-rc.003 (2015-02-19)

## 2.0.0-rc.002 (2015-02-11)

## 2.0.0-rc.001 (2015-02-11)

## v1.4.14 (2014-12-09)

## v1.4.13 (2014-12-07)

## v1.4.12 (2014-11-17)

## v1.4.11 (2014-11-12)

## v1.4.10 (2014-11-11)

## v1.4.9 (2014-10-28)

## v1.4.8 (2014-04-10)

## v1.4.7 (2014-03-26)

## v1.4.6 (2014-03-03)

## v1.4.5 (2014-02-16)

## v1.4.4.2 (2014-02-03)

## v1.4.4.1 (2014-01-30)

## v1.4.4 (2014-01-29)

## v1.4.3 (2014-01-27)

## v1.4.2 (2014-01-24)

## v1.4.1 (2014-01-20)

## v1.4.0 (2014-01-20)

## v1.3.6 (2013-11-13)

## v1.3.5 (2013-11-07)

## v1.3.4 (2013-10-14)

## v1.3.3 (2013-10-14)

## v1.3.2 (2013-10-10)

## v1.3.1 (2013-09-12)

## v1.3.1-beta2 (2013-09-12)

## v1.3.1-beta (2013-09-12)

## v1.3 (2013-08-12)

## v1.3-beta1 (2013-08-12)

## v1.2.1.10 (2013-05-22)

## v1.2.1.9 (2013-05-16)

## v1.2.1.8 (2013-05-06)

## v1.2.1.7 (2013-05-04)

## v1.2.1.6 (2013-03-07)

## v1.2.1.5 (2013-03-03)

## v1.2.1.4 (2013-02-12)

## v1.2.1.3 (2013-02-06)

## v1.2.1.2 (2013-01-31)

## v1.2.1.1 (2013-01-31)

## v1.2.1 (2013-01-18)

## v1.2.1rc2 (2013-01-17)

## v1.2.1rc1 (2013-01-17)

## v1.1rc4 (2012-08-30)

## v1.1rc3 (2012-08-28)

## v1.1rc2 (2012-08-28)

## v1.1rc1 (2012-08-27)

## v1.1b1 (2012-08-25)

## v1.1a3 (2012-08-20)

## v1.1a2 (2012-08-20)

## v1.1a1 (2012-08-19)

## before_subjectadminmerge (2012-07-24)

## v1.0.1 (2012-08-19)

## v1.0 (2011-12-01)

## v0.1.5 (2011-02-26)

## v0.1.4 (2011-02-21)

## v0.1.3 (2011-02-11)

## v0.1.2 (2010-11-10)

## v0.1.1 (2010-11-10)

## v0.1.0 (2010-09-05)
