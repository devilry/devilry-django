from devilry.core.utils import OrderedDict


def group_assignmentgroups(assignment_groups):
    return group_nodes(assignment_groups, 3)

def group_assignments(assignments):
    return group_nodes(assignments, 2)


def group_nodes(nodes, tree_height):

    dict = OrderedDict()

    for node in nodes:

        print "make-node-list"
        list = make_node_list(Node(node), tree_height)
        print "listname:" + str(list.get_name())
        print "\n"

        if not dict.has_key(list.get_name()):
            dict[list.get_name()] = list
        else:
            dict[list.get_name()].merge(list)


    for n in dict.values():
        print "Printing tree:"
        print_tree(n)

    return dict.itervalues()


def make_node_list(child_node, list_count):
    
    print "make_node_list:" + str(child_node)

    parent = Node(child_node.node.parentnode) 
    parent.add_child(child_node)
    
    print "parent:" + str(parent.get_name())

    if list_count == 0:
        return parent
    else:
        list_count -= 1
        return make_node_list(parent, list_count)


class Node(object):

    def __init__(self, node):
        self.children = OrderedDict()
        self.node = node
            
    def __str__(self):
        
        if hasattr(self.node, 'short_name'):
            return self.node.short_name
        else:
            return "no_name"

    def get_name(self):
        return self.__str__()

    def add_child(self, child_node):
        
        if not hasattr(child_node.node, 'short_name'):
            self.children[child_node] = child_node
        else:
            if not self.children.has_key(child_node.get_name()):
                self.children[child_node.get_name()] = child_node
            else:
                self.children[child_node.get_name()].merge(child_node)

    # Merge the list with the current node
    def merge(self, list):
        print "merge:" + str(list.get_name())
        for n in list:
            self.add_child(n)

    def __iter__(self):
        return iter(self.children.values())

def print_tree(node):
    
    print "node:" + str(node.get_name())

    for child in node:
        print_tree(child)
