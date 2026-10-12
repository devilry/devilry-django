import functools
import warnings


class CradminDeprecated(object):
    """
    Mark functions, classes, methods or modules as deprecated.

    Examples::

        Function::

            @CradminDeprecated()
            def myfunc():
                pass

        Function with message::

            @CradminDeprecated(message='This is deprecated and should not be used!')
            def myfunc():
                pass


        Method::

            class MyClass:

                @CradminDeprecated(message='This is deprecated and should not be used!')
                def mymethod(self):
                    pass

        Property::

            class MyClass:

                @property
                @CradminDeprecated(message='This is deprecated and should not be used!')
                def myproperty(self):
                    return 10

        Class::

            @CradminDeprecated(message='This is deprecated and should not be used!')
            class MyClass:
                pass

        Module::
            CradminDeprecated(message='This is deprecated and should not be used!')\
                .show_warning(name=__name__)
    """

    def __init__(self, message="Deprecated"):
        self.message = message

    def generate_message(self):
        return self.message

    def show_warning(self, name):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter("always", DeprecationWarning)  # turn off filter
            warnings.warn(
                "{name}: {message}.".format(name=name, message=self.generate_message()),
                category=DeprecationWarning,
                stacklevel=2,
            )

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            self.show_warning(name=func.__name__)
            return func(*args, **kwargs)

        return wrapper


class CradminDeprecatedSinceV4(CradminDeprecated):
    def __init__(self, message=""):
        super(CradminDeprecatedSinceV4, self).__init__(message=message)

    def generate_message(self):
        full_message = "Deprecated in django_cradmin 4.x. Will be removed in a future release"
        if self.message:
            full_message = "{}: {}".format(full_message, self.message)
        return full_message
