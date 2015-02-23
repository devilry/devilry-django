#####################
Release Notes 1.2.1.1
#####################


*************
Major changes
*************

New qualified for final exam app
================================
The qualified for final exam app has been rewritten. It now uses a very user-friendly wizard
to guide users through the process, and the entire system in plugin-based, so is is relatively
easy to add support for more complex scenarios than the build-in plugins support. In addition
to a plugin based architecture, the new app adds some useful new features:

- Support for *almost finished*. This solves the problem that arises when just a couple of the
  students need more time, but you want to export the rest of the students as ready for exams.

  Here is how it works for a subject/course administrator:
    - The entire period/semester is marked as *almost ready for export*.
    - The administrator gets a message field where they can explain the situation.
    - The administrator has to select the students that is not ready for export.

  And for a Node/Department administrator:
    - Gets a list of un-exported periods/semesters, kind of like the TODO-list for examiners.
    - Can mark periods/semesters as exported.
    - If the qualified-for-final-exam status on a period/semester is changed, it re-appears
      in the TODO-list with information about why it has re-appeared.

  For systems that want to auto-export from Devilry:
    - Can get the same information as admins get via their UI via the REST API, and make smart
      choices based on metadata they store about the last time they exported. Devilry saves a
      new status each time an admin makes a change, so it should not be a problem to track
      changes.
