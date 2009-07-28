"""
    Author: Hasen il Judy
    License GPL v2

    This module provides the functionality for non-blocking directory listing
"""
import os

def stack_top(stack):
    """Get the top (last item) of the stack """
    return stack[-1]

def stack_pop(stack):
    """Remove the top (last) item from the list/stack"""
    return stack[:-1]

class DirEntry(object):
    def __init__(self, root, name):
        self.root = root
        self.name = name
        self._isdir = None
    def path(self):
        return os.path.join(self.root, self.name)
    def isdir(self):
        if self._isdir is None:
            self._isdir = os.path.isdir(self.path())
        return self._isdir
    def __repr__(self):
        dir = "dir" if self.isdir() else "file"
        return "[%s] %s" % (self.name, dir) 


def dir_entry_list(root):
    root = os.path.realpath(root)
    return [DirEntry(root, name) for name in os.listdir(root)]

class DirList(object):
    def __init__(self, root, parent=None):
        """
            parent is the listring of the parent directory, if any
        """
        root = os.path.realpath(root)
        self.root = root
        self.parent = parent
        self.list = dir_entry_list(self.root)

    def __repr__(self):
        return "\n".join(
                ["[%s] ---------" % self.root] +
                ["     %s" % entry for entry in self.list])


            

