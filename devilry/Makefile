PRODTEST=devilry.cfg.test2
PROD=devilry.cfg.prod1
EXAMPLEDATA_BACKUP=exampledata-backup
NUM_STUDENTS=30
NUM_EXAMINERS=2

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
	python manage.py dumpdata auth.user --indent=4 > core/fixtures/example/users.json
	python manage.py dumpdata core --indent=4 > core/fixtures/example/data.json
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

create-duck1100-data:
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.week1 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "-30" --grade-maxpoints 14
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.week2 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "-20" --grade-maxpoints 10
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.week3 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "old" --grade-maxpoints 9
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.week4 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "recent" --grade-maxpoints 12
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.week5 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "soon" --grade-maxpoints 6

create-duck1080-data:
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1080.h01.week1 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "-30" --grade-maxpoints 11 \
		--pointscale 10
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1080.h01.week2 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "-20" --grade-maxpoints 9 \
		--pointscale 10
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1080.h01.week3 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "recent" --grade-maxpoints 8 \
		--pointscale 10
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1080.h01.week4 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "soon" --grade-maxpoints 14 \
		--pointscale 10


create-exampledb: create-duck1100-data


init-exampledb: cleardb
	python manage.py loaddata -v0 core/fixtures/example/users.json

backup-exampledb:
	rm -rf $(EXAMPLEDATA_BACKUP)
	rm -f $(EXAMPLEDATA_BACKUP).tar.bz2
	mkdir $(EXAMPLEDATA_BACKUP)
	sqlite3 db.sqlite3 .dump > $(EXAMPLEDATA_BACKUP)/dbdump.sql
	cp deliverystore.dbm.dat $(EXAMPLEDATA_BACKUP)/
	cp deliverystore.dbm.dir $(EXAMPLEDATA_BACKUP)/
	tar -cvjf $(EXAMPLEDATA_BACKUP).tar.bz2 $(EXAMPLEDATA_BACKUP)
	rm -rf $(EXAMPLEDATA_BACKUP)

restore-exampledb:
	rm -f db.sqlite3
	tar -xvjf $(EXAMPLEDATA_BACKUP).tar.bz2
	cp $(EXAMPLEDATA_BACKUP)/deliverystore.dbm.dat ./
	cp $(EXAMPLEDATA_BACKUP)/deliverystore.dbm.dir ./
	sqlite3 db.sqlite3 < $(EXAMPLEDATA_BACKUP)/dbdump.sql
	rm -rf $(EXAMPLEDATA_BACKUP)

create-minimal-exampledata:
	python manage.py dumpdata core --indent=4 > core/fixtures/example/minimaldata.json
	python manage.py dumpdata auth.user --indent=4 > core/fixtures/example/minimalusers.json

reset-minimal-exampledb:
	rm -f db.sqlite3
	python manage.py syncdb --noinput
	python manage.py loaddata -v0 core/fixtures/example/minimalusers.json
	python manage.py loaddata -v0 core/fixtures/example/minimaldata.json
	git checkout deliverystore.dbm.dat
	git checkout deliverystore.dbm.dir
	chmod a+rw db.sqlite3



selenium-clear-db: cleardb
	git checkout deliverystore.dbm.dat
	git checkout deliverystore.dbm.dir

selenium-student-test: selenium-clear-db
	python manage.py loaddata -v0 addons/student/fixtures/selenium/student/*.json
	sleep 2
	export DJANGO_SETTINGS_MODULE=devilry.settings
	python addons/student/seleniumtests.py

selenium-examiner-test:
	export DJANGO_SETTINGS_MODULE=devilry.settings
	python addons/examiner/seleniumtests.py

selenium-admin-test: selenium-clear-db
	python manage.py loaddata -v0 addons/admin/fixtures/selenium.json
	sleep 2
	export DJANGO_SETTINGS_MODULE=devilry.settings
	python addons/admin/seleniumtests.py

selenium-tests: selenium-student-test selenium-examiner-test selenium-admin-test

clean:
	coverage erase
