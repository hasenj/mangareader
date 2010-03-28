"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    Manager for scrolling manga. The idea is that the scroller doesn't see the entire directory tree,
    only a small window of it, and has to constantly acquire (fetch) next/previous pages (images) as 
    the user scrolls down or up

    fetch.py handles the fetching process.

    fstrip.py is a static film strip mechanism: you have a bunch of images, you draw them 
        vertically on top of each other, starting at some vertical offset.

    mscroller.py uses the fetcher and the film strip to dynamically fetch and move the vertical
        list of images as the user scrolls up/down
"""    

import itertools

from PyQt4 import QtGui, QtCore

from mangareader import fetch, fstrip
from mangareader.tree.walk import step as walk_step
from mangareader.tree.view import context as view_context
from mangareader.bgloader import queue_image_loader

import os.path

class Page(object):
    def __init__(self, path):
        self.path = path
        self.loading = 0 # 0 = not loaded; 1 = loading; 2 = loaded
        self.frame = None
        self.scaled = {}

    @property
    def is_loaded(self): 
        return self.loading == 2

    def load(self, max_width=None):
        """
            Load page in the background, if not already loaded.

            This function basically puts the loader function in a background thread.

            But it's actually not just a thread, it puts the loader in a queue, 
            among with other loader functions that are waiting to be loaded.

            We do this so that images are loaded in order, not randomly (or depending on which is faster to load/smaller in size)

            We'll know when the loader is done because it sets `self.loading = 2`
        """
        if self.loading > 0: return
        def image_loader(): # this will run in a background thread
            _frame = fstrip.create_frame(self.path)
            if max_width and _frame.rect().width() > max_width:
                _frame = _frame.scaledToWidth(max_width, QtCore.Qt.SmoothTransformation)
            self.frame = _frame
            self.loading = 2
            # print "done loading", self.path
        # print "queueing:", self.path
        self.loading = 1
        queue_image_loader(image_loader)
    @property
    def height(self):
        if not self.is_loaded:
            return 800 # some weird default? :/
        return self.frame.rect().height()
    def get_frame(self):
        if not self.is_loaded:
            return None
        return self.frame

class ImageCache(object):
    """A mapping from image path to page object, with caching

        usage: first, initialize a cache
               - you can add paths to the cache, and the images will be loaded
               - you can remove paths (and the images will be removed)
               - you can reset the cache with a list of paths, any loaded image not 
                 in the new list will be removed, and new image will be loaded

        TODO consider using the image width as an additional key

        @note: the paths we deal with should always be absolute paths
    """
    def __init__(self):
        self.map = {}

    def get(self, path):
        return self.map[path]

    def contains(self, path):
        return self.map.has_key(path)

    def add(self, path):
        if self.contains(path): return
        page = Page(path)
        self.map[path] = page
        # page.load(max_width) # don't load yet ..
    def remove(self, path):
        del self.map[path]
    def reset(self, path_list):
        """remove paths not in path_list, load pages not already loaded"""
        old_paths = set(self.map.keys()) - set(path_list)
        for path in old_paths:
            self.remove(path)
        for path in path_list:
            self.add(path)

class PageList(object):
    def __init__(self, root):
        """ `root` is the manga root directory """
        self.tree = fetch.DirTree(root)
        self.nodes = []
        self.img_cache = ImageCache()
        first_node = walk_step(self.tree, self.tree.root)
        self.reset_window(first_node)
        if len(self.nodes) == 0:
            raise EmptyMangaException
        self.index = 0
        self.cursor_pixel = 0

    def loaded_pages_count(self):
        sum = 0
        for page in self.as_list():
            if page.is_loaded:
                sum +=1
        return sum

    def page(self, index):
        """fake list of Page objects"""
        return self.img_cache.get(self.page_path(index))

    def page_path(self, index):
        return self.nodes[index].path

    def as_list(self):
        """get a list of the pages we have"""
        return map(self.page, range(len(self.nodes)))

    @property
    def current_page(self):
        return self.page(self.index)

    def change_chapter(self, path):
        chapter_node = self.tree.get_node(path)
        first_node = walk_step(self.tree, chapter_node)
        self.reset_window(first_node)
        self.cursor_pixel = 0

    def scroll_down(self, step=100):
        self.move_cursor(step)
    
    def scroll_up(self, step=100):
        self.move_cursor(-step)

    def move_cursor(self, amount):
        # amount is in pixels
        self.cursor_pixel += amount
        # read: if
        while self.cursor_pixel < 0: # we're moving backwards
            ok = self.move_index(-1) # move to previous page
            if not ok: 
                self.cursor_pixel = 0
                break
            if not self.current_page.is_loaded:  # don't proceed if page is not loaded (we don't know its height)
                print "Breaking out -- page is not loaded yet!! (backward)"
                self.index += 1 # restore index
                self.cursor_pixel = 0
                break # really?
            self.cursor_pixel += self.current_page.height
        # read: if (elif?)
        while self.cursor_pixel > self.current_page.height:
            if not self.current_page.is_loaded:  # don't proceed if page is not loaded (we don't know its height)
                print "Breaking out -- page is not loaded yet!! (forward)"
                # restore index to previous page
                self.index -= 1
                self.cursor_pixel = self.current_page.height - 1
                break # really?
            new_pixel = self.cursor_pixel - self.current_page.height
            ok = self.move_index(1)
            if not ok:
                self.cursor_pixel = self.current_page.height
                break
            self.cursor_pixel = new_pixel
                
    def move_index(self, steps):
        """ move the index `steps` steps, and optionally readjusts the context/window
            @returns: whether or not we overstepped our boundaries
        """
        if steps not in (1, -1):
            raise Exception("stepping move than one step is not supported")
        if self.index < 2 or self.index + 2 > len(self.nodes):
            self.reset_window()
        new_index = self.index + steps
        if new_index not in range(0, len(self.nodes)):
            return False
        self.index = new_index
        return True # ok

    def reset_window(self, node=None):
        """resets the view/window around the current file path"""
        if node is None: node = self.nodes[self.index]
        list = view_context(self.tree, node)
        index = list.index(node)
        self.nodes = list
        self.index = index
        path_list = [node.path for node in self.nodes]
        self.img_cache.reset(path_list)

class EmptyPageList(object):
    def __init__(self):
        self.nodes = []
    def scroll_up(self, step=0): pass
    def scroll_down(self, step=0): pass
    def move_cursor(self, amount): pass
    def loaded_pages_count(self): return -1
    def as_list(self): return []

class MangaScroller(object):
    def __init__(self, root):
        try: 
            self.page_list = PageList(root)
        except EmptyMangaException: 
            print "Warning: empty manga"
            self.page_list = EmptyPageList()

    def change_chapter(self, path):
        self.page_list.change_chapter(path)

    def scroll_down(self, step=100):
        self.page_list.scroll_down(step)
    
    def scroll_up(self, step=100):
        self.page_list.scroll_up(step)

    def move_cursor(self, amount):
        self.page_list.move_cursor(amount)

    def loaded_pages_count(self):
        return self.page_list.loaded_pages_count()
                
class EmptyMangaException(Exception): pass
class FetchError(Exception): pass

def paint_scroller(painter, scroller, count=3):
    """
        Render scroller using painter

        @return number of frames rendered (so we know if we need to update)
    """
    # First, load any unloaded image:
    #   setup loading parameters
    #   TODO: fix, should be viewing parameters? 
    max_width = painter.viewport().width()
    for page in scroller.page_list.as_list():
        page.load(max_width=max_width) # load page in background, if not already loaded
    if scroller.page_list.loaded_pages_count() <= 0: return
    index = scroller.page_list.index
    pages = scroller.page_list.as_list()[index:index+count] # FIXME: hmm, why is the iteration built into the page list? maybe we should do it as a mapping from filenames to image/page objects
    frames = [p.get_frame() for p in pages if p.is_loaded]
    y = -scroller.page_list.cursor_pixel
    fstrip.paint_frames(painter, frames, y)
    return len(frames) 

