"""
    Author: Hasen il Judy
    License: GPL v2

    Manager for scrolling manga. The idea is that the scroller doesn't see the entire directory tree,
    only a small window of it, and has to constantly acquire next/previous pages (images) as user 
    scrolls down or up
"""    

import fstrip
import fetch

class Page(object):
    def __init__(self, path):
        self.path = path
        self.loaded = False
        self.frame = None
    def load(self, width=None):
        self.frame = fstrip.create_frame(self.path, width)
        self.loaded = True
    def height(self):
        if not self.loaded:
            self.load()
        return self.frame.rect().height()
    def get_frame(self):
        if not self.loaded:
            self.load()
        return self.frame

class MangaScroller(object):
    def __init__(self, root):
        self.fetcher = fetch.Fetcher(root)
        self.pages = [Page(i) for i in fetch.fetch_items(self.fetcher, 2, 0.1)]
        if len(self.pages) == 0:
            raise EmptyMangaError
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
        if self.cursor_pixel > self.cursor_page.height():
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
            fetch_result = [Page(i) for i in fetch.fetch_items(self.fetcher, 5, 0.1)]
            self.pages = self.pages[-4:] + fetch_result
        else:
            # add pages to beginning, in reverse
            fetch_result = [Page(i) for i in fetch.fetch_items(self.fetcher, 5, 0.1)][::-1]
            self.pages = fetch_result + self.pages[:4]
            # TODO adjust index cursor? well we don't have the index cursor yet!!

class EmptyMangaError(Exception): pass
class FetchError(Exception): pass

def paint_scroller(painter, scroller, count=3):
    index = scroller.cursor_index()
    pages = scroller.pages[index:index+count]
    frames = [p.get_frame() for p in pages]
    y = -scroller.cursor_pixel
    fstrip.paint_frames(painter, frames, y)

