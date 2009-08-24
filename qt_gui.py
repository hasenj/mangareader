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

    def scrollDown(self):
        self.scroller.scroll_down(self.step)
    
    def scrollUp(self):
        self.scroller.scroll_up(self.step)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_J:
            self.scrollDown()
        if event.key() == QtCore.Qt.Key_K:
            self.scrollUp()
        if event.key() == QtCore.Qt.Key_Q:
            QtGui.QApplication.instance().quit()
        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        mscroll.paint_scroller(painter, self.scroller)
        painter.end()


def main():
    app = QtGui.QApplication(sys.argv)
    window = MangaWidget()
    window.resize(950, 850)
    window.setWindowTitle("Manga Reader")
    # window.setWindowIcon(QtGui.QIcon('art/icon.png'))
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
