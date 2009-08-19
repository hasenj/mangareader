"""
    Author: Hasen il Judy
    License GPL v2

    This module provides the functionality for directory fetching, which is used to make
    the recursive directory listing as non-blocking as possible
"""
import os

# ------ some primitives ----------------

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
        self.path = os.path.join(self.root, self.name)
    def isdir(self):
        if self._isdir is None:
            self._isdir = os.path.isdir(self.path)
        return self._isdir
    def __repr__(self):
        dir = "dir" if self.isdir() else "file"
        return "[%s] %s" % (self.name, dir) 

def root_path(root):
    return os.path.realpath(root)

def dir_entry_list(root):
    root = root_path(root)
    return [DirEntry(root, name) for name in sorted(os.listdir(root))]

class List(object):
    def __init__(self, root, parent=None):
        """
            parent is the list of the parent directory, if any
        """
        root = root_path(root)
        self.root = root
        self.parent = parent
        self.list = dir_entry_list(self.root)
        self.cursor = 0

    def move_cursor(self, direction=1):
        if direction not in (1,-1):
            raise Error("bad direction")
        self.cursor += direction

    def item(self):
        return self.list[self.cursor]

    def inbound(self):
        return self.cursor >= 0 and self.cursor < len(self.list)

    def __repr__(self):
        return "\n".join(
                ["[%s] ---------" % self.root] +
                ["     %s" % entry for entry in self.list])

FORWARD, BACKWARD = 1, -1

class Fetcher(object):
    def __init__(self, root, direction=FORWARD):
        self.root = root_path(root)
        self.list = List(self.root)
        self.direction = direction

    def next(self):
        if not self.list.inbound():
            if not self.list.parent:
                return None
            self.list = self.list.parent
            return self.next() # try again
        if self.list.item().isdir():
            newlist = List(self.list.item().path, self.list)
            self.list.move_cursor(self.direction)
            self.list = newlist
            return self.next() # try again
        # happy case
        ret = self.list.item().path
        self.list.move_cursor(self.direction)
        return ret



