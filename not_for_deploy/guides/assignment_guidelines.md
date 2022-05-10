# The assignment guidelines system

## What it solves
The assignment guidelines system makes it possible to force students and examiners
to read guidelines before they can access the feedback feed for an assignment.
It is mainly for student guidelines, but since it did not add any complexity,
we also added support for guidelines for other roles. The solution is not
fully integrated for examiners because it is not shown when they are
providing bulk feedback, but if the need arises, it should be easy to extend
to that use case too.

First described in https://github.com/devilry/devilry-django/issues/1068.


## Usage

You set it up via the ``DEVILRY_ASSIGNMENT_GUIDELINES`` setting. Example:

```python
DEVILRY_ASSIGNMENT_GUIDELINES = {
    'student': [

        # These regexes are matched in order. That means that you should add more
        # specific regexes first.
        #: You can test the regexes using ``python manage.py devilry_show_assignment_guidelines``.
        (r'duckin10.+', {
            # If you change any of the texts or urls below, you should update the version. That will force
            # students to read the updated guidelines.
            '__version__': '1',

            # The default is the fallback if the languagecode the user has selected does not appear in this map.
            '__default__': {
                'htmltext': 'This is the assignment guidelines for duckin10xx courses.',
                'url': 'http://example.com'
            },

            # Translated guidelines for norwegian bokmaal.
            'nb': {
                'htmltext': 'Dette er retningslinjene for oppgaver i duckin10xx kurs',
                'url': 'http://example.com'
            }
        }),
        (r'duckin.+', {
            '__version__': '1',
            '__default__': {
                'htmltext': 'This is the assignment guidelines for duckin courses.',
                'url': 'http://example.com'
            }
        }),
        (r'duckmath.+', {
            '__version__': '1',
            '__default__': {
                'htmltext': 'This is the assignment guidelines for duckmath courses.',
                'url': 'http://example.com'
            }
        })
    ]
}
```

As mentioned above in the example, you can use the:

```
$ python manage.py devilry_show_assignment_guidelines <subject-short-name>.<period-short-name> <devilryrole>
```

management script to debug regex matching and see what is shown to your users. For students, ``<devilryrole>`` is ``student``.


### The ``__version__`` option
The ``__version__`` option is required. Changing it will force users that have already
accepted the guidelines for a Period to do so again. It is recommended to use
some structured info in the version, like a number or a change date as a string etc.
The version is not shown to the users, it is just something to trigger/force showing
the guidelines again if they change in within the active period.
