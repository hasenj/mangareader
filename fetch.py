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
            raise InvalidEntryName()

    def get_entry(self, name):
        """Get the entry with the given name"""
        return ls[get_entry_index(name)]

    def __repr__(self):
        type = "dir " if self.isdir() else "file"
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

def get_first_item(entry): if len(entry.ls) return entry.ls[0] else return None
def get_last_item(entry): if len(entry.ls) return entry.ls[-1] else return None

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
class InvalidEntryName(Exception): pass

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

    def _next_item(self, path, get_next_item=get_next_item, get_first_item=get_first_item):
        """Get the next item after the one given by `path`
        
            This is a private function, used to abstract away the differences between getting
            the next and the previous items
        """
        path = rel_path(path, root_path) # normalize to relative path
        parent, name = os.path.split(path)
        entry = get_entry(parent) # entry that contains path

        next = get_next_item(entry, name)
        while next is None: # we're on the edge?
            # TODO (interrupted half way through)
            parent, name = os.path.split(parent) # try our sibling
            entry = get_entry(parent)
            next = get_first_item(entry)
            


    def get_entry(self, path):
        """Get the entry for the given path, and use a cache"""
        if self.cache.has_key(path):
            return self.cache.get(path)
        # first time we see this, let's find it and remember it
        entry = self.dir_entry # the root entry
        for part in path.split('/'):
            entry = entry.get_entry(part)
        self.cache.set(path, entry)
        return entry



