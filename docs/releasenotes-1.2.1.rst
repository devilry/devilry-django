====================================
1.2.1 release notes
====================================

.. warning:: This is incomplete because the version has not been released yet.

##############################
Major changes
##############################

New subject admin UI
====================
A completely new user interface for subject (course) administrators. The UI has more or less all of
the features of the old UI, but it is far more user-friendly and optimized for common task.


New node admin UI
=================
Because the old admin interface was for both node and subject administrator, we had to
make a new UI for node administrators when we replaced it. This UI is not very powerful
in this release, but we plan to improve it gradually in cooperation with its users.


New qualified for final exam app
================================
The qualified for final exam app has been rewritten. It now uses a very user-friendly wizard
to guide users through the process, and the entire system in plugin-based, so is is relatively
easy to add support for more complex scenarios than the build-in plugins support. In addition
to a plugin based architecture, the new app adds some useful new features:

- Support for *almost finished*. This solves the problem that arises when just a couple of the
  students need more time, but you want to export the rest of the students as ready for exams.
  The support is really simple:
    - The entire period/semester is marked as *almost ready for export*.
    - The administrator gets a message field where they can explain the situation.
    - The administrator has to select the students that is not ready for export.