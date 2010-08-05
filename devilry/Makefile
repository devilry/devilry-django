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

reset-exampledb:
	rm -f db.sqlite3
	python manage.py syncdb --noinput
	python manage.py loaddata -v0 core/fixtures/example/users.json
	python manage.py loaddata -v0 core/fixtures/example/data.json
	python manage.py loaddata -v0 core/fixtures/example/grade_rstschema.json
	git checkout deliverystore.dbm.dat
	git checkout deliverystore.dbm.dir

selenium-test: cleardb
	python manage.py loaddata -v0 addons/student/fixtures/exampleusers.json
	python manage.py loaddata -v0 addons/student/fixtures/exampledata.json
	export DJANGO_SETTINGS_MODULE=devilry.settings
	python addons/student/seleniumtests.py

clean:
	coverage erase
