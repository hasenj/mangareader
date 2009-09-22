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
import fstrip
import mscroll

if os.name == 'posix':
    test_image = "/home/hasenj/manga/skipbeat17/01.png"
    test_path = "/home/hasenj/manga/sample/"
elif os.name == 'nt':
    test_path = "C:\manga\sample\\"

def load_frames(path):
    for file in sorted(os.listdir(path)):
        _, ext = os.path.splitext(file)
        if ext in ['.png', '.jpg', '.jpeg']:
            image_path = os.path.join(path, file)
            yield fstrip.create_frame(image_path, 800)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.scroller = mscroll.MangaScroller(test_path)
        self.step = 100
        self.big_step = 600

        open = QtGui.QAction(QtGui.QIcon("art/open.png"), "Open Manga", self)
        open.setShortcut('Ctrl+O')
        open.setStatusTip('Choose a manga to read')
        self.connect(open, QtCore.SIGNAL('triggered()'), self.choose_manga)

        # toolbar = self.addToolBar('Manga')
        # toolbar.addAction(open)
        # toolbar.hide()

    def change_manga(self, path):
        # TODO managa a repo of mangas or something so that when we go back 
        # to another previous manga, we also restore the scroller object
        # or at least restore where the user was
        self.scroller = mscroll.MangaScroller(path)
        self.repaint()

    def choose_manga(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self, "Choose Manga", os.path.join(self.scroller.fetcher.root, '..'))
        if not dir: return
        self.change_manga(unicode(dir))

    def choose_chapter(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self, "Choose Chapter", self.scroller.fetcher.root)
        if not dir: return
        self.scroller.change_chapter(unicode(dir))

    def scrollDown(self, step):
        self.scroller.scroll_down(step)
    
    def scrollUp(self, step):
        self.scroller.scroll_up(step)

    def keyPressEvent(self, event):
        key = event.text()
        if key == 'j':
            self.scrollDown(self.step)
        if key == 'k':
            self.scrollUp(self.step)
        if key == 'J':
            self.scrollDown(self.big_step)
        if key == 'K':
            self.scrollUp(self.big_step)
        if key == 'q':
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
        mscroll.paint_scroller(painter, self.scroller)
        painter.end()


def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(1000, 800)
    window.setWindowTitle("Manga Reader")
    # window.setWindowIcon(QtGui.QIcon('art/icon.png'))
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
