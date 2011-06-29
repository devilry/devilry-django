.. _devilry.utils.groupnodes:

==========================================================
:mod:`devilry.utils.groupnodes`
==========================================================

.. class:: devilry.utils.GroupNode

   The node object containing a node, and GroupNode children.

.. py:function:: group_assignmentgroups(assignment_group_list)

   Creates a tree where each assignmentgroup  is represented as a GroupNode.
   assignmentgroups with the same parent (period) are grouped together.

.. py:function:: group_assignments(assignment_list)

   Creates a tree where each assignment is represented as a GroupNode.
   assignments with the same parent (period) are grouped together.
   

.. py:function:: group_nodes(node_list, tree_height)

   Creates a tree where each node is represented as a GroupNode.
   nodes with the same parent (period) are grouped together.
   
