====================================
How to release a new Devilry version
====================================

1. Merge all changes into the ``production`` branch. Normally from ``master`` into ``production``.
2. Update ``devilry/version.json``.
3. Remove old builds from ``devilry/devilry_theme3/static/devilry_theme3/`` (empty the directory).
4. Production build the javascript: ``ievv buildstatic --production``
5. Commit these changes with ``Release <version>``.
6. Tag these changes with ``git tag <version>``.
7. Make source dist: ``python setup.py sdist``
8. Release to pypi: ``twine upload dist/devilry-<version>.tar.gz``
9. Push the changes to the remote ``production`` branch.
10. Merge the changes in the ``production`` branch into the ``master`` branch, and push to the remote master branch.
