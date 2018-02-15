====================================
How to release a new Devilry version
====================================

- Add a migration guide to ``not_for_deploy/docs/sysadmin/migrationguides/``.
- Add a changelog to ``not_for_deploy/docs/user/changelog/``.
- Merge all changes into the ``production`` branch. Normally from ``master`` into ``production``.
- Update ``devilry/version.json``.
- ``git rm -r devilry/devilry_theme3/static/devilry_theme3/``
- Production build the javascript: ``ievv buildstatic --production``
- ``git add devilry/devilry_theme3/static/devilry_theme3/``
- Commit these changes with ``Release <version>``.
- Tag these changes with ``git tag <version>``.
- Make source dist: ``python setup.py sdist``
- Release to pypi: ``twine upload dist/devilry-<version>.tar.gz``
- Push the changes to the remote ``production`` branch.
- Merge the changes in the ``production`` branch into the ``master`` branch, and push to the remote master branch.
