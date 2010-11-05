Targets
#######

  test
    Run tests with coverage.
  html-testreport
    Create a test coverage report. Depends on 'test'.


Developer help
##############

Typical workflow:

   1. Create initial example data with: (this take a while)::

        ---> ~$ make create-exampledb
        or
        ---> ~$ make create-exampledb NUM_STUDENTS=100 NUM_EXAMINERS=5
        or
        ---> ~$ make init-exampledb create-duck1080-data NUM_STUDENTS=40
        or
        ---> ~$ make init-exampledb
             ~$ adminscripts/create_testgroups.py somenode:duck20xx.hxx.someassignment [more arguments]
        or
        ---> other cobinations suiting the current development.

   2. Backup the data (since it takes a while to recreate)::

        ~$ make backup-exampledata

   3. Login as "grandma" to do admin stuff, "examiner0" to test as examiner and
      student0, student1, .... studentN to test as student (see Nodes).

   4. Restore the db from backup when needed with::

        ~$ make restore-exampledata

Why not just a static dataset?

   - Because we need to test stuff relative to current time.
   - Because adminscripts/create_testgroups.py can make relevant
     testdata when needed. Just run it with --help for more help.

Notes:

   - All users created by create_testgroups.py and all users in
     users.json uses "test" as password.
   - student1 will always be a good student, and the higher number a student
     has, the worst it is.
