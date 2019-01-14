##################################################
:mod:`devilry_report` --- Devilry report framework
##################################################

The ``devilry_report`` module provides a framework for generating downloadable reports.


*************
Datamodel API
*************

.. currentmodule:: devilry.devilry_report

.. automodule:: devilry.devilry_report.models
    :members:



**********
Generators
**********

The framework provides an abstract generator-class you will need to subclass. You need to implement a set of
required methods in the generator-subclass, and the actual data parsing.

.. currentmodule:: devilry.devilry_report

.. automodule:: devilry.devilry_report.abstract_generator
    :members:



******************
Generator registry
******************

To be able to use a generator, you need to register the generator-class in a registry singleton in the `apps.py`-file
in the app you where the generator belongs. Do NOT create or register generators in the `devilry_report`-app, this is a
framework, and thus other apps should be dependent on this app not the other way around.

.. currentmodule:: devilry.devilry_report

.. automodule:: devilry.devilry_report.generator_registry
    :members:


Simple example of the basic usage
=================================


1. Create your generator class
******************************

In some app of your choice, subclass the `AbstractReportGenerator`-class and override the required methods.
See the class for which methods to override.


2. Register the generator-class
*******************************

Register you generator in the `apps.py`-file::

    class SomeDevilryAppConfig(AppConfig):
    name = 'devilry.devilry_admin'
    verbose_name = 'Devilry admin'

    def ready(self):
        from devilry.devilry_report import generator_registry as report_generator_registry
        from devilry.devilry_someapp.path.to.generator import MyGenerator

        report_generator_registry.Registry.get_instance().add(
            generator_class=MyGenerator
        )


3. Implementing support for starting the report generation and download
***********************************************************************

To implement support for generating and downloading the report, you need to provide valid data for the report
download view. The view for generating and downloading a report is the same view, but generation is triggered via the
HTTP POST method, and download via HTTP GET.

To generate a report, we need to add support for posting to the generate/download view. This view requires a JSON-blob
defining as a minimum what generator-type to use.

1. Add the generate/download view to your urls.
By default, the DownloadReportView only accepts a download by the user that created the report. If you need any extra
permission-checks, you will need to subclass the view. The view can be added to a urls.py file, or an CrAdmin-app.
We'll use a CrAdmin-app for this example::

        DownloadReportView.as_view(),
        name='download_report')


2. Add a JSON-blob that can be posted to the DownloadReportView. This is usually added in the `get_context_data`-method
of the view that supports generating a report::

    def get_context_data(self, **kwargs):
        ...
        context['report_options'] = json.dumps({
            'generator_type': '<generatortype (defined by get_generator_type on you generator-class)>',
            'generator_options': {// You can provide data here if you generator-class requires it, else leave this empty}
        })
        return context


3. Add a form for posting the `report_options` data in the template::

    <form action="{% cradmin_appurl 'download_report' %}" method="POST">
        {% csrf_token %}
        <input type="hidden" name="report_options" value="{{ report_options }}">
        <input class="btn btn-primary" type="submit" name="confirm" value="{% trans "Download results" %}"/>
    </form>
