============================================
Migrating from 5.3.1 to 5.4.0 (NOT RELEASED)
============================================

What's new
##########

This update mainly contains WCAG-improvements.

- WCAG: Fix comment-editor keyboard-trap.
- WCAG: Improvements to the fileupload section of the editor.
- WCAG: Contextual description for screenreaders regarding the links for downloading assignment-files, with aria-live for when file-archive is finished building.
- WCAG: Adjusted contrast for various elements to comply with AA, such as the contextual colors for students, examiners and admins.
- WCAG: Fix some links not being interpreted as links.
- WCAG: Add label to empty (default) filter-values.
- WCAG: HTML-lang attribute uses the selected language.
- django-allauth: Update to version 0.47, and bypass newly added signup-page default.


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 5.4.0
#######################

Update the devilry version to ``5.4.0`` as described in :doc:`../update`.
