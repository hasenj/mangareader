"""
    Author: Hasen il Judy
    License: GPL v2

    Qt based graphical user interface for the manga reader
"""

test_image = "/home/hasenj/manga/skipbeat17/01.png"
test_path = "/home/hasenj/manga/sample/"

# system imports
import os
import sys
# Qt imports
from PyQt4 import QtGui, QtCore
# Project imports
import fstrip
import mscroll

def load_frames(path):
    for file in sorted(os.listdir(path)):
        _, ext = os.path.splitext(file)
        if ext in ['.png', '.jpg', '.jpeg']:
            image_path = os.path.join(path, file)
            yield fstrip.create_frame(image_path, 800)

class MangaWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.scroller = mscroll.MangaScroller(test_path)
        self.step = 100
        self.big_step = 600

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
    window = MangaWidget()
    window.resize(1000, 800)
    window.setWindowTitle("Manga Reader")
    # window.setWindowIcon(QtGui.QIcon('art/icon.png'))
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
