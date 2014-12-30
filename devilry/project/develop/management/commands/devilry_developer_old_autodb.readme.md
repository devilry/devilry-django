# About the demo database

## Locale/language
For now, we have only activated the default devilry locale. This uses the following _terminology_:

- **Subject**: A university will typically call this a Course.
- **Period**: A period in time, with a start and an end. At a university, this will typically be a semester.


## Subjects
We define two subjects:

### duck1010
A fairly traditional university-style subject with 3 obligatory assignments,
with approved/not approved grading. ``thor`` is admin on the subject.

### duck1100
A subject with weekly deliveries where students are graded using points.
``thor`` is admin on the ``springcur``-period.

### duck4000
A subject with a single period and a single assignment. ``thor`` is admin on the assignment.

### duck4000
A subject with a single period. ``thor`` is admin on the period.


## Periods
The periods are generated relative to the time when the demo-database was
generated. This makes is hard to give them common names like _spring 2012_, so
we simply call them _cur_ (currently active), _old_ (expired), and veryold (even older
than old).


## Users

### A user with most roles
For a user that is student, examiner and admin, login as ``thor``.

### Superuser
For a superuser, login as ``grandma``.

### Administrators
For a node admin, login as ``duckburghadmin`` or ``ifiadmin``.

### Students
We define 3 types of students, _bad_, _medium_ and _good_. These are defined in
variables at the top of [dev_autodb.py](dev_autodb.py)

- For bad student, login as ``johnsmith``.
- For a medium student, login as ``dewey``.
- For a good student, login as ``odin``.

### Examiners
``scrooge`` and ``donald`` are examiners. ``donald`` has all the good students,
and half the bad students, while ``scrooge`` has all the ``medium`` students,
and the other half of the bad students.
