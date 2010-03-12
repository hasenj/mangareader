"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    This module provides the functionality for recursively iterating directory content
    in an effecient way that doesn't block when the directory is huge and messy
"""

import os

# ------ some primitives ----------------

def real_path(root):
    return os.path.realpath(root)

def default_sort(list): # TODO consider heuristic sorting
    return sorted(list)

def is_image(filepath):
    """filter for dir listing"""
    _, ext = os.path.splitext(filepath)
    return ext.lower() in ('.png', '.jpg', '.jpeg', '.gif')
        
def dir_entry_list(root, sort_func=default_sort, filterer=is_image):
    root = real_path(root)
    listing = [DirEntry(os.path.join(root, name))
            for name in sort_func(os.listdir(root))] 
    listing = [item for item in listing if item.isdir or filterer(item.path)]
    return listing

class DirEntry(object):
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
    def ls(self):
        if self.isdir and self._ls is None: # lazy, don't hit the disk unless we need to
            self._ls = dir_entry_list(self.path)
        return self._ls

    @property
    def ls_map(self):
        if self._ls_map is None: 
            self._ls_map = dict( ((item.name, index) for index, item in enumerate(self.ls)) )
        return self._ls_map

    def get_entry_index(self, name):
        try:
            return self.ls_map[name]
        except:
            print self.ls_map
            raise InvalidEntryName(self, name)

    def get_entry(self, name):
        """Get the entry with the given name"""
        return self.ls[self.get_entry_index(name)]

    def __repr__(self):
        type = "dir " if self.isdir else "file"
        return "[%s] %s" % (type, self.name) 

def get_offset_item(entry, name, offset):
    """Get an item that's `offset` steps apart from the item with `name` in the DirEntry `entry`"""
    index = entry.get_entry_index(name)
    ls = entry.ls
    if 0 <= index+offset < len(ls):
        return ls[index+offset]
    else:
        return None

# kind of low level functions ..
def get_next_item(entry, name): return get_offset_item(entry, name, 1)        
def get_prev_item(entry, name): return get_offset_item(entry, name, -1)        

def get_first_item(entry): 
    if len(entry.ls): return entry.ls[0] 
    else: return None

def get_last_item(entry): 
    if len(entry.ls): return entry.ls[-1] 
    else: return None

FORWARD, BACKWARD = 1, -1

from time import time as now

class NotSubdirectoryError(Exception): pass

class InvalidEntryName(Exception):
    def __init__(self, entry, name):
        print "asked for %s from %s" % (name, entry.path)

# ---------------- iteration instead of fetching ---- (test)

class DirListIterator(object):
    """ The iterator can start on a file path and walk through the 
        directory tree looking for the next or previous file that matches
        a certain type (images by default).

        Unlike a C++/Java notion of an iterator, this one doesn't actually
        remember what the last item was; you have to keep supplying it.
    """
    def __init__(self, root_path):
        """ @param root_path: the directory we walk inside """
        self.root_path = real_path(root_path)
        self.dir_entry = DirEntry(self.root_path)
        self.cache = {} # maps paths to entries

    def _get_first_item_recursive(self, entry, get_first_item=get_first_item):
        if not entry.isdir: return entry.path # base case
        first = get_first_item(entry)
        if first is None: return None
        return self._get_first_item_recursive(first, get_first_item=get_first_item)

    def first_item(self):
        """returns the path to the first item (first leaf node(file)) in the directory tree, recursively"""
        return self._get_first_item_recursive(self.dir_entry)

    def last_item(self):
        """returns the path to the last item (last leaf node(file)) in the directory tree, recursively"""
        return self._get_first_item_recursive(self.dir_entry, get_first_item=get_last_item)

    def first_item_in(self, path):
        """returns the path to the first item inside a certain subdirectory"""
        print "getting first in ", path
        path = self.relpath(path)
        item = self._get_first_item_recursive(self.get_entry(path))
        if item is None: # means this directory was empty!
            item = self.next_item(path)
        return item

    def next_item(self, path):
        return self._next_item(path)

    def prev_item(self, path):
        return self._next_item(path, get_next_item=get_prev_item, get_first_item=get_last_item)

    def relpath(self, path):
        if os.path.isabs(path):
            return os.path.relpath(path, self.root_path)
        return path

    def _next_item(self, path, get_next_item=get_next_item, get_first_item=get_first_item):
        """Get the next item after the one given by `path`
        
            This is a private function, used to abstract away the differences between getting
            the next and the previous items

            @returns: the absolute path of the item
        """
        path = self.relpath(path) # normalize to relative path
        parent, name = os.path.split(path)
        entry = get_next_item(self.get_entry(parent), name)

        while True:
            if entry is not None:
                # This should work whether entry is a dir or a file
                result = self._get_first_item_recursive(entry, get_first_item=get_first_item) 
                if result is not None:
                    return result # here we return .. with the path
                path = self.relpath(entry.path) # hmm, this is kinda bad, having to remember to call relpath everytime we alter `path`
                parent, name = os.path.split(path) # go up a level and try our sibling
                entry = self.get_entry(parent)
                entry = get_next_item(entry, name) # parent's sibling
            if entry is None:
                if parent in ('', '/'): # we're at the very end, nothing more!!
                    return None
                parent, name = os.path.split(parent) # this level is done, go up
                entry = get_next_item(self.get_entry(parent), name)

    def get_entry(self, path):
        """Get the entry for the given path, and use a cache; path must be a relative path"""
        if self.cache.has_key(path):
            return self.cache.get(path)
        # first time we see this, let's find it and remember it
        entry = self.dir_entry # the root entry
        for part in path_parts(path):
            entry = entry.get_entry(part)
        self.cache[path] = entry
        return entry

def path_parts(path):
    path.replace('\\', '/')
    parts = path.split('/')
    if parts and parts[0] == '': parts = parts[1:]
    if parts and parts[-1] == '': parts = parts[:-1]
    return parts

def _get_next_x_items(iterator, item, count, attr='next_item'):
    """ get next (or previous) x items
        @param count: how many items to get. Note: not guaranteed to return exactly `count` items (e.g. if we're near the end/beginning of the list)
        @param filter: a function that takes a file path and return a boolean specifying if we should accept or reject this file
    """
    res = []
    get_func = getattr(iterator, attr)
    for x in range(count):
        item = get_func(item)
        if item is None: break # nothing more to get
        res.append(item)
    return res

# Helper functions for getting the context around an item
def get_next_x_items(iterator, item, count): return _get_next_x_items(iterator, item, count)
def get_prev_x_items(iterator, item, count): return _get_next_x_items(iterator, item, count, attr='prev_item')

def get_context(iterator, item=None, prev_count=4, next_count=12):
    """Get the context around an a file -- used for making a partial view of the recursive file list
    @param iterator: object for iterating the directory tree
    @param item: the path for the file we want the context around
    @param prev_count: how many items before?
    @param next_count: how many items after?
    @returns: (list, index) where list is a partial file list and index is the index of the item in the list
    """
    if item is None: item = iterator.first_item()
    if item is None: return [], 0 # though 0 doesn't really make sense, but calling code should handle empty list gracefully
    prev = get_prev_x_items(iterator, item, prev_count)
    next = get_next_x_items(iterator, item, next_count)
    return prev + [item] + next, len(prev)

iterator = DirListIterator # a short and sweet alias

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
        
    def step_test(iterator):
        item = iterator.first_item()
        while True:
            print item
            c = getch()
            if c == 'q':
                break
            if item is None: continue
            if c == 'j': item = iterator.next_item(item)
            if c == 'k': item = iterator.prev_item(item)
            if '0' <= c <= '9': item = iterator.first_item_in(iterator.dir_entry.ls[int(c)].path) # start from the nth directory (simulate jumping to a chapter)

debug = True
if debug and __name__ == '__main__':
    it = DirListIterator('/home/hasenj/manga/sample')
    step_test(it)

