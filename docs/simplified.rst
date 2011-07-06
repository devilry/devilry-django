.. _simplified:

==========================================
Simplified API
==========================================

.. currentmodule:: devilry.simplified

This API was first introduced in this `github issue <https://github.com/devilry/devilry-django/issues/90>`_

The simplified API is a simple task oriented API which simplifies the most
common needs. It is a API which lends itself naturally to be exposed
as a RESTful web service API. This API is the public interface for devilry in any
language and platform:

    - RESTful web services
    - javascript
    - serverside python
    - client libraries using the RESTful web API.

This means that a developer who has played around with the javascript in the
Devilry templates, can use the same API if he or she wants to develop a
serverside addon or a command-line script using the official devilry python
bindings.


What is it?
#####################################################################

The devilry core is very powerful and flexible. This unfortunatly makes it a
bit complex. The simplified API makes all the information provided by the core
available through a much more simple API. Instead of the recursive database
API provided by the core, developers get a API where they can say things like:

- give me all deliveries by this user on this assignent.
- update the feedback on this delivery
- get all files in this delivery
- ...


What is it not?
#####################################################################

You can access all data in the devilry core via the simplified API, but it is
limited to the most common ways of accessing this data. This means that you have
to use the core directly if you wish to make complex queries which is not needed
by a common *task*. To put it simple: It is not an API for doing things that are
not supported by the devilry web interface.




Example
#############

The code for a simplified class might look like this::

    @simplified_modelapi
    class Subject(object):
        class Meta:
            model = models.Subject
            resultfields = FieldSpec('id', 'short_name', 'long_name')
            searchfields = FieldSpec('short_name', 'long_name')
            methods = ['search', 'read']

        @classmethod
        def create_searchqryset(cls, user, **kwargs):
            return cls._meta.model.published_where_is_examiner(user)

        @classmethod
        def read_authorize(cls, user, obj):
            if not cls._meta.model.published_where_is_examiner(user).filter(id=obj.id):
                raise PermissionDenied()

This is the API an examiner would use to access a subject in Devilry. Every Simplified API class
has to have the fields *model, resultfields, searchfields* and *methods*. Depending on what methods you define
you will also need to implement some @classmethods in your Simplified class. Lets run through the details::

    class Meta:
        ...

This class contains all the required fields. Lets look at what thiese fields do. 

*model* defines the database model to be used::

    class Meta:
        model = models.Subject
        ...

*resultfields* defines the fields you will get access to when you search/read from the model using this API::

    class Meta:
        ...
        resultfields = FieldSpec(...)
        ...

*searchfields* defines what fields in the model will be used when searching for this object::

    class Meta:
        ...
        searchfields = FieldSpec(...)
        ...

And *methods* define what methods will be created for this class::


    class Meta:
        ...
        methods = [...]

Now let look at the required methods for class Subject.

::

        @classmethod
        def create_searchqryset(cls, user, **kwargs):
            return cls._meta.model.published_where_is_examiner(user)

runs a query in the database for the information *user* has access to with the parameters 
given in *kwargs* and returns this queryset. This is needed for all database-lookups.

::

        @classmethod
        def read_authorize(cls, user, obj):
            if not cls._meta.model.published_where_is_examiner(user).filter(id=obj.id):
                raise PermissionDenied()

simply checkes that *user* has access to the information he/she/it tries to access. This is needed for 
the *read* method we defined in *methods*.

Now its time to start using this API. If you look at the *methods* field you will se that the defined methods are
*read* and *search*, and if we look at the *searchfields* we can search based on *short_name* and *long_name*.
Say we have a subject with short_name = 'dev10' and another subject with short_name = 'dev11'. And we have a user
with username = 'bob' as an examiner in both subjects.

::

    from simplified import Subject

    examinerbob = User.objects.get(username="bob")
    qrywrap = Subject.search(examinerbob, query="dev1")

Then *qrywrap* would contain the two subjects dev10 and dev11, since both short_name's match our query. 
However, of we run::

    from simplified import Subject

    examinerbob = User.objects.get(username="bob")
    qrywrap = Subject.search(examinerbob, query="10")

our query will only match dev10, and *qrywrap* will only contain the subject dev10.
    

Public API
##########

Every function and class in the public API is made available directly in
``devilry.simplified.NAME``.


.. automodule:: devilry.simplified


utils
=====

.. automodule:: devilry.simplified.utils
