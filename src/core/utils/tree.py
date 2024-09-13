
class TreeNode:
    def __init__(self, data):
        self.data = data
        self.children = []
        self.parent = None

    def add_child(self,child):
        child.parent = self
        self.children.append(child)

    def get_level(self):
        level = 0
        p = self.parent
        while p :
            p = p.parent
            level += 1
        return level

    def print_tree(self):
        print('  '*self.get_level() + '|--', end = '')
        print(self.data)
        if self.children:
            for each in self.children:
                each.print_tree()


class HierarchyTree:

    def __init__(self):
        self.node_map = {}

    def insert(self, key, parent_key, data):
        parent = None
        if parent_key is not None:
            parent = self.node_map.get(parent_key)
            if not parent:
                parent = TreeNode(None) # empty node
                self.node_map[parent_key] = parent

        node = self.node_map.get(key)
        if node:
            node.data = data # in case it was an empty node, set data (parent use case)
        else:
            node = TreeNode(data)
            self.node_map[key] = node

        if parent:
            parent.add_child(node)

    def get_roots(self):
        roots = []
        for dummy, node in self.node_map.items():
            if node.parent is None:
                roots.append(node)
        return roots

