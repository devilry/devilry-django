==================
Migrating to 6.5.0
==================

.. warning:: Always update one version at a time. Do not skip versions unless it is explicitly stated in the migration guide.


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########

- fix(settings): Remove USE_L10N and SHA1PasswordHasher as they are no longer in use
- feat(pyrproject): upgrade to django>=5.2.3,<5.3.0
- fix(settings): #1327 - added blockquote to the HTML_SANITIZERS.devilry used by markdown
- feat(devilry_dbcache): #1328 - New cache field public_student_attempts_with_delivered_files
- feat(devilry_admin): #1328 - New sheet Number of attempts
- fix(core): bulk_create_groups adds started_by to batch operation
- feat(core): #1303 - applicationstate readyness probe now checks rq redis connections for all rq queues and database healthcheck now also handle other exceptions which might occur as well
- feat(comment_email): #1323 include course name in comment email subjects and templates
- feat(examiner_feedback): #1287 update grade editing logic to redirect with warning message
- feat(qualification_preview): #1324 add CSV download functionality for qualified students
- feat(rq_handlers): add RQ timeout exception handler for better error reporting
- feat(tasks): implement simulate_timeout_task for testing timeout scenarios
- feat(settings): add comment for RQ exception handler configuration closes #1310
- fix(applicationstate): Update readiness check for Redis to handle sentinel
- fix(applicationstate): Correct import path for redis Sentinel.
- fix(applicationstate): Fix redis_cls error
- fix: Add a new error reporting system that can be overridden via settings.
- fix(compressionutil): Make the base action class for compression re-raise after catching exception.
- fix: Remove TracebackLoggingMiddleware from default MIDDLEWARE setup.

Update devilry
##############

Update the devilry version to ``6.5.0`` as described in :doc:`../update`.
