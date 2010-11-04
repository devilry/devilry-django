PRODTEST=devilry.cfg.test2
PROD=devilry.cfg.prod1
EXAMPLEDATA_BACKUP=exampledata-backup

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
	#python manage.py loaddata -v0 core/fixtures/example/data.json
	#python manage.py loaddata -v0 core/fixtures/example/grade_rstschema.json
	#python manage.py loaddata -v0 core/fixtures/example/grade_default.json
	#python manage.py loaddata -v0 core/fixtures/example/grade_approved.json

	#git checkout deliverystore.dbm.dat
	#git checkout deliverystore.dbm.dir
	chmod a+rw db.sqlite3

create_duck1100_data:
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.hxx.week1 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students 300 \
		--deadline-profile "-70" --grade-maxpoints 10
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.hxx.week2 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students 300 \
		--deadline-profile "-60" --grade-maxpoints 12
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.hxx.week3 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students 300 \
		--deadline-profile "-50" --grade-maxpoints 8
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.hxx.week4 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students 300 \
		--deadline-profile "-40" --grade-maxpoints 7
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.hxx.week5 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students 300 \
		--deadline-profile "-30" --grade-maxpoints 14
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.hxx.week6 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students 300 \
		--deadline-profile "-20" --grade-maxpoints 10
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.hxx.week7 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students 300 \
		--deadline-profile "old" --grade-maxpoints 9
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.hxx.week9 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students 300 \
		--deadline-profile "recent" --grade-maxpoints 12
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.hxx.week10 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students 300 \
		--deadline-profile "soon" --grade-maxpoints 6

backup-exampledata:
	rm -rf $(EXAMPLEDATA_BACKUP)
	mkdir $(EXAMPLEDATA_BACKUP)
	echo ".dump" | sqlite3 db.sqlite3 > $(EXAMPLEDATA_BACKUP)/dbdump.sql
	cp deliverystore.dbm.dat $(EXAMPLEDATA_BACKUP)/
	cp deliverystore.dbm.dir $(EXAMPLEDATA_BACKUP)/
	tar -cvf $(EXAMPLEDATA_BACKUP).tar $(EXAMPLEDATA_BACKUP)
	lzma $(EXAMPLEDATA_BACKUP).tar

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
