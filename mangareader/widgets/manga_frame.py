"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    widget that displays the scrollable manga
"""

# Qt imports
from PyQt4 import QtGui, QtCore

# Project imports
from mangareader.widgets import fstrip, mscroll

class MangaFrame(QtGui.QWidget):
    def __init__(self, startdir):
        QtGui.QWidget.__init__(self, None)
        self.scroller = mscroll.MangaScroller(startdir)
        self.last_pages_count = 0 # we use this to know to re-render when new pages are loaded!

        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.timerEvent)
        self.timer.start(80) # number is msec

    def scrollDown(self, step=None):
        self.scroller.scroll_down(step)
    
    def scrollUp(self, step=None):
        self.scroller.scroll_up(step)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        try: self.last_pages_count = mscroll.paint_scroller(painter, self.scroller)
        except: print "error in painting"
        painter.end()

    def timerEvent(self):
        if self.scroller.loaded_pages_count() > self.last_pages_count:
            self.repaint()

    def change_manga(self, path):
        # TODO remember where we were last time we were reading this mange
        # and restore to the same place
        self.scroller = mscroll.MangaScroller(path)
        self.repaint()

    def change_chapter(self, path):
        self.scroller.change_chapter(path)

