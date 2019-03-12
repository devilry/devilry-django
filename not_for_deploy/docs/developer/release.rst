====================================
How to release a new Devilry version
====================================

- Add a migration guide to ``not_for_deploy/docs/sysadmin/migrationguides/``.
- Add a changelog to ``not_for_deploy/docs/user/changelog/``.
- Commit migration guide and changelog.
- Merge all changes into the ``production`` branch. Normally from ``master`` into ``production``.
- Update ``devilry/version.json``.
- Run ``fab make_source_dist``.
- Commit these changes with ``Release <version>``.
- Tag these changes with ``git tag <version>``.
- Release to pypi: ``twine upload dist/devilry-<version>.tar.gz``.
- Push the changes to the remote ``production`` branch with (``git push && git push --tags``).
- Merge the changes in the ``production`` branch into the ``master`` branch, and push to the remote master branch.
