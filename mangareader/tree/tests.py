"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    unit tests for walking a tree
"""

import unittest
from mangareader.tree.walk import step

# mockup classes

class FakeNode(object):
    def __init__(self, name, children=None):
        self.name = name
        self.parent = None
        if children:
            self.isdir = True
            self.isfile = False
            self.ls = children
            for node in self.ls:
                node.parent = self # the tree can be dumb! we manage our own children
        else:
            self.isdir = False
            self.isfile = True
    def __repr__(self):
        return "[node \"%s\"]" % self.name

class FakeTree(object):
    def __init__(self, root):
        self.root = root
    def parent(self, node):
        return node.parent
    def _sibling(self, node, offset):
        parent = self.parent(node)
        index = parent.ls.index(node)
        sibdex = index + offset
        if 0 <= sibdex < len(parent.ls):
            return parent.ls[sibdex]
        else:
            return None
    def sibling_next(self, node):
        return self._sibling(node, 1)
    def sibling_prev(self, node):
        return self._sibling(node, -1)


class TestBasicWalking(unittest.TestCase):

    def setUp(self):
        self.basic_tree = FakeTree(
            FakeNode( # root
                name = 'root',
                children = [
                    FakeNode(name='ch01', 
                        children = [
                            FakeNode(name='01'),
                            FakeNode(name='02'),
                            FakeNode(name='03'),
                            FakeNode(name='04'),
                            FakeNode(name='05'),
                                   ]
                                ),
                    FakeNode(name='ch02', 
                        children = [
                            FakeNode(name='06'),
                            FakeNode(name='07'),
                            FakeNode(name='08'),
                            FakeNode(name='09'),
                            FakeNode(name='10'),
                                   ]
                                ),
                           ]
                    )
        )

    def test_stepping(self):
        tree = self.basic_tree
        node = tree.root
        for name in ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10'):
            node = step(tree, node)
            print node
            self.assertEqual(node.name, name)
        self.assertTrue(step(tree, node) is None)

if __name__ == '__main__':
    unittest.main()

