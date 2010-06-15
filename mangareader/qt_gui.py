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

test_path = ''

# constants    
g_step = 30
g_big_step = 600

class MainWindow(QtGui.QWidget):
    def __init__(self, startdir):
        QtGui.QMainWindow.__init__(self, None)
        self.current_manga_path = startdir # for use in the open folder dialoge
        self.manga_frame = MangaFrame(startdir)

        vbox_container = QtGui.QVBoxLayout()
        vbox_container.addWidget(self.manga_frame)

        self.setLayout(vbox_container)

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
        if key == 'z':
            self.manga_frame.zoom_in(10)
        if key == 'x':
            self.manga_frame.zoom_out(10)
        if key == 'Z':
            self.manga_frame.reset_zoom()
        self.manga_frame.repaint()

    def mousePressEvent(self, event):
        btn = event.button()
        self.posMouseOrigin = event.pos()
        if btn == QtCore.Qt.LeftButton:
            self.funcMouseMove = self.mousePan
        elif btn == QtCore.Qt.RightButton:
            self.funcMouseMove = self.mouseZoom

    def mouseMoveEvent(self, event):
        delta = self.posMouseOrigin.y() - event.pos().y()
        self.funcMouseMove(delta)
        self.posMouseOrigin = event.pos()
        self.manga_frame.repaint()

    def wheelEvent(self, event):
        self.manga_frame.scrollDown(-event.delta())
        self.manga_frame.repaint()

    def mousePan(self, delta):
        self.manga_frame.scrollDown(delta)

    def mouseZoom(self, delta):
        self.manga_frame.zoom_out(delta)

import sys

def main():
    startdir = ''
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

