test: test-core

test-core:
	coverage -x manage.py test core


html-testreport: test
	coverage html

clean:
	coverage erase
