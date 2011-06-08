from . import OrderedDict

def group_assignmentgroups(assignment_group_list):
    """
    Groups a list of assignment_groups.
    """
    return group_nodes(assignment_group_list, 2)

def group_assignments(assignment_list):
    """
    Groups a list of assignments.
    """
    return group_nodes(assignment_list, 1)

def group_nodes(node_list, tree_height):
    """
    Groups a list of nodes.
    """
    dict = OrderedDict()
    for node in node_list:
        nodelist = _make_node_list(GroupNode(node), tree_height)
        if not dict.has_key(nodelist.get_name()):
            dict[nodelist.get_name()] = nodelist
        else:
            dict[nodelist.get_name()].merge(nodelist)
    return dict.values() # we usually need to know the length, so values() instead of itervalues()

def _make_node_list(child_node, list_count):
    """
    Creates a list of GroupNodes. This is used by the method group_nodes before
    creating the tree of GroupNodes.
    """
    parent = GroupNode(child_node.node.parentnode) 
    parent.add_child(child_node)
    if list_count == 0:
        return parent
    else:
        list_count -= 1
        return _make_node_list(parent, list_count)

def print_tree(node, depth=1):
    """
    Print the tree of GroupNodes. 
    """
    for child in node:
        print "  " * depth + child.get_name()
        print_tree(child, depth+1)

class GroupNode(object):
    """
    .. attribute:: children

       The :class:`OrderedDict` containing all the children of this node.

    .. attribute:: node

        The node element of this GroupNode.
        
    """
    def __init__(self, node):
        self.children = OrderedDict()
        self.node = node
        self.display_group = False
    
    def __unicode__(self):
        if hasattr(self.node, 'short_name'):
            return self.node.short_name
        elif hasattr(self.node, 'long_name'):
            return self.node.long_name
        else:
            if self.display_group:
                return self.node.parentnode.long_name + " (" + self.node.get_candidates() + ")"
            else:
                return self.node.parentnode.long_name

    def get_name(self):
        return self.__unicode__()

    def add_child(self, child_node):
        """
        Add a child to this node.
        """
        # Assignment group doesn't have short_name
        if not hasattr(child_node.node, 'short_name'):
            # Makes sure the candidates are shown if a student 
            # is part of more than one AssignmentGroup
            if len(self.children) != 0:
                child_node.display_group = True
                # Contains only one, set display_group to True for that element as well.
                if len(self.children) == 1:
                    self.children.values()[0].display_group = True
            self.children[child_node] = child_node
        else:
            if not self.children.has_key(child_node.get_name()):
                self.children[child_node.get_name()] = child_node
            else:
                self.children[child_node.get_name()].merge(child_node)

    def merge(self, list):
        """
        Merge the children of this node with the elements of the list.
        """
        for n in list:
            self.add_child(n)

    def __iter__(self):
        return iter(self.children.values())
