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
    def height(self):
        if not self.is_loaded():
            return 10
        return self.frame.rect().height()
    def get_frame(self):
        if not self.is_loaded():
            return None
        return self.frame

class PageList(object):
    def __init__(self, root):
        """ `root` is the manga root directory """
        self.fetcher = fetch.Fetcher(root)
        self.pages = [Page(i) for i in fetch.fetch_items(self.fetcher, 10, 0.1)]
        if len(self.pages) == 0:
            raise EmptyMangaError
        self.cursor_page = self.pages[0]
        self.cursor_pixel = 0

    def loaded_pages_count(self):
        sum = 0
        for page in self.pages:
            if page.is_loaded():
                sum +=1
            else:
                break
        return sum

    def change_chapter(self, path):
        self.fetcher = fetch.create_fetcher(self.fetcher.root, path)
        self.pages = [Page(i) for i in fetch.fetch_items(self.fetcher, 10, 0.1)]
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
        current_index = self.pages.index(self.cursor_page)
        self.cursor_pixel += amount
        if amount > 0 and (len(self.pages) - current_index) < 2: #we're getting close to the end and moving forward
            self.fetch_more(fetch.FORWARD)
        if amount < 0 and current_index < 2: #we're moving backward and getting close the beginning
            self.fetch_more(fetch.BACKWARD)
            # this changes current index, so re-calculate it
            current_index = self.pages.index(self.cursor_page)
        if self.cursor_page.is_loaded() and self.cursor_pixel > self.cursor_page.height():
            # move to next page
            next_index = current_index + 1
            if len(self.pages) > next_index:
                # happy case: move cursor page and adjust pixel offset
                prev_height = self.cursor_page.height()
                self.cursor_page = self.pages[next_index]
                self.cursor_pixel -= prev_height
        if self.cursor_pixel < 0:
            # we're jumping up to previous page
            prev_index = current_index - 1
            if prev_index >= 0: #make sure we're not at the first page .. since it has no previous
                # happy case: move cursor page and adjust pixel offset
                self.cursor_page = self.pages[prev_index]
                self.cursor_pixel += self.cursor_page.height()
                
    def fetch_more(self, direction):
        # prepare fetcher
        if not self.pages:
            print "no pages, not sure how to fetch" # DEBUG
            return
        if direction not in (1,-1):
            raise FetchError("invalid direction")
        if direction == fetch.FORWARD:
            last = self.pages[-1].path
        else:
            last = self.pages[0].path
        if (self.fetcher.direction != direction or
            self.fetcher.last != last): # fetcher not in sync with us
            self.fetcher = fetch.create_fetcher(self.fetcher.root, last, direction)
        # fetch from next
        if direction == fetch.FORWARD:
            # add pages to the end
            fetch_result = [Page(i) for i in fetch.fetch_items(self.fetcher, 10, 0.1)]
            self.pages = self.pages[-4:] + fetch_result
        else:
            # add pages to beginning, in reverse
            fetch_result = [Page(i) for i in fetch.fetch_items(self.fetcher, 10, 0.1)][::-1]
            self.pages = fetch_result + self.pages[:4]
            # TODO adjust index cursor? well we don't have the index cursor yet!!

class EmptyPageList(object):
    def __init__(self): pass
    def scroll_up(self, step=0): pass
    def scroll_down(self, step=0): pass
    def move_cursor(self, amount): pass
    def loaded_pages_count(self): return 0

class MangaScroller(object):
    def __init__(self, root):
        try: self.page_list = PageList(root)
        except EmptyMangaError: self.page_list = EmptyPageList()

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
    if scroller.loaded_pages_count() == 0: return
    index = scroller.cursor_index()
    pages = scroller.pages[index:index+count]
    # setup loading parameters
    # TODO: fix, should be viewing parameters? 
    max_width = painter.viewport().width()
    size_kw = { 'max_width': max_width }
    for page in pages:
        page.load(**size_kw) # load page in background, if not already loaded
    frames = [p.get_frame() for p in pages if p.is_loaded()]
    y = -scroller.cursor_pixel
    fstrip.paint_frames(painter, frames, y)
    return len(frames) 

