PRODTEST=devilry.cfg.test2
PROD=devilry.cfg.prod1

USER=../adminscripts/bin/devilry-user.py


help:
	@echo "Targets:"
	@echo "  test:                 Run tests with coverage."
	@echo "  html-testreport       Create a test coverage report. Depends on 'test'."
	@echo "  create-exampledata    Create example fixtures from db.sqlite3."
	@echo "  reset-exampledb       Reset db.sqlite3 from the example fixtures."
	@echo "  create-core-testdata  Create test fixtures for core from db.sqlite3."
	@echo "  cleardb               Clear the database."
	@echo ""
	@echo "EXAMPLE DATA AND TEST DATA"
	@echo "Test data is for the testcases, and must not be changed without careful "
	@echo "consideration. 'Example' data is used when working with UI-design or"
	@echo "just to show of Devilry, and it can be changed and extended without"
	@echo "affecting anything."

test:
	coverage -x manage.py test

html-testreport: test
	coverage html

cleardb:
	rm -f db.sqlite3
	python manage.py syncdb --noinput
	@echo
	@echo "Database is now clean."
	@echo "Use 'python manage.py loaddata' to load fixtures into the empty database. Example:"
	@echo
	@echo "   ~# python manage.py loaddata core/fixtures/tests/core/*.json"

create-exampledata:
	python manage.py dumpdata core --indent=4 > core/fixtures/example/data.json
	python manage.py dumpdata auth.user --indent=4 > core/fixtures/example/users.json
	python manage.py dumpdata grade_rstschema --indent=4 > core/fixtures/example/grade_rstschema.json
	python manage.py dumpdata grade_default --indent=4 > core/fixtures/example/grade_default.json
	python manage.py dumpdata grade_approved --indent=4 > core/fixtures/example/grade_approved.json

reset-exampledb:
	rm -f db.sqlite3
	python manage.py syncdb --noinput
	python manage.py loaddata -v0 core/fixtures/example/users.json
	python manage.py loaddata -v0 core/fixtures/example/data.json
	python manage.py loaddata -v0 core/fixtures/example/grade_rstschema.json
	python manage.py loaddata -v0 core/fixtures/example/grade_default.json
	python manage.py loaddata -v0 core/fixtures/example/grade_approved.json
	git checkout deliverystore.dbm.dat
	git checkout deliverystore.dbm.dir
	chmod a+rw db.sqlite3

reset-proddb:
	rm -f prod.db.sqlite3
	python manage.py syncdb --settings=${PROD} --noinput
	#DJANGO_SETTINGS_MODULE=${PROD} ${USER} add espeak --superuser yes --first-name "Espen" --last-name "Kristiansen"
	#DJANGO_SETTINGS_MODULE=${PROD} ${USER} add bendiko --superuser yes --first-name "Bendik" --last-name "Opstad"
	#DJANGO_SETTINGS_MODULE=${PROD} ${USER} add fredva --first-name "Fredrik" --last-name "Valdemais"
	chmod a+rw prod.db.sqlite3


clear-prodtestdb:
	-psql -d devilry_test -c "DROP TABLE auth_permission CASCADE;";
	-psql -d devilry_test -c "DROP TABLE auth_group_permissions CASCADE;";
	-psql -d devilry_test -c "DROP TABLE auth_group CASCADE;";
	-psql -d devilry_test -c "DROP TABLE auth_user_user_permissions CASCADE;";
	-psql -d devilry_test -c "DROP TABLE auth_user_groups CASCADE;";
	-psql -d devilry_test -c "DROP TABLE auth_user CASCADE;";
	-psql -d devilry_test -c "DROP TABLE auth_message CASCADE;";
	-psql -d devilry_test -c "DROP TABLE django_content_type CASCADE;";
	-psql -d devilry_test -c "DROP TABLE django_session CASCADE;";
	-psql -d devilry_test -c "DROP TABLE django_site CASCADE;";
	-psql -d devilry_test -c "DROP TABLE django_admin_log CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_grademodel CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_node_admins CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_node CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_subject_admins CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_subject CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_period_admins CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_period CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_assignment_admins CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_assignment CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_candidate CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_assignmentgroup_examiners CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_assignmentgroup CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_deadline CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_delivery CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_feedback CASCADE;";
	-psql -d devilry_test -c "DROP TABLE core_filemeta CASCADE;";
	-psql -d devilry_test -c "DROP TABLE grade_approved_approvedgrade CASCADE;";
	-psql -d devilry_test -c "DROP TABLE grade_default_charfieldgrade CASCADE;";
	-psql -d devilry_test -c "DROP TABLE grade_schema_schemagrade CASCADE;";
	-psql -d devilry_test -c "DROP TABLE grade_schema_entry CASCADE;";
	-psql -d devilry_test -c "DROP TABLE grade_schema_schemagraderesults CASCADE;";
	-psql -d devilry_test -c "DROP TABLE grade_schema_result CASCADE;";
	-psql -d devilry_test -c "DROP TABLE grade_rstschema_rstschemadefinition CASCADE;";
	-psql -d devilry_test -c "DROP TABLE grade_rstschema_rstschemagrade CASCADE;";

init-prodtestdb:
	python manage.py syncdb --settings=${PRODTEST} --noinput
	python manage.py loaddata --settings=${PRODTEST} -v0 core/fixtures/example/users.json
	python manage.py loaddata --settings=${PRODTEST} -v0 core/fixtures/example/data.json
	python manage.py loaddata --settings=${PRODTEST} -v0 core/fixtures/example/grade_rstschema.json
	python manage.py loaddata --settings=${PRODTEST} -v0 core/fixtures/example/grade_default.json
	python manage.py loaddata --settings=${PRODTEST} -v0 core/fixtures/example/grade_approved.json

reset-prodtest: clear-prodtestdb init-prodtestdb

selenium-test: cleardb
	python manage.py loaddata -v0 addons/student/fixtures/exampleusers.json
	python manage.py loaddata -v0 addons/student/fixtures/exampledata.json
	export DJANGO_SETTINGS_MODULE=devilry.settings
	python addons/student/seleniumtests.py

clean:
	coverage erase
