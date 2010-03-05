"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    This module provides the functionality for directory fetching, which is used to make
    the recursive directory listing as non-blocking as possible
"""
import os

# ------ some primitives ----------------

def real_path(root):
    return os.path.realpath(root)

def dir_entry_list(root):
    root = real_path(root)
    return [DirEntry(os.path.join(root, name))
            for name in sorted(os.listdir(root))] # TODO consider heuristic sorting

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

def fetch_items(fetcher, count, time):
    """Fetch {{count}} items from fetcher, but stop if you're taking more than {{time}} seconds"""
    start = now()
    result = []
    while len(result) < count and (now() - start) < time:
        try: result.append(fetcher.next())
        except StopIteration: break
    return result

class NotSubdirectoryError(Exception): pass

class InvalidEntryName(Exception):
    def __init__(self, entry, name):
        print "asked for %s from %s" % (name, entry.path)

# ---------------- iteration instead of fetching ---- (test)

class DirListIterator(object):
    """ The iterator can start on a file path and walk through the 
        directory tree looking for the next or previous file that matches
        a certain type (images by default).
    """
    def __init__(self, root_path):
        """ @param root_path: the directory we walk inside """
        self.root_path = real_path(root_path)
        self.dir_entry = DirEntry(self.root_path)
        self.cache = {} # maps paths to entries

    def _get_first_item_recursive(self, entry, get_first_item=get_first_item):
        if not entry.isdir: return entry
        first = get_first_item(entry)
        if first is None: return None
        return self._get_first_item_recursive(first, get_first_item=get_first_item)

    def first_item(self):
        return self._get_first_item_recursive(self.dir_entry)

    def last_item(self):
        return self._get_first_item_recursive(self.dir_entry, get_first_item=get_last_item)

    def first_item_in(self, path):
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

            @returns: the DirEntry for the item (we probably just want the path from it)
        """
        def get_most_next_item(entry):
            """ My algorithm to walk the tree starting from the DirEntry `entry`
                and get the first non-directory entry
            """
        path = self.relpath(path) # normalize to relative path
        parent, name = os.path.split(path)
        entry = get_next_item(self.get_entry(parent), name)

        while True:
            if entry is not None:
                # This should work whether entry is a dir or a file
                result = self._get_first_item_recursive(entry, get_first_item=get_first_item) 
                if result is not None:
                    return result
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
            print item.path
            c = getch()
            if c == 'q':
                break
            if item is None: continue
            if c == 'j': item = iterator.next_item(item.path)
            if c == 'k': item = iterator.prev_item(item.path)
            if '0' <= c <= '9': item = iterator.first_item_in(iterator.dir_entry.ls[int(c)].path)

debug = True
if debug and __name__ == '__main__':
    it = DirListIterator('/home/hasenj/manga/sample')
    step_test(it)
