====================================
How to release a new Devilry version
====================================

In the devilry-django repo:

1. Update the version number in ``src/devilry/setup.py``.
2. Update the version number in ``docs/conf.py``.
3. Tag the release::

    $ git tag vX.Y.Z


In the devilry-deploy repo:

1. Update the version number in ``docs/src/conf.py``
2. Tag the release just like you did for devilry-django above.


In the devilry-userdoc repo:

1. Update the version number in ``conf.py``
2. Tag the release just like you did for devilry-django above.


.. note:: We plan on making this more streamlined in the future --- see :devilryissue:`384`.
