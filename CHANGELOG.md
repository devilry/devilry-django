## 6.1.0rc0 (2023-10-31)

### Feat

- **PrintStatusView**: propper sorting and more data displayed

### Fix

- **pyproject.toml**: upped the version of gunicorn to 21
- **devilry_authenticate**: changed allauthloginview to support allauth version > 0.55

## 6.0.1 (2023-10-26)

### Fix

- **AssignmentGradingConfigurationUpdateView**: corrected changing grading for assignments

## 6.0.0 (2023-07-21)

### BREAKING CHANGE

- This will be a major release

### Feat

- Django 4.2 and python 3.10 support     - Add health-check endpoints.     - Group invitations: Now using the devilry_message backend for storing messages.     - WCAG: Contrast-issue with link in "No access" warning-box.     - Translations: Various translation errors.     - Self-assign: Issue with duplicate rows from query when examiner is self-assigning.     - Self-assign: Missing CSRF-token.     - Comment-notification to examiners: When examiner posts comments all admins are notified.

## 6.0.0rc2 (2023-07-20)

### Feat

- Add endpoints readiness and liveness probing

### Fix

- Use CSRF-middleware to ensure CSRF-cookie is set everywhere
- If user is admin and examiner, the user should receive a notification as examiner if they post a comment as an admin.
- E-mail sent to admins when comment-poster was the only examiner in the group
- Group invite - email translations
- Group invite - use devilry_message system
- Use distinct to filter out duplicate rows from AssignmentGroup-query
- translation errors
- Contrast level adjustment for "danger"-box anchor-tag
- Update sphinx and related packages
- readthedocs testing
- **.readthedocs.yml**: Python version 3.8
- **.readthedocs.yml**: Python version 3.10
- Add pip-tools

## 6.0.0rc1 (2023-05-31)

### BREAKING CHANGE

- Django 4.2 support

## 5.5.3 (2022-12-06)

## 5.5.2 (2022-09-20)

## 5.5.1 (2022-06-14)

## 5.5.0 (2022-06-07)

## 5.4.2 (2022-04-21)

## 5.4.1 (2022-03-11)

## 5.4.0 (2022-03-09)

## 5.4.0rc4 (2022-03-03)

## 5.4.0rc3 (2022-03-03)

## 5.4.0rc2 (2022-03-02)

## 5.4.0rc1 (2022-03-02)

## 5.3.1 (2021-09-07)

## 5.3.0 (2021-09-07)

## 5.2.0 (2021-09-03)

## 5.2.0rc2 (2021-09-02)

## 5.2.0rc1 (2021-08-31)

## 5.1.0 (2021-04-30)

## 5.1.0rc4 (2021-04-29)

## 5.1.0rc3 (2021-04-28)

## 5.1.0rc2 (2021-04-27)

## 5.1.0rc1 (2021-04-23)

## 5.0.1 (2021-03-16)

## 5.0.0 (2020-09-25)

## 5.0.0rc1 (2020-09-09)

## 4.0.3 (2019-11-07)

## 5.0.0b2 (2019-07-24)

## 4.0.2 (2019-07-24)

## 5.0.0b1 (2019-06-24)

## 4.0.1 (2019-06-03)

## 4.0.0 (2019-04-23)

## 4.0.0b2 (2019-03-14)

## 4.0.0b1 (2019-03-12)

## 3.7.3 (2019-02-15)

## 3.7.2 (2019-02-11)

## 3.7.1 (2019-01-30)

## 3.7.0 (2019-01-30)

## 3.7.0b1 (2019-01-22)

## 3.6.0 (2019-01-09)

## 3.6.0b1 (2019-01-03)

## 3.5.2 (2018-11-28)

## 3.5.1 (2018-11-23)

## 3.5.0 (2018-11-22)

## 3.4.6 (2018-11-07)

## 3.4.5 (2018-10-30)

## 3.4.4 (2018-10-23)

## 3.4.3 (2018-10-18)

## 3.4.2 (2018-10-18)

## 3.4.1 (2018-10-11)

## 3.4.0 (2018-10-02)

## 3.3.3 (2018-09-25)

## 3.3.2 (2018-09-25)

## 3.3.1 (2018-09-11)

## 3.3.0 (2018-09-06)

## 3.3.0b11 (2018-09-06)

## 3.3.0b10 (2018-08-31)

## 3.3.0b9 (2018-08-28)

## 3.3.0b8 (2018-08-22)

## 3.3.0b7 (2018-08-17)

## 3.3.0b6 (2018-08-15)

## 3.3.0b5 (2018-08-09)

## 3.3.0b4 (2018-08-08)

## 3.3.0b3 (2018-08-07)

## 3.3.0b2 (2018-08-03)

## 3.3.0b1 (2018-07-26)

## 3.1.6 (2018-03-02)

## 3.1.5 (2018-03-01)

## 3.1.4 (2018-02-22)

## 3.1.3 (2018-02-20)

## 3.1.2 (2018-02-19)

## 3.1.1 (2018-02-19)

## 3.1.0 (2018-02-15)

## 3.0.3 (2018-01-31)

## 3.0.2 (2018-01-31)

## 3.0.1 (2018-01-29)

## 3.0.0 (2018-01-19)

## 3.0.0a25 (2017-07-02)

## 3.0.0a24 (2017-07-01)

## 3.0.0a23 (2017-06-30)

## 3.0.0a22 (2017-06-30)

## 3.0.0a8 (2017-06-14)

## 3.0.0a7 (2017-06-14)

## 3.0.0a5 (2017-06-14)

## 3.0.0a4 (2017-06-14)

## 3.0.0a3 (2017-06-13)

## 3.0.0a2 (2017-03-08)

## 2.1.0-beta.016 (2015-06-04)

## 2.1.0-beta.014 (2015-06-03)

## 2.1.0-beta.013 (2015-06-02)

## 2.1.0-beta.012 (2015-06-01)

## 2.1.0-beta.011 (2015-06-01)

## release-2.1.0-beta.010 (2015-06-01)

## release-2.1.0-beta.009 (2015-05-31)

## release-2.1.0-beta.008 (2015-05-31)

## release-2.1.0-beta.007 (2015-05-31)

## release-2.1.0-beta.006 (2015-05-31)

## release-2.1.0-beta.005 (2015-05-31)

## release-2.1.0-beta.003 (2015-05-31)

## release-2.1.0-beta.002 (2015-05-31)

## release-2.1.0-beta.001 (2015-05-30)

## 2.0.0 (2015-02-25)

## 2.0.0-rc.004 (2015-02-25)

## 2.0.0-rc.003 (2015-02-19)

## 2.0.0-rc.002 (2015-02-11)

## 2.0.0-rc.001 (2015-02-11)

## v1.4.14 (2014-12-09)

## v1.4.13 (2014-12-07)

## v1.4.12 (2014-11-17)

## v1.4.11 (2014-11-12)

## v1.4.10 (2014-11-11)

## v1.4.9 (2014-10-28)

## v1.4.8 (2014-04-10)

## v1.4.7 (2014-03-26)

## v1.4.6 (2014-03-03)

## v1.4.5 (2014-02-16)

## v1.4.4.2 (2014-02-03)

## v1.4.4.1 (2014-01-30)

## v1.4.4 (2014-01-29)

## v1.4.3 (2014-01-27)

## v1.4.2 (2014-01-24)

## v1.4.1 (2014-01-20)

## v1.4.0 (2014-01-20)

## v1.3.6 (2013-11-13)

## v1.3.5 (2013-11-07)

## v1.3.4 (2013-10-14)

## v1.3.3 (2013-10-14)

## v1.3.2 (2013-10-10)

## v1.3.1 (2013-09-12)

## v1.3.1-beta2 (2013-09-12)

## v1.3.1-beta (2013-09-12)

## v1.3 (2013-08-12)

## v1.3-beta1 (2013-08-12)

## v1.2.1.10 (2013-05-22)

## v1.2.1.9 (2013-05-16)

## v1.2.1.8 (2013-05-06)

## v1.2.1.7 (2013-05-04)

## v1.2.1.6 (2013-03-07)

## v1.2.1.5 (2013-03-03)

## v1.2.1.4 (2013-02-12)

## v1.2.1.3 (2013-02-06)

## v1.2.1.2 (2013-01-31)

## v1.2.1.1 (2013-01-31)

## v1.2.1 (2013-01-18)

## v1.2.1rc2 (2013-01-17)

## v1.2.1rc1 (2013-01-17)

## v1.1rc4 (2012-08-30)

## v1.1rc3 (2012-08-28)

## v1.1rc2 (2012-08-28)

## v1.1rc1 (2012-08-27)

## v1.1b1 (2012-08-25)

## v1.1a3 (2012-08-20)

## v1.1a2 (2012-08-20)

## v1.1a1 (2012-08-19)

## before_subjectadminmerge (2012-07-24)

## v1.0.1 (2012-08-19)

## v1.0 (2011-12-01)

## v0.1.5 (2011-02-26)

## v0.1.4 (2011-02-21)

## v0.1.3 (2011-02-11)

## v0.1.2 (2010-11-10)

## v0.1.1 (2010-11-10)

## v0.1.0 (2010-09-05)
