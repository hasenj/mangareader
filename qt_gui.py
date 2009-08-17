"""
    Author: Hasen il Judy
    License: GPL v2

    Qt based graphical user interface for the manga reader
"""

test_image = "/home/hasenj/manga/skipbeat17/01.png"
test_path = "/home/hasenj/manga/skipbeat17/"

import sys
from PyQt4 import QtGui, QtCore

class PictureWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.image = QtGui.QImage(test_image)
        self.y = 0
    
    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        padding = painter.viewport().width() - self.image.rect().width()
        x = int(padding/2)
        y = self.y
        painter.drawImage(QtCore.QPoint(x,y), self.image)
        painter.end()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_J:
            self.y -= 10
        if event.key() == QtCore.Qt.Key_K:
            self.y += 10
        if event.key() == QtCore.Qt.Key_Q:
            QtGui.QApplication.instance().quit()
        self.repaint()


def main():
    app = QtGui.QApplication(sys.argv)
    window = PictureWidget()
    window.resize(950, 550)
    window.setWindowTitle("Manga Reader")
    # window.setWindowIcon(QtGui.QIcon('art/icon.png'))
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
