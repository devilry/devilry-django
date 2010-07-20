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

test: test-core

test-core:
	coverage -x manage.py test core

html-testreport: test
	coverage html

create-core-testdata:
	python manage.py dumpdata auth.user --indent=4 > core/fixtures/tests/core/users.json
	python manage.py dumpdata core.node --indent=4 > core/fixtures/tests/core/nodes.json
	python manage.py dumpdata core.subject --indent=4 > core/fixtures/tests/core/subjects.json
	python manage.py dumpdata core.period --indent=4 > core/fixtures/tests/core/periods.json
	python manage.py dumpdata core.assignment --indent=4 > core/fixtures/tests/core/assignments.json
	python manage.py dumpdata core.assignmentgroup --indent=4 > core/fixtures/tests/core/assignmentgroups.json
	python manage.py dumpdata core.candidate --indent=4 > core/fixtures/tests/core/candidates.json
	python manage.py dumpdata core.delivery --indent=4 > core/fixtures/tests/core/deliveries.json

cleardb:
	rm -f db.sqlite3
	python manage.py syncdb --noinput
	@echo
	@echo "Database is now clean."
	@echo "Use 'python manage.py loaddata' to load fixtures into the empty database. Example:"
	@echo
	@echo "   ~# python manage.py loaddata core/fixtures/tests/core/*"

create-exampledata:
	python manage.py dumpdata core --indent=4 > core/fixtures/exampledata.json
	python manage.py dumpdata auth.user --indent=4 > core/fixtures/exampleusers.json

reset-exampledb:
	rm -f db.sqlite3
	python manage.py syncdb --noinput
	python manage.py loaddata -v0 exampleusers
	python manage.py loaddata -v0 exampledata


clean:
	coverage erase

