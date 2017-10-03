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


In the devilry-deploy repo
##########################

.. note::

    Make sure all new develop (mr.developer fs) dependencies in
    ``buildout-base.cfg`` or ``buildout.cfg`` in the devilry code repo has been
    added to ``buildout/buildout-base.cfg`` before releasing a new version.

1. Add migration guide to ``docs/src/``, and remember to add the guide to ``migrationguidelisting.rst``.
2. Update the version number in ``docs/src/conf.py``
3. Update the revision id in ``${buildout:extends}`` and
   ``${download-devilryrepo}`` in ``buildout/buildout-base.cfg``. Must use TAG,
   not branch name. Should end up with something like this::

       [buildout]
       extends = https://raw.github.com/devilry/devilry-django/vX.Y.Z/versions.cfg

       ...

       [download-devilryrepo]
       ...
       rev = vX.Y.Z

4. Make sure all the changes from the steps above are committed.
5. Tag the release and push just like you did for devilry-django above.


In the devilry-userdoc repo
###########################

1. Update the version number in ``conf.py``
2. Create a BRANCH named by the version number on the following format: ``X.Y.Z``. Take a look at the output from::

     $ git branch -a

   if you are unsure about the version branch naming format.
3. Push the branch
4. Go to https://readthedocs.org/dashboard/devilry-userdoc/versions/, and
   mark the branch as active. You may have to
   `force a rebuild <https://readthedocs.org/builds/devilry-userdoc/>`_
   before the branch becomes visible.


.. note:: We plan on making this more streamlined in the future --- see :devilryissue:`384`.
