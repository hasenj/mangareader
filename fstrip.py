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
    while frames and y < painter.viewpoert().height():
        paint_frame(painter, frames[0], y)
        y += frames[0].rect().height()
        frames = frames[1:]

