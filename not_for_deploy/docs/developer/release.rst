====================================
How to release a new Devilry version
====================================

1. Merge all changes into the ``production`` branch. Normally from ``master`` into ``production``.
2. Update ``devilry/version.json``.
3. Remove old builds from ``devilry/devilry_theme3/static/devilry_theme3/`` (empty the directory).
4. Production build the javascript: ``ievv buildstatic --production``
5. Make source dist: ``python setup.py sdist``
6. Release to pypi: ``twine upload devilry-<version>.tar.gz``
