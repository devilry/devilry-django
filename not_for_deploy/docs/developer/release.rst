====================================
How to release a new Devilry version
====================================

In the devilry-django repo
##########################

1. Make sure you build and commit any changed ExtJS apps (see
   :doc:`javascript`). Make sure to test out student, examiner, course admin
   and department admin roles with the ``EXTJS4_DEBUG=False`` setting
   as explained in :doc:`javascript`.

2. Update the version number in::
   
      devilry/version.json

3. Add a releasenotes document in ``docs/releasenotes-X.Y.Z.rst``, and commit
   the new file.
4. Commit the version changes.
5. Tag the release::

    $ git tag vX.Y.Z

6. Push the changes::

    $ git push
    $ git push --tags

7. Push the changes to pypi::

   $ python setup.py sdist upload
