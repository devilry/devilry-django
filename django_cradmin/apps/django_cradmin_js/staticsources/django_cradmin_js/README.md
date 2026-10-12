# django_cradmin_js

Javascript library for https://github.com/appressoas/django_cradmin.


## Install

```
$ npm install django_cradmin_js --save-dev
.. or ..
$ yarn add django_cradmin_js --dev
```


## Docs

1. Clone a local copy of the https://github.com/appressoas/django_cradmin git repo.
2. ``cd django_cradmin/apps/django_cradmin_js/staticsources/django_cradmin_js/``
3. Run ``npm install`` or ``yarn`` (depending on your preferred package manager)
4. Run ``npm run build-docs`` or ``yarn run build-docs`` (depending on your preferred package manager)
5. Open ``built_docs/index.html`` in a browser.



## Release a new version
(for people with publish permissions for the npm package)

1. Update the ``version`` in ``package.json``.
2. ``npm publish``.
3. Git commit the changes. The commit should be
   ``Release django_cradmin_js <version>``
   where ``<version>`` is the same version as you used in (2).
4. ``git tag django_cradmin_js-<version>`` where ``<version>`` is the same version as
   you used in (2).
5. ``git push && git push --tags``.
