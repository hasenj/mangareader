"""
    Author: Hasen il Judy
    License: GPL v2

    Film strip module.

    A film strip is an "infinite" list of images that can be scrolled up and down.
"""

from PyQt4 import QtGui, QtCore

def create_frame(image_path):
    return QtGui.QImage(image_path)

def paint_frame(painter, frame, y):
    """Draw a single frame at vertical position `y` """
    padding = painter.viewport().width() - frame.rect().width()
    x = int(padding/2)
    painter.drawImage(QtCore.QPoint(x,y), frame)

def paint_frames(painter, frames, y):
    """Draw a list of frames starting at vertical position `y`"""
    while frames and y < painter.viewport().height():
        frame = frames[0]
        frame_height = frame.rect().height()
        if y + frame_height > 0: # don't draw something that won't be even visible
            paint_frame(painter, frame, y)
        y += frame_height 
        frames = frames[1:]

class FilmStrip(QtGui.QWidget):
    """A Film Strip is a widget that draw a list of pictures vertically"""
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.frames = []
        self.y = 0

    def setFrames(self, frames, y):
        self.frames = frames
        self.y = y
    
    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        paint_frames(painter, self.frames, self.y)
        painter.end()

