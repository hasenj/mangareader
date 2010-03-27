"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    Get a view/window of the context around a file

"""

from mangareader.tree.walk import step

def context(tree, node, items_before=3, items_after=10):
    """Get the context around node from the given tree
    @param tree: The root directory where search within. must implement ITree
    @param node: the file we want the context around. must implement INode, and must be a file (leaf)
    @param items_before: how many previous items to fetch
    @param items_after: how many next items to fetch
    """
    if not node.isfile: raise ValueError("node must be a file")
    prev, next = [], []
    def get_prev_next(tree, node, steps, dir='next'):
        result = []
        node = step(tree, node, dir)
        for i in range(steps):
            if node is None: break
            result.append(node)
            node = step(tree, node, dir)
        return result
    prev = get_prev_next(tree, node, items_before, 'prev')[::-1]
    next = get_prev_next(tree, node, items_after, 'next')
    return prev + [node] + next
        


