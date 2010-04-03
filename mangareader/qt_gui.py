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

# widget imports
from mangareader.widgets import fstrip, mscroll
from widgets.manga_frame import MangaFrame

# XXX This should go away, right after we implement remembering manga location
if os.name == 'posix':
    test_path = "/home/hasenj/manga/sample/" # TEMP
elif os.name == 'nt':
    test_path = "C:\manga\sample\\" # TEMP

# constants    
g_step = 30
g_big_step = 600

class MainWindow(QtGui.QMainWindow):
    def __init__(self, startdir):
        QtGui.QMainWindow.__init__(self, None)
        self.current_manga_path = startdir
        self.manga_frame = MangaFrame(startdir)
        self.setCentralWidget(self.manga_frame)

    def choose_manga(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self, "Choose Manga", os.path.join(self.current_manga_path, '..'))
        if not dir: return
        path = unicode(dir)
        self.current_manga_path = path
        self.manga_frame.change_manga(path)

    def choose_chapter(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self, "Choose Chapter", self.current_manga_path)
        if not dir: return
        path = unicode(dir)
        self.manga_frame.change_chapter(path)

    def keyPressEvent(self, event):
        key = event.text()
        qt_key = event.key()
        if key == 'j' or qt_key == QtCore.Qt.Key_Down:
            self.manga_frame.scrollDown(g_step)
        if key == 'k' or qt_key == QtCore.Qt.Key_Up:
            self.manga_frame.scrollUp(g_step)
        if key == 'J' or qt_key == QtCore.Qt.Key_PageDown:
            self.manga_frame.scrollDown(g_big_step)
        if key == 'K' or qt_key == QtCore.Qt.Key_PageUp:
            self.manga_frame.scrollUp(g_big_step)
        if key == ' ':
            self.manga_frame.scrollDown(g_big_step)
        if key == 'q' or qt_key == QtCore.Qt.Key_Escape:
            QtGui.QApplication.instance().quit()
        if key == 'o':
            self.choose_manga()
        if key == 'i':
            self.choose_chapter()
        if key == ':':
            print "cmdbar TODO"
        self.manga_frame.repaint()

    def wheelEvent(self, event):
        self.manga_frame.scrollDown(-event.delta())
        self.manga_frame.repaint()


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

