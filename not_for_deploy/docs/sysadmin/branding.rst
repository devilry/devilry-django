################
Branding devilry
################


******************************
Simple branding with templates
******************************

Setup
=====
First, you need to create a directory to hold custom templates.
This directory needs to have a subdirectory named ``devilry_deploy``,
and it is in this subdirectory you will add your custom templates.
For this guide, we will assume you use ``~/devilrydeploy/custom_devilry_templates/``::

    $ mkdir ~/devilrydeploy/custom_devilry_templates/
    $ mkdir ~/devilrydeploy/custom_devilry_templates/devilry_deploy/

When the directory is created, you need to add it to your
``~/devilry_deploy/devilry_settings.py``::

    from devilry.utils.custom_templates import add_custom_templates_directory
    add_custom_templates_directory(
        TEMPLATES,
        '/absolute/path/to/devilrydeploy/custom_devilry_templates/')


.. _branding_footer:

Add a footer to all pages
=========================
To add a footer to all pages, you need to create
``~/devilrydeploy/custom_devilry_templates/devilry_deploy/footer.django.html``.

Example template content:

.. code-block:: django

    {% extends "devilry_deploy/footer_base.django.html" %}

    {% block content %}
        <p>
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/af/Tux.png"
                class="footer__logo">
        </p>
        <p>
            Vivamus sagittis lacus vel augue laoreet rutrum faucibus dolor auctor.
            Nullam id dolor id nibh ultricies vehicula ut id elit.
            Cras mattis consectetur purus sit amet fermentum.
            Aenean lacinia bibendum nulla sed consectetur.
            Etiam porta sem malesuada magna mollis euismod.
        </p>

        <p>
            <a href="http://example.com/support">Support</a>
            |
            <a href="http://example.com/faq">Common questions</a>
        </p>
    {% endblock content %}


Notice that we provide a css-class for the logo (if you have a logo).
You can adjust the size of the logo by changing the class of the
logo image to one of these:

- ``footer__logo footer__logo--small``
- ``footer__logo footer__logo--large``
- ``footer__logo footer__logo--xlarge``



Add a footer to the frontpage
=============================
This can be used to only add a footer to the frontpage, or if you
have a footer for all pages (see :ref:`branding_footer`),
you can use this to have a different footer on the frontpage.

The frontpage is the page where users select their role (student, examiner, ...),
and it is the page they come to right after logging in.

To add a footer to the frontpage, you need to create
``~/devilrydeploy/custom_devilry_templates/devilry_deploy/frontpage_footer.django.html``.
The format is exactly the same as for ``footer.django.html`` (see :ref:`branding_footer`).



Add a footer to the login page
==============================
This can be used to only add a footer to the login page, or if you
have a footer for all pages (see :ref:`branding_footer`),
you can use this to have a different footer on the login page.

To add a footer to the login page, you need to create
``~/devilrydeploy/custom_devilry_templates/devilry_deploy/login_footer.django.html``.
The format is exactly the same as for ``footer.django.html`` (see :ref:`branding_footer`).



Add custom CSS
==============
To add custom CSS, you need to create
``~/devilrydeploy/custom_devilry_templates/devilry_deploy/custom_css.django.css``.

Lets make the color of all text in the footer red:

.. code-block:: django

    {% extends "devilry_deploy/custom_css_base.django.html" %}

    {% block css %}
        .footer {
            color: red;
        }
    {% endblock css %}

You can override any CSS from Devilry, but be VERY careful. Generally
speaking, you should mostly use this to add css classes that
you use in custom templates, such as the footer documented above.


****************************
Available template variables
****************************
Template variables you can use in your branding templates:

- ``DEVILRY_VERSION``: Gives the devilry version (Example: ``3.0.0``)


*****************
Advanced branding
*****************
You can go much further than the simple branding provided with
templates above. If you know Django, you can override a lot of templates,
and if you know LESS, you can create your own theme. We do not have
a guide for this at this time. Generally, we do not recommend this
since it will require you to keep up to date with changes in the
Devilry styles and templates.
