"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    unit tests for walking a tree
"""

import unittest
from mangareader.tree.walk import step
from mangareader.tree.view import context

# mockup classes

class FakeNode(object):
    def __init__(self, name, children=None):
        self.name = name
        self.parent = None
        if children is None:
            self.isdir = False
            self.isfile = True
        else:
            self.isdir = True
            self.isfile = False
            self.ls = children
            for node in self.ls:
                node.parent = self # the tree can be dumb! we manage our own children
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

    def test_stepping_forward(self):
        tree = self.basic_tree
        node = tree.root
        for name in (str(i).zfill(2) for i in range(1, 11)): # 01 ... 10 (inclusive)
            node = step(tree, node)
            self.assertEqual(node.name, name)
        self.assertTrue(step(tree, node) is None)

    def test_stepping_backward(self):
        tree = self.basic_tree
        node = tree.root
        for name in (str(i).zfill(2) for i in range(10, 0, -1)): # 10 ... 01 (inclusive)
            node = step(tree, node, dir='back')
            self.assertEqual(node.name, name)
        self.assertTrue(step(tree, node, dir='back') is None)

class TestWalkingWithSomeEmptyNodes(TestBasicWalking):
    def setUp(self):
        self.basic_tree = FakeTree(
            FakeNode( # root
                name = 'root',
                children = [
                    FakeNode(name='ch01', 
                        children = [
                            FakeNode(name='01'),
                            FakeNode(name='02'),
                            FakeNode(name='empty1', children=[]),
                            FakeNode(name='03'),
                            FakeNode(name='04'),
                            FakeNode(name='05'),
                                   ]
                                ),
                    FakeNode(name='empty2', children=[]),
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

class TestWalkingWithSomeEmptyAndNestedNodes(TestBasicWalking):
    def setUp(self):
        self.basic_tree = FakeTree(
            FakeNode( # root
                name = 'root',
                children = [
                    FakeNode(name='ch01', 
                        children = [
                            FakeNode('ch01.2', 
                                children = [
                                FakeNode(name='01'),
                                    ]),
                            FakeNode(name='02'),
                            FakeNode(name='empty1', children=[]),
                            FakeNode(name='03'),
                            FakeNode(name='04'),
                            FakeNode(name='05'),
                                   ]
                                ),
                    FakeNode(name='empty2', children=[]),
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

class TestWalkingWithDeeplyNestedNodes(TestBasicWalking):
    def setUp(self):
        self.basic_tree = FakeTree(
            FakeNode( # root
                name = 'root',
                children = [
                    FakeNode(name='ch01', 
                        children = [
                            FakeNode('ch01.2', 
                                children = [
                                FakeNode(name='01'),
                                    ]),
                            FakeNode(name='02'),
                            FakeNode(name='03'),
                            FakeNode(name='04'),
                            FakeNode(name='05'),
                                   ]
                                ),
                    FakeNode(name='empty2', children=[]),
                    FakeNode(name='ch02', 
                        children = [
                            FakeNode(name='06'),
                            FakeNode(name='07'),
                            FakeNode(name='08'),
                            FakeNode(name='09'),
                            FakeNode(name='level1',
                                children=[
                                    FakeNode(name='level2', 
                                        children=[
                                            FakeNode(name='level3',
                                                children=[
                                                    FakeNode(name='10'),
                                                         ])

                                                 ])
                                          ])
                                   ]
                                ),
                           ]
                    )
        )

class TestContextWithDeeplyNestedNodes(unittest.TestCase):
    def setUp(self):
        node6 = FakeNode(name='06')
        self.current_node = node6
        self.basic_tree = FakeTree(
            FakeNode( # root
                name = 'root',
                children = [
                    FakeNode(name='ch01', 
                        children = [
                            FakeNode('ch01.2', 
                                children = [
                                FakeNode(name='01'),
                                    ]),
                            FakeNode(name='02'),
                            FakeNode(name='03'),
                            FakeNode(name='04'),
                            FakeNode(name='05'),
                                   ]
                                ),
                    FakeNode(name='empty2', children=[]),
                    FakeNode(name='ch02', 
                        children = [
                            node6,
                            FakeNode(name='07'),
                            FakeNode(name='08'),
                            FakeNode(name='09'),
                            FakeNode(name='level1',
                                children=[
                                    FakeNode(name='level2', 
                                        children=[
                                            FakeNode(name='level3',
                                                children=[
                                                    FakeNode(name='10'),
                                                         ])

                                                 ])
                                          ])
                                   ]
                                ),
                           ]
                    )
        )
    
    def test_context(self):
        node_context = context(self.basic_tree, self.current_node, items_before=2, items_after=3)
        # assert (4, 5, [6], 7, 8, 9)
        expected_context = ('04', '05', '06', '07', '08', '09')
        for index, item in enumerate(node_context):
            a = item.name
            b = expected_context[index]
            self.assertEqual(a, b)

if __name__ == '__main__':
    unittest.main()

