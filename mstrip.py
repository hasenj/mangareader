"""
    Author: Hasen il Judy
    License: GPL v2

    @see fstrip.py
    A manga strip is an "infinite" list of images that can be scrolled vertically up and down.
"""    

import fstrip

class Page(object):
    def __init__(self, path):
        self.path = path
        self.loaded = False
        self.frame = None
    def load(self, width=None):
        self.frame = create_frame(self.path, width)
        self.loaded = True
    def height(self):
        if not self.loaded:
            self.load()
        return self.frame.rect().height()

class MangaStrip(object):
    def __init__(self, root):
        self.fetcher = dirlist.Fetcher(root)
        self.pages = dirlist.fetch_item(self.fetcher, 20, 0.1)
        if len(self.pages[]) == 0:
            raise EmptyMangaError
        self.cursor_page = self.pages[0]
        self.cursor_pixel = 0

    def move_cursor(self, amount):
        # amount is in pixels
        self.cursor_pixel += amount
        if self.cursor_pixel > self.cursor_page.height():
            # move to next page
            next_index = self.pages.index(self.cursor_page)+1
            if len(self.pages) <= next_index:
                # we're at last page, try to fetch more then try again
                self.fetch_more(dirlist.FORWARD)
            if len(self.pages) > next_index:
                # happy case: move cursor page and adjust pixel offset
                prev_height = self.cursor_page.height()
                self.cursor_page = self.pages[next_index]
                self.cursor_pixel -= prev_height
        if self.cursor_pixel < 0:
            # we're jumping up to previous page
            prev_index = self.pages.index(self.cursor_page)-1
            if prev_index < 0:
                #we're at the top, see if we can fetch more from before then try again
                self.fetch_more(dirlist.BACKWARD)
                prev_index = self.pages.index(self.cursor_page)-1
            if prev_index >= 0:
                # happy case: move cursor page and adjust pixel offset
                self.cursor_page = self.pages[prev_index]
                self.cursor_pixel += self.cursor_page.height()
                


    def fetch_more(self, direction):
        # prepare fetcher
        if not self.pages:
            print "no pages, not sure how to fetch" # DEBUG
            return
        if direction not in (1,-1):
            raise Error("invalid direction")
        if direction == dirlist.FORWARD:
            last = self.pages[-1].path
        else:
            last = self.pages[0].path
        if (self.fetcher.direction != direction or
            self.fetcher.last != last): # fetcher not in sync with us
            self.fetcher = dirlist.create_fetcher(self.fetcher.root, last, direction)
        # fetch from next
        if direction == listdir.FORWARD:
            # add pages to the end
            fetch_result = [Page(i) for i in dirlist.fetch_items(self.fetcher, 20, 0.1)]
            if len(self.pages) > 5:
                self.pages = self.pages[-4:]
            self.pages += fetch_result
        else:
            # add pages to beginning, in reverse
            fetch_result = [Page(i) for i in dirlist.fetch_items(self.fetcher, 5, 0.1)][::-1]
            if len(self.pages) > 20:
                self.page = self.pages[:15]
            self.pages = fetch_result + self.pages
            # TODO adjust cursor? well we don't have the cursor yet!!

class EmptyMangaError(Error): pass

