# vim: set ts=4 sts=4 noexpandtab sw=4:

PRODTEST=devilry.cfg.test2
PROD=devilry.cfg.prod1
EXAMPLEDATA_BACKUP=exampledata-backup
HTMLHELP=Makefile.readme.rst.html
NUM_STUDENTS=30
NUM_EXAMINERS=2

USER=../adminscripts/bin/devilry-user.py


help:
	@cat Makefile.readme.rst

htmlhelp:
	rst2html.py Makefile.readme.rst > $(HTMLHELP)
	@echo
	@echo "Created $(HTMLHELP)"


cleardb:
	rm -f db.sqlite3
	python manage.py syncdb --noinput
	@echo
	@echo "Database is now clean."
	@echo "Use 'python manage.py loaddata' to load fixtures into the empty database. Example:"
	@echo
	@echo "   ~# python manage.py loaddata core/fixtures/tests/core/*.json"


#######################################################
# Example db
#######################################################

create-duck1100-data:
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.week1 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "-30" --grade-maxpoints 14 \
		--subject-long-name "DUCK1100 - Getting started with python" \
		--period-long-name "Spring year zero" \
		--assignment-long-name "The one and only week one"
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.week2 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "-20" --grade-maxpoints 10 \
		--assignment-long-name "The one and only week two"
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.week3 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "old" --grade-maxpoints 9 \
		--assignment-long-name "The one and only week three"
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.week4 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "recent" --grade-maxpoints 12 \
		--assignment-long-name "The one and only week four"
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.week5 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "soon" --grade-maxpoints 6 \
		--assignment-long-name "The one and only week five"

	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.proj1 \
		--grade-plugin "grade_approved:approvedgrade" \
		--num-students 10 --num-examiners=$(NUM_EXAMINERS) \
		--student-name-prefix=projstud --pointscale=40\
		--deadline-profile "recent" \
		--assignment-long-name "Project one"
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1100.h01.proj2 \
		--grade-plugin "grade_approved:approvedgrade" \
		--num-students 8 --num-examiners=$(NUM_EXAMINERS) \
		--student-name-prefix=projstud \
		--deadline-profile "soon" --pointscale=30 \
		--assignment-long-name "Project two"

create-duck1080-data:
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1080.h01.week1 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "-30" --grade-maxpoints 11 \
		--pointscale 10 \
		--subject-long-name "DUCK1080 - Making the illogical seem logical" \
		--period-long-name "Fall year zero" \
		--assignment-long-name "Week one"
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1080.h01.week2 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "-20" --grade-maxpoints 9 \
		--pointscale 10 \
		--assignment-long-name "Week two"
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1080.h01.week3 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "recent" --grade-maxpoints 8 \
		--pointscale 10 \
		--assignment-long-name "Week three"
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck1080.h01.week4 \
		--grade-plugin "grade_rstschema:rstschemagrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "soon" --grade-maxpoints 14 \
		--pointscale 10 \
		--assignment-long-name "Week four"

create-duck3580-data:
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck3580.h01.week1 \
		--grade-plugin "grade_approved:approvedgrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "-30" \
		--subject-long-name "DUCK3580 - Making the illogical seem logical" \
		--period-long-name "Fall year zero" \
		--assignment-long-name "Week one"
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck3580.h01.week2 \
		--grade-plugin "grade_approved:approvedgrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "-20" \
		--assignment-long-name "Week two"
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck3580.h01.week3 \
		--grade-plugin "grade_approved:approvedgrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "recent" \
		--assignment-long-name "Week three"
	python adminscripts/create_testgroups.py \
		duckburgh.univ:duck3580.h01.week4 \
		--grade-plugin "grade_approved:approvedgrade" \
		--num-students $(NUM_STUDENTS) --num-examiners=$(NUM_EXAMINERS) \
		--deadline-profile "soon" \
		--assignment-long-name "Week four"


clear-exampledb: cleardb
	rm -rf deliverystore

init-exampledb: clear-exampledb
	mkdir deliverystore
	python manage.py loaddata -v0 core/fixtures/example/users.json

create-exampledb: init-exampledb create-duck1100-data create-duck1080-data create-duck3580-data

backup-exampledb:
	rm -rf $(EXAMPLEDATA_BACKUP)
	rm -f $(EXAMPLEDATA_BACKUP).tar.bz2
	mkdir $(EXAMPLEDATA_BACKUP)
	sqlite3 db.sqlite3 .dump > $(EXAMPLEDATA_BACKUP)/dbdump.sql
	cp -r deliverystore $(EXAMPLEDATA_BACKUP)
	tar -cvjf $(EXAMPLEDATA_BACKUP).tar.bz2 $(EXAMPLEDATA_BACKUP)
	rm -rf $(EXAMPLEDATA_BACKUP)

restore-exampledb:
	rm -f db.sqlite3
	rm -rf deliverystore
	tar -xjf $(EXAMPLEDATA_BACKUP).tar.bz2
	mv $(EXAMPLEDATA_BACKUP)/deliverystore ./
	sqlite3 db.sqlite3 < $(EXAMPLEDATA_BACKUP)/dbdump.sql
	rm -rf $(EXAMPLEDATA_BACKUP)



######################################################
# Selenium testing
######################################################

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


###########################################################
# Test coverage
###########################################################

test:
	coverage -x manage.py test

html-testreport: test
	coverage html

###########################################################
# Doc
###########################################################

htmldoc:
	make -C ../doc/ html
cleanhtmldoc:
	make -C ../doc/ clean
