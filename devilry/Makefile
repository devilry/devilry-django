test: test-core

test-core:
	coverage -x manage.py test core

html-testreport: test
	coverage html

create-testdata:
	python manage.py dumpdata auth.user --indent=4 > core/fixtures/testusers.json
	python manage.py dumpdata core.node --indent=4 > core/fixtures/testnodes.json
	python manage.py dumpdata core.subject --indent=4 > core/fixtures/testsubjects.json
	python manage.py dumpdata core.period --indent=4 > core/fixtures/testperiods.json
	python manage.py dumpdata core.assignment --indent=4 > core/fixtures/testassignments.json
	python manage.py dumpdata core.assignmentgroup --indent=4 > core/fixtures/testassignmentgroups.json
	python manage.py dumpdata core.candidate --indent=4 > core/fixtures/testcandidates.json

reset-testdb:
	rm -i db.sqlite3
	python manage.py syncdb --noinput
	python manage.py loaddata -v0 testusers
	python manage.py loaddata -v0 testnodes
	python manage.py loaddata -v0 testsubjects
	python manage.py loaddata -v0 testperiods
	python manage.py loaddata -v0 testassignments
	python manage.py loaddata -v0 testassignmentgroups
	python manage.py loaddata -v0 testcandidates

create-exampledata:
	python manage.py dumpdata core --indent=4 > core/fixtures/exampledata.json
	python manage.py dumpdata grade_schema --indent=4 > core/fixtures/exampledata_schema.json
	python manage.py dumpdata auth.user --indent=4 > core/fixtures/exampleusers.json

reset-exampledb:
	rm -i db.sqlite3
	python manage.py syncdb --noinput
	python manage.py loaddata -v0 exampleusers
	python manage.py loaddata -v0 exampledata
	python manage.py loaddata -v0 exampledata_schema

clean:
	coverage erase

