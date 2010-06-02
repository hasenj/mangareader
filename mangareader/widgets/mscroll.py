"""
    Author: Hasen el Judy
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

from mangareader import fetch
from mangareader.widgets import fstrip
from mangareader.tree.walk import step as walk_step
from mangareader.tree.view import context as view_context
from mangareader.bgloader import queue_image_loader
from mangareader.widgets.scrolling import (
            ViewSettings, PageCursor, get_loaded_context)

import os.path

def scaled_image(image, new_width):
    return image.scaledToWidth(new_width, QtCore.Qt.SmoothTransformation)

def get_desired_display_width(image, view_settings=None):    
    if view_settings is None: 
        view_settings = ViewSettings() # use the defaults
    return view_settings.transformed_width(image.width())

class Page(object):
    def __init__(self, path):
        self.path = path
        self.loading = 0  # 0 = not loaded; 1 = loading; 2 = loaded
        self.frame = None # the QImage object
        self.scaled = {}  # a mapping from percentage to a scaled QImage 

    def is_loaded(self): 
        return self.loading == 2

    def load(self):
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
            self.frame = _frame
            self._set_loading_status('done')
            # print "done loading", self.path
        # print "queueing:", self.path
        self._set_loading_status('loading')
        queue_image_loader(image_loader)

    def _set_loading_status(self, status):
        print status
        self.loading = {
                'loading':1,
                'done':2
            }.get(status)

    @property
    def height(self):
        return self.get_height()

    def get_height(self, view_settings=None):
        if not self.is_loaded:
            return None
        return self.get_frame(view_settings).rect().height()
        

    def get_frame(self, view_settings=None):
        if not self.is_loaded:
            return None
        # The view settings determine the size of the image
        # To be efficient, we use a dictionary to cache resized images
        # we use the display width as the key, because that's what we're 
        # _semantically_ interested in when displaying the image
        display_width = get_desired_display_width(self.frame, view_settings)
        if not self.scaled.has_key(display_width):
            self.scaled[display_width] = scaled_image(self.frame, new_width=display_width)
        return self.scaled[display_width]

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
        """ Partial directory view that can be moved around (can't be resized
            yet, though that might be useful)

            This works internally by storing a node list an using an image
            cache to get the image corresponding to a certain node

            @param root: the manga root directory
        """
        self.tree = fetch.DirTree(root)
        self.nodes = []
        self.img_cache = ImageCache()
        first_node = walk_step(self.tree, self.tree.root)
        if first_node is None:
            raise EmptyMangaException
        self._reset_window_to_node(first_node)

    def page_at(self, index):
        """fake list of Page objects"""
        return self.img_cache.get(self.page_path_at(index))

    def page_path_at(self, index):
        return self.nodes[index].path

    def length(self):
        return len(self.nodes)
    __length__ = length

    @property
    def current_page(self):
        return self.page(self.index)

    # TODO: fix renames
    # def change_chapter(self, path):
    def reset_to_path(self, path):
        chapter_node = self.tree.get_node(path)
        first_node = walk_step(self.tree, chapter_node)
        self._reset_window_to_node(first_node)
        self.cursor_pixel = 0

    def _reset_window_to_node(self, node):
        """resets the view/window around the current file path"""
        if node is None: node = self.nodes[self.index]
        list = view_context(self.tree, node)
        new_index = list.index(node)
        self.nodes = list
        # also reset the image cache; this is essential to free up some ram
        path_list = [node.path for node in self.nodes]
        self.img_cache.reset(path_list)
        return new_index

    def reset_window(self, index):
        return self._reset_window_to_node(self.nodes[index])

class EmptyPageList(object):
    def __init__(self): pass
    def length(self): return 0
    __length__ = length
    def reset_window(self, index): pass

class MangaScroller(object):
    def __init__(self, root, view_settings=None):
        try: 
            self.page_list = PageList(root)
            if view_settings is None:
                view_settings = ViewSettings()
            self.view_settings = view_settings
            self.cursor = PageCursor(self.page_list, view_settings)
        except EmptyMangaException: 
            print "Warning: empty manga"
            self.page_list = EmptyPageList()
        # TODO: set to false after painting if there's
        # nothing more to paint
        self.dirty = True 

    def change_chapter(self, path):
        self.page_list.reset_to_path(path)

    def scroll_down(self, step=100):
        self.move_cursor(step)
    
    def scroll_up(self, step=100):
        self.move_cursor(-step)

    def move_cursor(self, amount):
        self.cursor.move(amount)

    # TODO: This will need a big (good :) rewrite!
    # TODO:should mark whether or not some space is left unrendered so that we
    # know when we need to render image when they load
    def paint_using(self, painter, view_settings):
        """
            Render scroller using painter

            @param painter: qt painter
            @returns: number of frames rendered (so we know if we need to update)
        """
        # First, load any unloaded image
        for i in range(self.page_list.length()):
            self.page_list.page_at(i).load() # this is non-blocking
        findex, loaded = get_loaded_context(self.page_list, self.cursor.index)
        index = self.cursor.index - findex
        limit = index + 3 # TEMP
        pages = loaded[index:limit]
        frames = [p.get_frame(view_settings) for p in pages]
        if len(frames) == 0: return 0
        # XXX: this is for transorming the image according to view_settings
        # TODO: refactor
        original_height = pages[0].get_height() 
        new_height = pages[0].get_height(view_settings)
        # TODO factorize this calculation .. it might allow us more flexibility/options
        # such as interpreting the cursor to be in the middle instead of the top
        y = -self.cursor.pixel * new_height / original_height
        fstrip.paint_frames(painter, frames, y)
        return len(frames) 

                
class EmptyMangaException(Exception): pass
class FetchError(Exception): pass

