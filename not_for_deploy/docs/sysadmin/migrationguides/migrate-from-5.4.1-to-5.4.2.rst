=============================
Migrating from 5.4.1 to 5.4.2
=============================

Fixes
#####

- Delivery files: Fix bug where files are deleted from disc when a student is removed from an assignment, even 
    though they are "shared" in other groups (merged groups where content is copied). 
    The fix ensures that even though the reference to the filepath (CommentFile/CommentFileImage) is deleted, the actual file is not deleted until the 
    last reference is deleted.


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 5.4.2
#######################

Update the devilry version to ``5.4.2`` as described in :doc:`../update`.
