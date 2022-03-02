===================================
Migrating from 5.4.0rc1 to 5.4.0rc2
===================================

You can also just update directly from `5.3.1`.

What's new
##########

This update contains improvements for accessibility:

- WCAG: Fix comment-editor keyboard-trap.
- WCAG: Improvements to the fileupload section of the editor.
- WCAG: Contextual description for screenreaders regarding the links for downloading assignment-files, with aria-live for when file-archive is finished building.
- WCAG: Adjusted contrast for various elements to comply with AA, such as the contextual colors for students, examiners and admins.
- WCAG: Fix some links not being interpreted as links.
- WCAG: Add label to empty (default) filter-values.
- WCAG: HTML-lang attribute uses the selected language.
- WCAG: Fileuploader has been updated for better accessibility.
- django-allauth: Update to version 0.48, and signup is not supported, so this is bypassed (automatic redirect to proxy-view introduced in 0.47).
- Comment-editor: Replaced Ace-editor with custom editor to ensure more flexibility in regards to accessibility and future features.
- Comment-editor: Support preview of Markdown.
- Comment-editor: Overview page of supported Markdown.
- Various text-fixes and translations.
- Admin: Add warning when groups with multiple examiners exist in examiner statistics view.


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 5.4.0rc2
##########################

Update the devilry version to ``5.4.0rc2`` as described in :doc:`../update`.
