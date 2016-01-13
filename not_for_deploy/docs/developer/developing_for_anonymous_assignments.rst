####################################
Developing for anonymous assignments
####################################

Ensuring that anonymous assignments does not bleed any information
about data that should be anonymous is fairly straight forward:

- Use the ``*_displayname`` tags in :doc:`devilry_core_tags`.
- If the template tags are not enough, use
  :meth:`devilry.apps.core.models.Assignment.students_must_be_anonymized_for_devilryrole`
  and :meth:`devilry.apps.core.models.Assignment.examiners_must_be_anonymized_for_devilryrole`
  to determine what needs to be anonymized for the assignment.
- Read the plain text explaination of the choices for the anonymizationmode field.
  You find this in the ``ANONYMIZATIONMODE_CHOICES`` attribute of
  ``devilry.apps.core.models.Assignment`` (in the source code).
- Read https://github.com/devilry/devilry-django/issues/846 for extra restrictions
  with ``fully_anonymous`` assignments in the admin UI.


********
In tests
********
The most important thing is to have tests that:

- Adds users with shortname and fullname (examiners and candidates) to an
  anonymous assignment.
- Use ``assertNotIn`` to ensure names that should not be visible anywhere in
 the HTML is not present. E.g.: ``self.assertNotIn('shortnameofuser', mockresponse.response.content)``.

Write tests like these for all of the 3 legal values for
:obj:`devilry.apps.core.models.Assignment.anonymizationmode`.

You should, of course, also do some more structure sanity tests that checks that things are rendered
with the correct CSS class, but you do not need to rewrite the tests for the tags in ``devilry_core_tags``
as long as your tests check that things that should be anonymized get one css class, and other things
get other css classes. The important css classes are:

- ``devilry-user-verbose-inline``: This is used for users when they are not anonymized.
- ``devilry-core-candidate-anonymous-name``: This is used for anonymized Candidates.
- ``devilry-core-examiner-anonymous-name``: This is used for anonymized Examiners.
