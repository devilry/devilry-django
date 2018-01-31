====================================
How to release a new Devilry version
====================================

1. Merge all changes into the ``production`` branch. Normally from ``master`` into ``production``.
2. Update ``devilry/version.json``.
3. ``git rm -r devilry/devilry_theme3/static/devilry_theme3/``
4. Production build the javascript: ``ievv buildstatic --production``
5. ``git add devilry/devilry_theme3/static/devilry_theme3/``
6. Commit these changes with ``Release <version>``.
7. Tag these changes with ``git tag <version>``.
8. Make source dist: ``python setup.py sdist``
9. Release to pypi: ``twine upload dist/devilry-<version>.tar.gz``
10. Push the changes to the remote ``production`` branch.
11. Merge the changes in the ``production`` branch into the ``master`` branch, and push to the remote master branch.
