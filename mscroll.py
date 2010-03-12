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

import fstrip
import fetch
from bgloader import queue_image_loader
from PyQt4 import QtGui, QtCore


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
            print "done loading", self.path
        print "queueing:", self.path
        self.loading = 1
        queue_image_loader(image_loader)
    @property
    def height(self):
        self.load()
        if not self.is_loaded:
            return 800 # some weird default? :/
        return self.frame.rect().height()
    def get_frame(self):
        if not self.is_loaded:
            return None
        return self.frame

class PageList(object):
    def __init__(self, root):
        """ `root` is the manga root directory """
        self.iterator = fetch.iterator(root)
        self.pages = []
        self.reset_window(self.iterator.first_item())
        if len(self.pages) == 0:
            raise EmptyMangaError
        self.index = 0
        self.cursor_pixel = 0

    def loaded_pages_count(self):
        sum = 0
        for page in self.pages:
            if page.is_loaded:
                sum +=1
            else:
                break
        return sum

    @property
    def current_page(self):
        return self.pages[self.index]

    def change_chapter(self, path):
        self.reset_window(path)
        self.cursor_page = self.pages[0]
        self.cursor_pixel = 0

    def cursor_index(self):
        return self.pages.index(self.cursor_page)

    def scroll_down(self, step=100):
        self.move_cursor(step)
    
    def scroll_up(self, step=100):
        self.move_cursor(-step)

    def move_cursor(self, amount):
        # amount is in pixels
        # TODO: user cue for trying to overstep boundaries
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
        # read: if
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
        if steps == 1:
            if self.index + 2 < len(self.pages): # don't need to move window
                self.index += 1
                return True
            newpath = self.iterator.next_item(self.current_page.path)
        elif steps == -1:
            if self.index > 0: # don't need to move window
                self.index -= 1
                return True
            newpath = self.iterator.prev_item(self.current_page.path)
        # if we get here, we needed to move window
        if newpath is None: # we're at the edges!!
            return False # not ok
        self.reset_window(newpath)
        return True # ok

    def reset_window(self, path):
        """resets the view/window around the given file path"""
        list, index = fetch.get_context(self.iterator, path)
        self.pages = [Page(i) for i in list]
        self.index = index

class EmptyPageList(object):
    def __init__(self): pass
    def scroll_up(self, step=0): pass
    def scroll_down(self, step=0): pass
    def move_cursor(self, amount): pass
    def loaded_pages_count(self): return -1

class MangaScroller(object):
    def __init__(self, root):
        try: 
            self.page_list = PageList(root)
        except EmptyMangaError: 
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
                
class EmptyMangaError(Exception): pass
class FetchError(Exception): pass

def paint_scroller(painter, scroller, count=3):
    """
        Render scroller using painter

        @return number of frames rendered (so we know if we need to update)
    """
    if scroller.page_list.loaded_pages_count() < 0: return
    index = scroller.page_list.index
    pages = scroller.page_list.pages[index:index+count] # FIXME: hmm, why is the iteration built into the page list? maybe we should do it as a mapping from filenames to image/page objects
    # setup loading parameters
    # TODO: fix, should be viewing parameters? 
    max_width = painter.viewport().width()
    size_kw = {'max_width': max_width}
    for page in scroller.page_list.pages:
        page.load(**size_kw) # load page in background, if not already loaded
    frames = [p.get_frame() for p in pages if p.is_loaded]
    y = -scroller.page_list.cursor_pixel
    fstrip.paint_frames(painter, frames, y)
    return len(frames) 

