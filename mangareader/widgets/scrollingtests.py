"""
    Author: Hasen el Judy
    License: GPL v2

    unit tests for scrolling infrastructure
"""

import unittest
from mangareader.widgets.scrolling import HeightList

class TestHeightList(unittest.TestCase):
    def setUp(self):
        pass

    def testBasics(self):
        h = HeightList([10, 5, 10])
        self.assertEqual(h.max(), 24)
        g = h.local_to_global(0, 7)
        i, p = h.global_to_local(7)
        self.assertEqual( (i,p), (0,7) )
        self.assertEqual(g, 7)
        g = h.local_to_global(1, 2)
        self.assertEqual(g, 12)
        i, p = h.global_to_local(12)
        self.assertEqual( (i,p), (1,2) )

        
        
if __name__ == '__main__':
    unittest.main()
