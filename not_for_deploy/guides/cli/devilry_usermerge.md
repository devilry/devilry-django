# devilry_usermerge

Used to merge two users.

## The current solution does the following:

- Merges RelatedStudent with subobjects (Candidate and QualifiedForFinalExam). If both the source and target users has a RelatedStudent on the same Period, we do a merge where all sub objects are moved to the target user, and the source users RelatedStudent is removed. If only the source user has a RelatedStudent on a period, we just move their User foreign key.
- Merges RelatedExaminer with subobjects (Examiner objects). Same strategy as with RelatedStudent.
- Merges PermissionGroupUser objects (just moved User foreign keys). This handles merging subject/period permissions.
- Merges Comment objects, BUT we leave CommentEditHistory alone. We just move the User foreignkey on the Comment objects from source user to target user.
- Merges FeedbackSet objects. I.e.: We move the ``grading_published_by``, ``created_by`` and ``last_updated_by`` foreign keys from source user to target user.

### We DO NOT HANDLE these things:
- A lot of meta-info fields like created_by on Assignment, Period, Subject, etc.
- Collisions with QualifiedForFinalExam. The same user can not be part of the same Status in the qualified for final exam system. So in the very strange case where we need to merge two users that both have qualified for final exam statuses for the same Period, it will crash. This is not something we can handle automatically (we can not determine which grade is the correct one safely), and that means that it must be fixed manually before merging. The crash will lead to a full revert (we do everything in a transaction), so there will not be a partial merge caused by this crash.
- Merging AssignmentGroups that are left when the two merged users was already in their own AssignmentGroup on the same assignment. This is to complex to handle automatically safely. The most likely case is that the both of the users are already registered in an AssignmentGroup on the same assignment, but they person behind both user accounts have only "used" one of their user accounts, so the other AssignmentGroup have no comments/deliveries etc. In that case, it will just be messy to merge the groups, and deleting them would be better. In other cases, they may be in groups with multiple students, and merging is risky. In any case: We support both deleting and merging AssignmentGroups in the UI, so this is something that can be handled by the course administration after the merge when needed. It will look a bit strange from the students perspective since they will get the same assignment twice in their list of assignments. We would recommend that standard practice is to inform the course administration on any active courses and the student themselves after the merge, and get them to clean this up as they see fit.


## Usage

```
$ python manage.py devilry_usermerge --source-user "<from-username>" --target-user "<into-username>"
```

If you add ``--verbose``, you will get the full JSON summary of the merge. After running a merge, you can
view the merge in the ``Merged users`` section of the superuser UI (django admin). If you forgot to use ``--verbose``,
you can always view that information in the superuser UI later in the _Summary json_ field.
