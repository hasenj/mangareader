"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    Qt based graphical user interface for the manga reader
"""

# system imports
import os
import sys

# Qt imports
from PyQt4 import QtGui, QtCore

# Project imports
from mangareader import fstrip, mscroll

# XXX This should go away, right after we implement remembering manga location
if os.name == 'posix':
    test_path = "/home/hasenj/manga/sample/" # TEMP
elif os.name == 'nt':
    test_path = "C:\manga\sample\\" # TEMP

class MainWindow(QtGui.QMainWindow):
    def __init__(self, startdir):
        QtGui.QMainWindow.__init__(self, None)
        self.current_manga_path = startdir
        self.scroller = mscroll.MangaScroller(startdir)
        self.step = 100
        self.big_step = 600
        self.update_notice = False
        self.last_pages_count = 0 # we use this to know to re-render when new pages are loaded!

        open = QtGui.QAction(QtGui.QIcon("art/open.png"), "Open Manga", self)
        open.setShortcut('Ctrl+O')
        open.setStatusTip('Choose a manga to read')
        self.connect(open, QtCore.SIGNAL('triggered()'), self.choose_manga)

        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.timerEvent)
        self.timer.start(80) # number is msec

        # toolbar = self.addToolBar('Manga')
        # toolbar.addAction(open)
        # toolbar.hide()

    def change_manga(self, path):
        # TODO remember where we were last time we were reading this mange
        # and restore to the same place
        self.current_manga_path = path
        self.scroller = mscroll.MangaScroller(path)
        self.repaint()

    def choose_manga(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self, "Choose Manga", os.path.join(self.current_manga_path, '..'))
        if not dir: return
        self.change_manga(unicode(dir))

    def choose_chapter(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self, "Choose Chapter", self.current_manga_path)
        if not dir: return
        self.scroller.change_chapter(unicode(dir))

    def scrollDown(self, step):
        self.scroller.scroll_down(step)
    
    def scrollUp(self, step):
        self.scroller.scroll_up(step)

    def keyPressEvent(self, event):
        key = event.text()
        qt_key = event.key()
        if key == 'j' or qt_key == QtCore.Qt.Key_Down:
            self.scrollDown(self.step)
        if key == 'k' or qt_key == QtCore.Qt.Key_Up:
            self.scrollUp(self.step)
        if key == 'J' or qt_key == QtCore.Qt.Key_PageDown:
            self.scrollDown(self.big_step)
        if key == 'K' or qt_key == QtCore.Qt.Key_PageUp:
            self.scrollUp(self.big_step)
        if key == ' ':
            self.scrollDown(self.big_step)
        if key == 'q' or qt_key == QtCore.Qt.Key_Escape:
            QtGui.QApplication.instance().quit()
        if key == 'o':
            self.choose_manga()
        if key == 'i':
            self.choose_chapter()
        if key == ':':
            print "cmdbar TODO"
        self.repaint()

    def wheelEvent(self, event):
        self.scroller.move_cursor(-event.delta())
        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        try: self.last_pages_count = mscroll.paint_scroller(painter, self.scroller)
        except: print "error in painting"
        painter.end()

    def timerEvent(self):
        if self.scroller.loaded_pages_count() > self.last_pages_count:
            self.repaint()


import sys

def main():
    if len(sys.argv) > 1:
        startdir = sys.argv[1]
    else:
        startdir = test_path
        if not os.path.exists(startdir):
            startdir = ''
    qapp = QtGui.QApplication(sys.argv)
    window = MainWindow(startdir)
    window.resize(1000, 800)
    window.setWindowTitle("Manga Reader")
    window.setWindowIcon(QtGui.QIcon('art/icon.png'))
    window.show()
    sys.exit(qapp.exec_())

if __name__ == '__main__':
    main()

