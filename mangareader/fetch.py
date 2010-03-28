"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    This module provides the functionality for recursively iterating directory content
    in an effecient way that doesn't block when the directory is huge and messy

    Terminology notes:

        - Sometimes things can be confusing: are we passing a path or a directory node? so:
            item: means the file path
            node: means the DirNode object

    TODO: getting the parent of a DirNode in the iterator is a confusing operation: make a method for it
"""

import os
from time import time as now
from mangareader.tree.walk import step as walk_step


# ------ some primitives ----------------

def real_path(root):
    return os.path.realpath(root)

def default_sort(list): # TODO consider heuristic sorting
    return sorted(list)

def is_image(filepath):
    """filter for dir listing"""
    _, ext = os.path.splitext(filepath)
    return ext.lower() in ('.png', '.jpg', '.jpeg', '.gif')
        
def dir_node_list(directory, sort_func=default_sort, filterer=is_image):
    directory = real_path(directory)
    listing = [DirNode(os.path.join(directory, name))
            for name in sort_func(os.listdir(directory))] 
    listing = [item for item in listing if item.isdir or filterer(item.path)]
    return listing

class DirNode(object):
    def __init__(self, path):
        path = real_path(path)
        self.path = path
        self.name = os.path.basename(path)
        self._isdir = None
        self._ls = None
        self._ls_map = None

    @property
    def isdir(self): 
        if self._isdir is None: # lazy, don't hit the disk unless we need to
            self._isdir = os.path.isdir(self.path)
        return self._isdir

    @property
    def isfile(self):
        return not self.isdir

    @property
    def ls(self):
        if self.isdir and self._ls is None: # lazy, ditto
            self._ls = dir_node_list(self.path, filterer=is_image)
        return self._ls

    @property
    def ls_map(self):
        if self._ls_map is None: 
            # maps a file's basename to its node
            self._ls_map = dict( ((item.name, index) for index, item in enumerate(self.ls)) )
        return self._ls_map

    def get_node_index(self, name):
        try:
            return self.ls_map[name]
        except:
            print self.ls_map
            raise InvalidEntryName(self, name)

    def get_node(self, name):
        """Get the child node with the given name"""
        return self.ls[self.get_node_index(name)]

    def __repr__(self):
        type = "dir " if self.isdir else "file"
        return "[%s] %s" % (type, self.name) 

FORWARD, BACKWARD = 1, -1

class NotSubdirectoryError(Exception): pass

class InvalidEntryName(Exception):
    def __init__(self, node, name):
        print "asked for %s from %s" % (name, node.path)

# ---------------- iteration instead of fetching ---- (test)

class DirTree(object):
    """The directory tree is used for the root directory of the manga"""
    def __init__(self, root_path):
        """@param root_path: the directory we walk inside"""
        self.root_path = real_path(root_path)
        self.root = DirNode(self.root_path)
        self.cache = {} # maps paths to entries

    def next_item(self, path):
        node = self.get_node(path)
        return walk_step(self, node, 'next')

    def prev_item(self, path):
        node = self.get_node(path)
        return walk_step(self, node, 'prev')

    def relpath(self, path):
        if os.path.isabs(path):
            return os.path.relpath(path, self.root_path)
        return path

    def get_node(self, path):
        """Get the node for the given path, and use a cache; path must be a relative path"""
        if self.cache.has_key(path):
            return self.cache.get(path)
        # first time we see this, let's find it and remember it
        node = self.root # the root entry
        for part in path_parts(path):
            node = node.get_node(part)
        self.cache[path] = node
        return node

    def parent(self, node):
        """Get the parent for the given node"""
        path = node.path
        path = self.relpath(path)
        parent, name = os.path.split(path)
        return self.get_node(parent)

def path_parts(path):
    path.replace('\\', '/')
    parts = path.split('/')
    if parts and parts[0] == '': parts = parts[1:]
    if parts and parts[-1] == '': parts = parts[:-1]
    return parts

### debug stuff
if os.name == 'posix':                                       
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
        
    def step_test(tree):
        node = walk_step(tree, tree.root)
        prev_node = node
        while True:
            if node is None:
                node = prev_node
            else:
                prev_node = node
            print node.path
            c = getch()
            if c == 'q':
                break
            elif c == 'j': node = walk_step(tree, node, 'next')
            elif c == 'k': node = walk_step(tree, node, 'prev')
            elif '0' <= c <= '9': 
                nth_node = tree.root.ls[int(c)]
                node = walk_step(tree, nth_node) # start from the nth directory (simulate jumping to a chapter)
            if node is None:
                print "|---- end ----|"
                continue
        print "broke out of loop!"

debug = True
if debug and __name__ == '__main__':
    tree = DirTree('/home/hasenj/manga')
    # it = DirListIterator('/home/hasenj/manga/sample')
    step_test(tree)

