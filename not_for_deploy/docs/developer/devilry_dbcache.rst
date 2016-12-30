==========================================================
:mod:`devilry.devilry_dbcache` --- Data caching with PGSQL
==========================================================

This app provides database caching for assignment groups.


How to debug with logging
######################################
Enable logging by editing `dbdev_tempdata/PostgresBackend/postgresql.conf`
and uncomment the lines to look like this::

 log_destination = 'stderr'
 logging_collector = on
 log_directory = 'pg_log'
 log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
 client_min_messages = notice
 log_min_messages = notice

In the PGSQL code insert print statements::

    RAISE NOTICE 'SKROT';
    RAISE NOTICE 'Some value: %', name_of_variable;

View output::

 tail -f dbdev_tempdata/PostgresBackend/pg_log/postgresql-2016-08-06_223959.log
