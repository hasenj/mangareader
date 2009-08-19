"""
    Author: Hasen il Judy
    License: GPL v2

    Qt based graphical user interface for the manga reader
"""

test_image = "/home/hasenj/manga/skipbeat17/01.png"
test_path = "/home/hasenj/manga/skipbeat17/"

# system imports
import os
import sys
# Qt imports
from PyQt4 import QtGui, QtCore
# Project imports
import fstrip

def load_frames(path):
    for file in sorted(os.listdir(path)):
        _, ext = os.path.splitext(file)
        if ext in ['.png', '.jpg', '.jpeg']:
            image_path = os.path.join(path, file)
            yield fstrip.create_frame(image_path, 800)

class MangaWidget(fstrip.FilmStrip):
    def __init__(self, parent=None):
        fstrip.FilmStrip.__init__(self, parent)
        self.frames = list(load_frames(test_path))
        self.y = 0
        self.step = 100

    def scrollDown(self):
        self.y -= self.step
    
    def scrollUp(self):
        self.y += self.step

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_J:
            self.scrollDown()
        if event.key() == QtCore.Qt.Key_K:
            self.scrollUp()
        if event.key() == QtCore.Qt.Key_Q:
            QtGui.QApplication.instance().quit()
        self.repaint()


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
