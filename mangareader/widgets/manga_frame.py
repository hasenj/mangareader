"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    MangaFrame: widget that displays the scrollable manga

    The "frame" here refers to the widget that hosts the manga scroller

    Don't confuse this with the frame concenpt from a film-strip, we call these
    things "pages" here!
"""

# Qt imports
from PyQt4 import QtGui, QtCore

# Project imports
from mangareader.widgets import fstrip, mscroll, scrolling

class MangaFrame(QtGui.QWidget):
    def __init__(self, startdir):
        QtGui.QWidget.__init__(self, None)
        self.scroller = mscroll.MangaScroller(startdir)
        # we use this to know to re-render when new pages are loaded!
        self.last_pages_count = 0 
        self._zoom_factor = 100 # in percent
        self.dirty = True

        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.timerEvent)
        self.timer.start(500) # number is msec


    def scrollDown(self, step=None):
        self.scroller.scroll_down(step)
    
    def scrollUp(self, step=None):
        self.scroller.scroll_up(step)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        view_settings = scrolling.ViewSettings(zoom_level=self.zoom_factor, 
                max_width=painter.viewport().width())
        try: 
            self.last_pages_count = self.scroller.paint_using(painter,
                    view_settings)
        except: 
            raise
            print "error in painting"
        finally:
            painter.end()

    # XXX: this is a hack to paint images than need to wait for loading
    # TODO: replace with an image-loaded event
    def timerEvent(self):
        if self.scroller.dirty:
            self.repaint()

    def change_manga(self, path):
        # TODO remember where we were last time we were reading this mange
        # and restore to the same place
        self.scroller = mscroll.MangaScroller(path)
        self.repaint()

    def change_chapter(self, path):
        self.scroller.change_chapter(path)

    def zoom_in(self, amount):
        self.set_zoom_factor(self.zoom_factor + amount)

    def zoom_out(self, amount):
        self.zoom_in(-amount)

    def reset_zoom(self):
        self.set_zoom_factor(100)

    @property
    def zoom_factor(self): 
        return self._zoom_factor

    def set_zoom_factor(self, value):
        if value < 70: return # don't zoom out too much
        self._zoom_factor = value
        self.dirty = True

