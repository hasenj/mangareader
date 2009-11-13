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
from PyQt4 import QtGui, QtCore

import thread, time
class ThreadQueue(object):
    """A thread runner that keeps running various things"""
    def __init__(self, name):
        self.name = name
        self.list = []
        self.list_lock = thread.allocate_lock()
        self.thread = thread.start_new_thread(self.run, ())
    def push(self, target):
        with self.list_lock:
            self.list.append(target)
    def run(self):
        """
            This function runs in its own thread!
        """
        while True:
            while len(self.list) == 0:
                time.sleep(0.1) # wait and check back in a while
            with self.list_lock:
                target = self.list.pop(0)
            target()

threads = {}
def queue_thread_target(target, name):
    """
        Put a function in the queue of a named thread.
        Right now we only use the image_loader thread, 
        but it sounds useful to generalize it a bit since it doesn't cost much at all

        @param target: function to run inside thread
        @param name: the name of the thread 
    """
    if not threads.has_key(name):
        threads[name] = ThreadQueue(name)
    threads[name].push(target)
    

class Page(object):
    def __init__(self, path):
        self.path = path
        self.loaded = False
        self.frame = None
        self.scaled = {}
    def load(self):
        """
            Load page in the background, if not already loaded.

            This function basically puts the loader function in a background thread.

            But it's actually not just a thread, it puts the loader in a queue, 
            among with other loader functions that are waiting to be loaded.

            We do this so that images are loaded in order, not randomly (or depending on which is faster to load/smaller in size)

            We'll know when the loader is done because it sets `self.loaded = True`
        """
        if self.loaded: return
        def loader_thread_runner():
            self.frame = fstrip.create_frame(self.path)
            self.loaded = True
        # load image in back ground, keep the order!
        queue_thread_target(loader_thread_runner, "image_loader")
    def height(self):
        if not self.loaded:
            return 10
        return self.frame.rect().height()
    def get_frame(self, width=None):
        if not self.loaded:
            return None
        if width is None:
            return self.frame
        if not width in self.scaled:
            self.scaled[width] = self.frame.scaledToWidth(width, QtCore.Qt.SmoothTransformation)
        return self.scaled[width]


class MangaScroller(object):
    def __init__(self, root):
        self.fetcher = fetch.Fetcher(root)
        self.pages = [Page(i) for i in fetch.fetch_items(self.fetcher, 10, 0.1)]
        if len(self.pages) == 0:
            raise EmptyMangaError
        self.cursor_page = self.pages[0]
        self.cursor_pixel = 0

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
        if self.cursor_page.loaded and self.cursor_pixel > self.cursor_page.height():
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

class EmptyMangaError(Exception): pass
class FetchError(Exception): pass

def paint_scroller(painter, scroller, count=3):
    index = scroller.cursor_index()
    pages = scroller.pages[index:index+count]
    for page in pages:
        page.load() # load page in background, if not already loaded
    frames = [p.get_frame() for p in pages if p.loaded]
    y = -scroller.cursor_pixel
    fstrip.paint_frames(painter, frames, y)

