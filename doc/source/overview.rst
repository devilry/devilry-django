.. _overview:

=========================================================
Overview
=========================================================


.. image:: http://yuml.me/diagram/scruffy;dir:LR;scale:80;/class/[Node]++1-subjects >*[Subject], [Node]++0-child-nodes >*[Node], [Subject]++1-periods >*[Period], [Period]++1-assignments >*[Assignment]


Node
====

A node at the top of the navigation tree. It is a generic element used to
organize administrators. A Node can be organized below another Node, and it
can only have one parent.

Let us say you use Devilry within two departments at *Fantasy University*;
mathematics and physics. The university have a administration, and each
department have their own administration. You would end ut with this
node-hierarchy:

    - Fantasy University
        - Department of informatics
        - Department of mathematics

Subject
=======
A subject is a course, seminar, class or something else beeing given
regularly. A subject is further divided into periods.

Period
======
A Period is a limited period of time, like *spring 2009*, *week 34 2010* or
even a single day.

Assignment
==========
TODO
