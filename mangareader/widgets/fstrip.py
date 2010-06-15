"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    Film strip module.

    A film strip is a widget that displays images vertically
    
    A manga strip is an "infinite" list of images that can be scrolled up and down.
"""

from PyQt4 import QtGui, QtCore

def load_image(image_path, width=None):
    """Load a picture into a frame
       @param width: optional, if present, scale image width to match width
       @returns: a frame object
       @note: really, it returns a QImage, but we pretend it's not a qt object, but rather
       a frame object!!!
    """
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
        if y + frame_height > 0: # don't draw something that won't even be visible
            paint_frame(painter, frame, y)
        y += frame_height 
        frames = frames[1:]

