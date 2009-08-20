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
    def __init__(self, root, parent, direction):
        """
            parent is the list of the parent directory, if any
        """
        root = root_path(root)
        self.root = root
        self.parent = parent
        self.list = dir_entry_list(self.root)
        if direction == FORWARD:
            self.cursor = 0
        else:
            self.cursor = len(self.list) - 1


    def set_cursor_end(self):
        #moves cursor to the end of the list
        self.cursor = len(self.list) - 1

    def move_cursor(self, direction):
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
        self.direction = direction
        self.list = List(self.root, None, self.direction)

    def __iter__(self):
        return self

    def next(self):
        if not self.list.inbound():
            if not self.list.parent:
                raise StopIteration
            self.list = self.list.parent
            return self.next() # try again
        if self.list.item().isdir():
            newlist = List(self.list.item().path, self.list, self.direction)
            self.list.move_cursor(self.direction)
            self.list = newlist
            return self.next() # try again
        # happy case
        ret = self.list.item().path
        self.list.move_cursor(self.direction)
        return ret

def create_fetcher(root, start, direction=FORWARD):
    start = os.path.relpath(start, root)
    fetcher = Fetcher(root, direction)
    start = start.replace('\\', '/')
    for part in start.split('/'):
        part_path = os.path.join(fetcher.list.root, part)
        # figure out how to set the cursor
        file_index = sorted(os.listdir(fetcher.list.root)).index(part) 
        if os.path.isdir(part_path):
            fetcher.list.cursor = file_index + direction
            fetcher.list = List(part_path, fetcher.list, direction)
        else:
            fetcher.list.cursor = file_index
    return fetcher

### debug stuff
class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


getch = _GetchUnix()
    

def step(fetcher):
    while True:
        print fetcher.next()
        c = getch()
        if c == 'q':
            break
