"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    This module provides the functionality for recursively iterating directory content
    in an effecient way that doesn't block when the directory is huge and messy

    Terminology notes:

        - Sometimes things can be confusing: are we passing a path or a directory entry? so:
            item: means the file path
            entry: means the DirEntry object

    TODO: getting the parent of a DirEntry in the iterator is a confusing operation: make a method for it
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

def _get_offset_entry(parent_entry, child_entry, offset):
    """Get an entry that's `offset` steps apart from the item with `name` in the DirEntry `entry`"""
    name = child_entry.name
    index = parent_entry.get_entry_index(name)
    ls = parent_entry.ls
    if 0 <= index+offset < len(ls):
        return ls[index+offset]
    else:
        return None

# kind of low level functions ..
def get_next_entry(parent_entry, child_entry):
    return _get_offset_entry(parent_entry, child_entry, 1)        
def get_prev_entry(parent_entry, child_entry):
    return _get_offset_entry(parent_entry, child_entry, -1)        

def get_first_entry(entry): 
    if len(entry.ls): return entry.ls[0]
    else: return None

def get_last_entry(entry): 
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

    def _get_first_item_recursive(self, entry, get_first_entry=get_first_entry, next_item='next_item'):
        """Recursively get the first item, if none, get the best next item (first leaf node)
            @param entry: the directory where we want to get the first item inside it
            @param get_first_entry: the function for getting the first entry (can be set to get_last_entry for opposite effect)
            @param next_item: name of the attribute for the next_item (could be set to 'prev_item' for opposite effect)
            @note: if you set get_first_entry to get_last_entry, then you also have to set next_item to 'prev_item'
            @return: path to the item
        """
        if not entry.isdir: 
            return entry.path # base case, at the top, to allow passing a file as well!
        else: # entry.isdir
            first = get_first_entry(entry)
            if first is None:
                return getattr(self, next_item)(entry.path)
            else:
                return self._get_first_item_recursive(first, get_first_entry, next_item)

    def first_item(self):
        """returns the path to the first item (first leaf node(file)) in the directory tree, recursively"""
        return self._get_first_item_recursive(self.dir_entry)

    def last_item(self):
        """returns the path to the last item (last leaf node(file)) in the directory tree, recursively"""
        return self._get_first_item_recursive(self.dir_entry, get_first_entry=get_last_entry, next_item='prev_item')

    def first_item_in(self, path):
        """returns the path to the first item inside a certain subdirectory"""
        # print "getting first in ", path
        path = self.relpath(path)
        item = self._get_first_item_recursive(self.get_entry(path))
        if item is None: # means this directory was empty!
            item = self.next_item(path)
        return item

    def next_item(self, path):
        return self._next_item(path)

    def prev_item(self, path):
        return self._next_item(path, get_next_entry=get_prev_entry, get_first_entry=get_last_entry)

    def relpath(self, path):
        if os.path.isabs(path):
            return os.path.relpath(path, self.root_path)
        return path

    def _next_item(self, path, get_next_entry=get_next_entry, get_first_entry=get_first_entry):
        """Get the next item after the one given by `path`
        
            This is a private function, used to abstract away the differences between getting
            the next and the previous items

            @returns: the absolute path of the item
        """
        # print "iteration:", path
        path = self.relpath(path) # normalize to relative path
        # print "relpath:", path
        entry = self.get_entry(path)
        parent = self.get_parent_entry(entry)
        entry = self.get_sibling_entry(entry, get_next_entry=get_next_entry)
        # if entry: print "sibling is", entry.path

        while True:
            if entry is not None:
                # This should work whether entry is a dir or a file
                result = self._get_first_item_recursive(entry, get_first_entry=get_first_entry) 
                if result is not None:
                    return result # here we return .. with the path
                path = self.relpath(entry.path) # hmm, this is kinda bad, having to remember to call relpath everytime we alter `path`
                # go up a level and try our sibling
                entry = self.get_sibling_entry(parent, get_next_entry=get_next_entry)
            if entry is None:
                if parent.path in ('', '/', '.'): # we're at the very end, nothing more!!
                    return None
                # this level is done, go up
                entry = self.get_sibling_entry(parent, get_next_entry=get_next_entry)

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

    def get_parent_entry(self, entry):
        """Get the parent entry for this entry within the root dir_entry"""
        path = entry.path
        path = self.relpath(path)
        parent, name = os.path.split(path)
        return self.get_entry(parent)

    def get_sibling_entry(self, entry, get_next_entry=get_next_entry):
        """Finds the sibling for the entry in the directory tree
        @param get_next_entry: the function for getting the sibling (used so the same function can get next/prev sibling
        """
        parent = self.get_parent_entry(entry)
        sibling = get_next_entry(parent, entry)
        return sibling

def path_parts(path):
    path.replace('\\', '/')
    parts = path.split('/')
    if parts and parts[0] == '': parts = parts[1:]
    if parts and parts[-1] == '': parts = parts[:-1]
    return parts

def _get_next_x_items(iterator, item, count, next_item='next_item'):
    """ get next (or previous) x items
        @param count: how many items to get. Note: not guaranteed to return exactly `count` items (e.g. if we're near the end/beginning of the list)
        @param filter: a function that takes a file path and return a boolean specifying if we should accept or reject this file
    """
    res = []
    for x in range(count):
        item = getattr(iterator, next_item)(item)
        if item is None: break # nothing more to get
        res.append(item)
    return res

# Helper functions for getting the context around an item
def get_next_x_items(iterator, item, count): return _get_next_x_items(iterator, item, count)
def get_prev_x_items(iterator, item, count): return _get_next_x_items(iterator, item, count, next_item='prev_item')

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
        print "broke out of loop!"

debug = True
if debug and __name__ == '__main__':
    it = DirListIterator('/home/hasenj/manga')
    # it = DirListIterator('/home/hasenj/manga/sample')
    step_test(it)


